from annotation import *
import psycopg2
import json
import sqlparse
class Preprocessing:
    def __init__(self, host, port, database, username, password):

        # Connect to PostgresSQL database server
        self.connect = psycopg2.connect(host=host, port=port, database=database, user=username, password=password)

        # Create a cursor object
        self.cursor = self.connect.cursor()

    def parse_query(self, query='', scenario=''):

        # Parse Query
        self.query = ''
        self.query_plan = {}
        self.query = query
        if scenario != '':
            self.cursor.execute(scenario)
        self.cursor.execute("EXPLAIN (ANALYZE, FORMAT JSON) {}".format(self.query))
        query_plan = self.cursor.fetchall()
        self.query_plan = query_plan[0][0][0]['Plan']

        parse_query_plan = (json.dumps(self.query_plan, sort_keys=False, indent=4))
        return parse_query_plan

    def generate_plans(self, query=''):
        all_plans = []
        scenarios = []

        # Optimized query
        parsed_plan = self.parse_query(query, '')
        pretty_query = json.loads(parsed_plan)
        all_plans.append(pretty_query)

        # Iterate through all scenarios
        # Reference https://www.postgresql.org/docs/current/runtime-config-query.html#RUNTIME-CONFIG-QUERY-ENABLE 
        
        # some variables are ignored and not modified :
        #   enable_tidscan (boolean) is toggled as we assme no READ/WRITE operations
        #   enable_material (boolean) is not toggled as it is impossible to suppress materialization entirely 

        scenarios.append("set local enable_indexscan to 0")
        scenarios.append("set local enable_hashjoin to 0;set local enable_indexscan to 1")
        scenarios.append("set local enable_nestloop to 0;set local enable_hashjoin to 1")
        scenarios.append("set local enable_mergejoin to 0;set local enable_nestloop to 1")
        scenarios.append("set local enable_bitmapscan to 0;set local enable_mergejoin to 1")
        scenarios.append("set local enable_hashagg to 0;set local enable_bitmapscan to 1")
        scenarios.append("set local enable_seqscan to 0;set local enable_hashagg to 1")
        scenarios.append("set local enable_sort to 0;set local enable_seqscan to 1")
        scenarios.append("set local enable_tidscan to 0;set local enable_sort to 1")
        scenarios.append("set local enable_indexonlyscan to 0;set local enable_tidscan to 1")
        scenarios.append("set local enable_async_append to 0;set local enable_indexonlyscan to 1")
        scenarios.append("set local enable_gathermerge to 0;set local enable_async_append to 1")
        scenarios.append("set local enable_incremental_sort to 0;set local enable_gathermerge to 1")
        scenarios.append("set local enable_memoize to 0;set local enable_incremental_sort to 1")
        scenarios.append("set local enable_parallel_append to 0;set local enable_memoize to 1")
        scenarios.append("set local enable_parallel_hash to 0;set local enable_parallel_append to 1")
        scenarios.append("set local enable_partition_pruning to 0;set local enable_parallel_hash to 1")
        scenarios.append("set local enable_partitionwise_join to 0;set local enable_partition_pruning to 1")
        scenarios.append("set local enable_partitionwise_aggregate to 0;set local enable_partitionwise_join to 1")


        for i in range(len(scenarios)):
            parsed_plan = self.parse_query(query, scenarios[i])
            pretty_query = json.loads(parsed_plan)
            all_plans.append((pretty_query))

        return all_plans

    def process_query(self, query=''):
        # breaks down/parses SQL Query into different components for annotation
        # output is a list of strings
        # eg ["SELECT",  "X, Y" , "FROM",  "A, B"]
        final_parsed = []

        # capitalise all keywords
        # exhaustive list from https://www.bitdegree.org/learn/sql-commands-list 
        keywords = ['ALTER', 'TABLE', 'BETWEEN', 'DATABASE', 'TABLE', 'INDEX', 'CREATE', 'VIEW', 'DELETE','GRANT','REVOKE','COMMIT','ROLLBACK','SAVEPOINT','DROP','EXISTS','GROUP BY','IN','INSERT INTO','JOIN','OUTER','LEFT JOIN','RIGHT JOIN', 'FULL JOIN', 'LIKE','ORDER BY','SELECT', 'DISTINCT','INTO','TOP','UNION','ALL','TRUNCATE','UPDATE','WHERE']

        query_words = query.split(" ")

        for word in query_words:
            if not(all(c.isupper() or c.isspace() for c in word)) and word.upper() in keywords:
                #replace that word with the uppercase
                query = query.replace(word,word.upper())
                print('capitalised ' + word)
        query = query.replace("GROUP BY", "GROUPBY")
        query = query.replace("ORDER BY", "ORDERBY")
        query = query.replace("UNION ALL", "UNIONALL")
        query = query.replace("AND", "and")
        query = query.replace("OR", "or")
        query = query.replace("HAVING", "having")
        query = query.replace("IN", "in")
        query = query.replace("INNER JOIN", "INNERJOIN")
        query = query.replace("OUTER JOIN", "OUTERJOIN")
        query = query.replace("LEFT JOIN", "LEFTJOIN")
        query = query.replace("RIGHT JOIN", "RIGHTJOIN")
        query = query.replace("FULL JOIN", "FULLJOIN")
        query = query.replace("orDER", "ORDER")
        query = query.replace("DISTinCT", "DISTINCT")
        query = query.replace("inTERSECT", "INTERSECT")
        query = query.replace("Min", "MIN")

        query_words = query.split(" ") # do it again to get capitalised words


        # now all keywords are capitalised
        lastkeywordindex = -1
        stopindex = -1
        for i, word in enumerate(query_words):
            templist = []

            if i==0: continue # skip first keyword
            if all(c.isupper() or c.isspace() for c in str(word)) and len(word)>1: # if keyword
                # get all words before (but not including) that word into 1 string and append it to parsed list
                for j, word in enumerate(query_words):
                    if stopindex <= j and j < i: templist.append(str(word))
                stopindex = i
                final_parsed.append(' '.join(templist))
                lastkeywordindex = i

            # store last fragment
            if i==len(query_words)-1:
                for j, word in enumerate(query_words):
                    if lastkeywordindex <= j: templist.append(str(word))
                final_parsed.append(' '.join(templist))

        # for element in final_parsed:
        #     print(element)
        for i in range(len(final_parsed)):
            if 'GROUPBY' in final_parsed[i]:
                final_parsed[i] = final_parsed[i].replace("GROUPBY", "GROUP BY")
            elif 'ORDERBY' in final_parsed[i]:
                final_parsed[i] = final_parsed[i].replace("ORDERBY", "ORDER BY")
            elif 'UNIONALL' in final_parsed[i]:
                final_parsed[i] = final_parsed[i].replace("UNIONALL", "UNION ALL")
            elif 'INNERJOIN' in final_parsed[i]:
                final_parsed[i] = final_parsed[i].replace("INNERJOIN", "INNER JOIN")
            elif 'OUTERJOIN' in final_parsed[i]:
                final_parsed[i] = final_parsed[i].replace("OUTERJOIN", "OUTER JOIN")
            elif 'LEFTJOIN' in final_parsed[i]:
                final_parsed[i] = final_parsed[i].replace("LEFTJOIN", "LEFT JOIN")
            elif 'RIGHTJOIN' in final_parsed[i]:
                final_parsed[i] = final_parsed[i].replace("RIGHTJOIN", "RIGHT JOIN")
            elif 'FULLJOIN' in final_parsed[i]:
                final_parsed[i] = final_parsed[i].replace("FULLJOIN", "FULL JOIN")

        return final_parsed

    def match_nodes_to_query(self, query, tree_array):
        # takes in query, and processed qep and tries to match fragments of query to nodes of the json plan

        # output is a list of strings
        # eg ["SELECT X, Y" , "FROM A, B"]
        parsed = self.process_query(query=query)

        # get list of nodes generated by PostgreSQL
        nodes = []
        for node in tree_array:
            nodes.append(node.op_type)

        print(nodes) #['Limit', 'Aggregate', 'Gather Merge', 'Sort', 'Aggregate', 'Seq Scan']

        # Process parsed[] to group the different types

        # Keep track of counters
        aggregate_counter = 0
        group_counter = 0
        merge_counter = 0
        sort_counter = 0
        scan_counter = 0
        distinct_counter = 0
        append_counter = 0
        setop_counter = 0
        recursive_counter = 0
        materialize_counter = 0
        #----------------------------- MATCHING LIMIT -------------------------------
        # Match Limit to LIMIT clauses
        for i, node in enumerate(tree_array):
            if node.op_type == 'Limit':
                try:
                    possible_frags = [x for x in parsed if x.startswith('LIMIT')] #find the fragments involving LIMIT
                    node.query_frag = possible_frags[-1] #makes sense that the query should only have ONE limit clause. Hence this code takes the last/first/only element of the list
                except:
                    node.query_frag = ''

        #------------------------------ MATCHING AGGREGATE ------------------------
            elif node.op_type == 'Aggregate':
                # An aggregate function computes a single result from multiple input rows
                # AVG, COUNT, SUM, MAX, MIN
                # In general, can be mapped to the SELECT statements, WHERE clause must not have any aggregate statements
                # Aggregate can also be GROUP BY, as suggested by the "Group Key": ["l_returnflag", "l_linestatus"] in json
                # Aggregate in Postgresql is also for ORDER BY, and used together with the SELECT statement to sort table data
                # so in this case the 2 aggregates map to GROUP BY and ORDER BY

                # Seq Scan is to filter the WHERE clause
                try:
                    possible_frags = []
                    for x in parsed:
                        if 'AVG' in x.upper() or 'COUNT' in x.upper() or 'MAX' in x.upper() or 'MIN' in x.upper() or 'SUM' in x.upper():
                            possible_frags.append(x)

                    node.query_frag = possible_frags[aggregate_counter]
                    aggregate_counter += 1
                except:
                    node.query_frag = ''


            elif node.op_type == 'Group':
                try:
                    possible_frags = []
                    for x in parsed:
                        if 'GROUP BY' in x.upper():
                            possible_frags.append(x)

                    node.query_frag = possible_frags[group_counter]
                    group_counter += 1
                except:
                    node.query_frag = ''

        #------------------------------ MATCHING MERGE ------------------------
            elif 'Join' in node.op_type or 'Nested' in node.op_type or 'Hash' in node.op_type:
                try:
                    possible_frags = []
                    for x in parsed:
                        if 'JOIN' in x.upper():
                            possible_frags.append(x)

                    if len(possible_frags) != 0:
                        node.query_frag = possible_frags[merge_counter]
                        merge_counter += 1
                    else:
                        for x in parsed:
                            if 'WHERE' in x.upper():
                                node.query_frag = x
                except:
                    node.query_frag = ''

        # ------------------------------ MATCHING SORT ------------------------
            elif 'Sort' in node.op_type or 'Gather Merge' in node.op_type:
                try:
                    possible_frags = []
                    for x in parsed:
                        if 'ORDER BY' in x.upper():
                            possible_frags.append(x)

                    node.query_frag = possible_frags[sort_counter]
                    sort_counter += 1
                except:
                    node.query_frag = ''

        # ------------------------------ MATCHING SCANS ------------------------
            elif 'Scan' in node.op_type:
                try:
                    possible_frags = []
                    for x in parsed:
                        if 'FROM' in x.upper():
                            possible_frags.append(x)

                    node.query_frag = possible_frags[scan_counter]
                    scan_counter += 1
                except:
                    node.query_frag = ''

            # ------------------------------ MATCHING OTHERS ------------------------
            elif node.op_type == 'Unique':
                try:
                    possible_frags = []
                    for x in parsed:
                        if 'DISTINCT' in x.upper():
                            possible_frags.append(x)

                    node.query_frag = possible_frags[distinct_counter]
                    distinct_counter += 1
                except:
                    node.query_frag = ''


            elif node.op_type == 'Append':
                try:
                    possible_frags = []
                    for x in parsed:
                        if 'UNION ALL' in x.upper():
                            possible_frags.append(x)

                    node.query_frag = possible_frags[append_counter]
                    append_counter += 1
                except:
                    node.query_frag = ''

            elif node.op_type == 'SetOp' or node.op_type == 'Merge Append':
                try:
                    possible_frags = []
                    for x in parsed:
                        if x.upper().startswith('UNION') or x.upper().startswith('INTERSECT') or x.upper().startswith('EXCEPT'):
                            possible_frags.append(x)

                    node.query_frag = possible_frags[setop_counter]
                    setop_counter += 1
                except:
                    node.query_frag = ''


            elif node.op_type == 'Recursive Union':
                try:
                    possible_frags = []
                    for x in parsed:
                        if 'RECURSIVE' in x.upper():
                            possible_frags.append(x)

                    node.query_frag = possible_frags[recursive_counter]
                    recursive_counter += 1
                except:
                    node.query_frag = ''

            elif node.op_type == 'Materialize':
                try:
                    possible_frags = []
                    for x in parsed:
                        if 'MATERIALIZED' in x.upper():
                            possible_frags.append(x)

                    node.query_frag = possible_frags[materialize_counter]
                    materialize_counter += 1
                except:
                    node.query_frag = ''

            else:
                node.query_frag = ''

        # Need to loop through again and take care of those with empty
        for i, node in enumerate(tree_array):
            if 'Scan' in node.op_type and node.query_frag == '':
                try:
                    for x in parsed:
                        if 'FROM' in x.upper():
                            node.query_frag = x

                except:
                    node.query_frag = ''


            elif 'Sort' in node.op_type or 'Gather Merge' in node.op_type and node.query_frag == '':
                try:
                    for x in parsed:
                        if 'ORDER BY' in x.upper():
                            node.query_frag = x

                except:
                    node.query_frag = ''

            elif 'Aggregate' in node.op_type or 'Group' in node.op_type and node.query_frag == '':
                try:
                    for x in parsed:
                        if 'GROUP BY' in x.upper():
                            node.query_frag = x
                    if node.query_frag == '':
                        for x in parsed:
                            if 'SELECT' in x.upper():
                                node.query_frag = x

                except:
                    node.query_frag = ''

            elif 'Join' in node.op_type or 'Nested' in node.op_type or 'Hash' in node.op_type and node.query_frag == '':
                try:
                    for x in parsed:
                        if 'WHERE' in x.upper():
                            node.query_frag = x

                except:
                    node.query_frag = ''

            elif 'Unique' in node.op_type and node.query_frag == '':
                try:
                    for x in parsed:
                        if 'DISTINCT' in x.upper():
                            node.query_frag = x

                except:
                    node.query_frag = ''

            elif 'Append' in node.op_type or 'SetOp' in node.op_type or 'Merge Append' in node.op_type and node.query_frag == '':
                try:
                    for x in parsed:
                        if 'UNION' in x.upper() or 'INTERSECT' in x.upper() or 'EXCEPT' in x.upper():
                            node.query_frag = x

                except:
                    node.query_frag = ''

        for i, node in enumerate(tree_array):
            if node.query_frag == '':
                node.query_frag = parsed[0]



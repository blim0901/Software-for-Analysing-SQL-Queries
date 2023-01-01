import json
import tkinter as tk
import Pmw

BOX_W = 150
BOX_H = 80
overall_nodes = []
visual_to_node = {}

final_costs_array = []

class Node:
    def __init__(self, x1, y1, x2, y2, op_type, annotation_text, query_frag, cost):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        
        self.center = ((x1 + x2) / 2, (y1 + y2) / 2)
        self.pointers = []
        self.op_type = op_type
        self.annotation_text = annotation_text
        self.query_frag = query_frag
        self.cost = cost

    def add_pointer(self, pointer):
        self.pointers.append(pointer)


def build_tree(cursor_node, parsed_plan):
    plan = parsed_plan
    cursor_node.op_type = plan["Node Type"]
    cursor_node.cost = plan["Total Cost"]

    cursor_node.annotation_text = create_annotation(plan)

    overall_nodes.append(cursor_node)

    if "Plans" in plan:
        if len(plan["Plans"]) == 1:
            x1 = cursor_node.x1
            y1 = cursor_node.y2 + BOX_H / 4
            x2 = cursor_node.x2
            y2 = y1 + BOX_H

            pointer_node = Node(x1, y1, x2, y2, "", "", "", 0)
            cursor_node.add_pointer(pointer_node)
            build_tree(pointer_node, plan["Plans"][0])

        elif len(plan["Plans"]) == 2:
            for i in range(2):
                x2 = cursor_node.x1 - BOX_W / 4 + i * (2 * BOX_W)
                y1 = cursor_node.y2 + BOX_H / 4
                x1 = x2 - BOX_W
                y2 = y1 + BOX_H

                pointer_node = Node(x1, y1, x2, y2, "", "", "", 0)
                cursor_node.add_pointer(pointer_node)
                build_tree(pointer_node, plan["Plans"][i])

    print(len(overall_nodes))
    print(overall_nodes)
    return overall_nodes


def calculate_costs(generated_plans):

    for i in range(len(generated_plans)):
        root_node = Node(0, 0, 0, 0, "", "", "", 0)
        temp_plan = build_tree(root_node, generated_plans[i])
        cost_of_plan = 0
        for node in temp_plan:
            cost_of_plan = cost_of_plan + float(node.cost)
        final_costs_array.append(round(cost_of_plan, 2))

    return final_costs_array

def add_comparison_values(tree_array):
    op_of_interest = ['Nested Loop', 'Hash Join', 'Merge Join', 'Seq Scan', 'Index Scan', 'Index Only Scan', 'Bitmap Heap Scan', 'Tid Scan', 'Sort', 'Gather Merge', 'Incremental Sort', 'Memoize']
    for node in tree_array:
        if node.op_type in op_of_interest:
            node.annotation_text = node.annotation_text + '\nThis operation is chosen as it is ' + str(cal_X(node.op_type,get_scenarios())) + ' times faster than if ' + node.op_type + ' is not used when processing the query.'

    return tree_array

def get_scenarios():
    scenarios = []
    scenarios.append('Optimised query')
    scenarios.append('Index scan disabled')
    scenarios.append('Hash join disabled')
    scenarios.append('Nested loop disabled')
    scenarios.append('Merge join disabled')
    scenarios.append('Bitmap heap scan disabled')
    scenarios.append('Hash agg disabled')
    scenarios.append('Seq scan disabled')
    scenarios.append('Sort disabled')
    scenarios.append('Tid scan disabled')
    scenarios.append('Index only scan disabled')
    scenarios.append('Async append disabled')
    scenarios.append('Gather merge disabled')
    scenarios.append('Incremental sort disabled')
    scenarios.append('Memoize disabled')
    scenarios.append('Parallel append disabled')
    scenarios.append('Parallel hash disabled')
    scenarios.append('Partition pruning disabled')
    scenarios.append('Partition wise join disabled')
    scenarios.append('Partition wise aggregate disabled')
    return scenarios

def cal_X(node_op_type, scenarios):
    # calculate how many times the plan w this algo is better than the one without
    index = -1

    # find index i of which scenario this corresponds to
    for i, scenario_str in enumerate(scenarios):
        if node_op_type.lower() in scenario_str.lower():
            index = i #index found
            break # exit for loop


    qep_cost = final_costs_array[0]
    aqp_cost = final_costs_array[index]

    # aqp cost should be more than qep, thats why qep is chosen
    x = aqp_cost / qep_cost
    #print(x)
    #truncate to 2dp

    return round(x, 2)


def create_annotation(plan):
    # creates annotations based on the different nodes of the plans returned by Postgres
    # split into different types
    # with reference to the exhaustive list of different node types
    # https://github.com/postgres/postgres/blob/master/src/backend/commands/explain.c#L814
    # line 1192 onwards

    annotation_text=""
    node_op_type = str(plan['Node Type'])
    duration = "\nDuration: %.2f ms" % (plan['Actual Total Time'] - plan['Actual Startup Time'])
    cost = "\nCost: %.2f" % plan['Total Cost']

    #------------------------------JOINS-------------------------------
    # Joins considered:
    # Nested Loop
    # Hash Join
    # Merge Join
    
    if node_op_type == 'Nested Loop':
        annotation_text = 'This join is executed using ' + node_op_type + ' Algorithm with ' +  str(plan['Join Type']) + ' join type. ' + node_op_type + ' is chosen.'

    elif node_op_type == 'Hash Join':
        annotation_text = 'This join is executed using ' + node_op_type + ' Algorithm with ' + str(plan['Join Type']) + ' join type ' + ' with hash condition '+ str(plan['Hash Cond'])  + ' ' +  node_op_type + ' is chosen.'

    elif node_op_type == 'Merge Join':
        annotation_text = 'Execute ' + node_op_type + ' using ' + str(plan['Join Type']) + ' join type ' + ' with merge condition ' + str(plan['Merge Cond']) + ' ' + node_op_type + ' is chosen.'

    #----------------------------SCANS---------------------------------
    # Scans Considered:
    # Seq Scan
    # Index Scan
    # Sample Scan
    # Index Only Scan
    # Bitmap Heap Scan
    # Foreign Scan: --> case CMD_SELECT:
					#pname = "Foreign Scan";
					#operation = "Select";
                    # ignore cases of CMD_INSERT, CMD_UPDATE, CMD_DELETE
    # Custom Scan:
    # Subquery Scan
    # Tid Scan
    # Tid Range Scan
    # Function Scan
    # Table Function Scan
    # Values Scan
    # Named Tuplestore Scan
    elif node_op_type == 'Named Tuplestore Scan':
        annotation_text = 'Data are read using the ' + node_op_type + ' algorithm. '
    # CTE Scan
    elif node_op_type == 'CTE Scan':
        annotation_text = 'Data are read using the ' + node_op_type + ' algorithm. It is chosen here as can cause the operations in the subquery to be evaluated, and the results stored to be used later in the query.'
    # WorkTable Scan
    elif node_op_type == 'WorkTable Scan':
        annotation_text = 'Data are read using the ' + node_op_type + ' algorithm. This is chosen as it needs to perform logical operations that needs to be stored in a a worktable. Worktables are built in tempdb and are dropped automatically when they are no longer needed.'

    elif node_op_type == 'Seq Scan':
        try:
            annotation_text = 'Tables are read using the Sequential Scan algorithm. It is executed on the relation ' + str(plan['Relation Name']) + '. This is because no index is available to be used to parse the relation.'
        except:
            annotation_text = 'Tables are read using the Sequential Scan algorithm. This is because no index is available to be used to parse the relation.'

    elif node_op_type == 'Index Scan':
        try:
            annotation_text = 'Tables are read using the Index Scan algorithm. This is because there exists an index ' + str(plan['Index Name']) + ' on the relation ' + str(plan['Relation Name'])+ '. As indexes drastically reduces the lookup and processing time for scanning a table, Index Scan is thus chosen over other Scans such as Sequential Scan.'
        except:
            annotation_text = 'Tables are read using the Index Scan algorithm. As indexes drastically reduces the lookup and processing time for scanning a table, Index Scan is thus chosen over other Scans such as Sequential Scan.'

    elif node_op_type == 'Sample Scan':
        try:
            annotation_text = 'Data are read using Sample Scan. It is executed on the relation ' + str(plan['Relation Name']) + 'and retrieves a random sample of data.'
        except:
            annotation_text = 'Data are read using Sample Scan.'
    
    elif node_op_type == 'Index Only Scan':
        # When all the information needed is contained in the index, an index-only scan can read all the data from it, without referring to the table.
        try:
            annotation_text = 'Data are read using Index Only Scan. This is because all the information is contained in the index ' + str(plan['Index Name']) + ' which the row can be checked with the number of heap fetches (' + str(plan['Heap Fetches']) + ').'
        except:
            annotation_text = 'Data are read using Index Only Scan. This is because all the information is contained in the index.'

    elif node_op_type == 'Bitmap Heap Scan':
        # Reads pages from a bitmap created by the other operations, filtering out any rows that don't match the condition.
        try:
            annotation_text = 'Pages are read using Bitmap Heap Scan. It reads pages from a bitmap and filter rows out with the condition ' + str(plan['Recheck Cond']) + '. It is required when the bitmap scan is lossy which contains ' + str(plan['Lossy Heap Blocks']) + ' of lossy blocks a bitmap heap scan visited. ' + str(plan['Rows Removed by Index Recheck']) + ' rows returned that do not meet the condition are removed.'
        except:
            annotation_text = 'Pages are read using Bitmap Heap Scan. It reads pages from a bitmap and filter rows out.'

    elif node_op_type == 'Foreign Scan':
        # Reads data from a remote data source.
        try:
            annotation_text = 'External data are read using Foreign Scan. It executes the ' + str(plan['Operation']) + ' operation with the foreign tables stored in ' + str(plan['Remote SQL']) + ' server.'
        except:
            annotation_text = 'External data are read using Foreign Scan.'

    elif node_op_type == 'Custom Scan':
        # Postgres allows extensions to add new custom scan types to extend the ways in which it can read data.
        try:
            annotation_text = 'Data can be read using Custom Scan through a scan provider (' + str(plan['Custom Plan Provider']) + ') to allow the use of some optimization not supported by the core system.'
        except:
            annotation_text = 'Data can be read using Custom Scan through a scan provider.'

    elif node_op_type == 'Subquery Scan':
        # Read the results of a subquery.
        try:
            annotation_text = 'Results are read based on the subquery using Subquery Scan. The subquery is evaluated to determine whether it returns any rows based on the ' + str(plan['Rows Removed by Filter']) + ' rows removed by filter.'
        except:
            annotation_text = 'Results are read based on the subquery using Subquery Scan. The subquery is evaluated to determine whether it returns any rows based on a filter.'

    elif node_op_type == 'Tid Scan':
        # A scan of a table by TupleID (or ctid).
        try:
            annotation_text = 'Tuples are read through scanning the table by TupleID using Tid Scan. It retrieves the corresponding tuple with the condition of ' + str(plan['Tid Cond']) + '.'
        except:
            annotation_text = 'Tuples are read through scanning the table by TupleID using Tid Scan. It retrieves the corresponding tuple with a condition.'

    elif node_op_type == 'Tid Range Scan':
        # A scan ranges of TupleID.
        try:
            annotation_text = 'Tuples are read through scanning the table by TupleID using Tid Range Scan. It retrieves the corresponding tuple with the range condition of ' + str(plan['Tid Cond']) + '.'
        except:
            annotation_text = 'Tuples are read through scanning the table by TupleID using Tid Range Scan. It retrieves the corresponding tuple with a range condition.'

    elif node_op_type == 'Function Scan':
        # Take the results of a set-returning function, and return them as if they were rows read from a table.
        try:
            annotation_text = 'The results of ' + str(plan['Function Name']) + ' function are read using Function Scan given the function call of ' + str(plan['Function Call']) + '.'
        except:
            annotation_text = 'The results are read using Function Scan given a function call.'

    elif node_op_type == 'Table Function Scan':
        try:
            annotation_text = 'Tables are read with the results of ' + str(plan['Function Name']) + ' function using Table Function Scan.'
        except:
            annotation_text = 'Tables are read using Table Function Scan.'

    elif node_op_type == 'Values Scan':
        # Read in constants as part of a VALUES command.
        annotation_text = 'Constants are read as part of a VALUES command.'


    #------------------------------HASH--------------------------
    elif node_op_type == 'Hash':
        annotation_text = 'Execute ' + node_op_type

    #----------------------------OTHERS-------------------------
    # Other Operator Types Considered:
    # ModifyTable --> got Merge, we ignore CMD_INSERT, CMD_UPDATE, CMD_DELETE
    elif node_op_type == 'ModifyTable':
        try:
            annotation_text = 'Execute write or delete using the ModifyTable algorithm. It is executed on the relation ' + str(plan['Relation Name']) + '. The number of write-ahead logging records generated by the operation is ' + str(plan['WAL Records'])
        except:
            annotation_text = 'Execute write or delete using the ModifyTable algorithm.'
    # Append: --> we only consider pname = operation = "Merge", ignore CMD_INSERT, CMD_UPDATE, CMD_DELETE
    elif node_op_type == 'Append':
        try:
            annotation_text = 'Child operations are combined using the ' + node_op_type + ' algorithm. The number of subplans removed is ' + str(plan['Subplans Removed']) + '. This can be the result of an explicit UNION ALL statement, or the need for a parent operation to consume the results of two or more children together.'
        except:
            annotation_text = 'Child operations are combined using the ' + node_op_type + ' algorithm.'
    # Merge Append
    elif node_op_type == 'Merge Append':
        try:
            annotation_text = 'The sorted results of the child operations are combined using the ' + node_op_type + ' algorithm in a way that preserves the order. It is chosen as it can combine already-sorted rows from table partitions. This is done using the sort key ' + str(plan['Sort Key'])
        except:
            annotation_text = 'The sorted results of the child operations are combined using the ' + node_op_type + ' algorithm in a way that preserves the order.'
    # Recursive Union
    elif node_op_type == 'Recursive Union':
        annotation_text = 'The steps of a recursive function are union together using the ' + node_op_type + ' algorithm. '
    # BitmapAnd
    elif node_op_type == 'BitmapAnd':
        annotation_text = 'The index are combined using the ' + node_op_type + ' algorithm. This is used as it is needed in a multi step process for the bitmap scan. This operation is needed to that the information from multiple index can be aggregated together.'
    # BitmapOr
    elif node_op_type == 'BitmapOr':
        annotation_text = 'The index are combined using the ' + node_op_type + ' algorithm. This is used as it is needed in a multi step process for the bitmap scan. This operation is needed to that the information from multiple index can be aggregated together.'
    # Gather
    elif node_op_type == 'Gather':
        annotation_text = 'Child nodes are combined using the ' + node_op_type + ' algorithm. This is used as the sort order does not matter. And there can be time savings using  parallel workers for execution. '
    # Gather Merge
    # Sort
    # Limit
    # Incremental Sort
    # Memoize
    # Materialize
    # Group
    # T_Agg --> several cases: Aggregate(Plain), Group Aggregate (sorted), Hash Aggregate (Hashed), Mixed Aggregate (Mixed)
    # WindowAgg
    # Unique
    # SetOp --> several cases: SetOp(Sorted), HashSetOp(Hashed)
    # LockRows
    # ProjectSet
    # Result

    elif node_op_type == 'Limit':
        annotation_text = 'Execute ' + node_op_type

    elif node_op_type == 'Sort':
        try:
            annotation_text = 'Execute ' + node_op_type + ' using ' + str(plan['Sort Method']) + ' on the attributes ' + str(plan['Sort Key']) + '.'
        except:
            annotation_text = 'Execute ' + node_op_type


    elif node_op_type == 'Gather Merge':
        annotation_text = 'Execute ' + node_op_type + '.'

    elif node_op_type == 'Incremental Sort':
        # Incremental Sort sorts the data by one column at a time
        # Can save a lot of time, and memory, when the rows are already sorted by one (or more) of the required columns already
        try:
            annotation_text = 'Execute Incremental Sort on the database on ' + str(plan['Sort Key']) + ' attributes as the Sort Keys. Specifically the '+ str(plan['Sort Method']) + ' method is used to sort the columns. The sort ran for ' + str(plan['Actual Loops'])+ ' number of loops. This method is preferred as the database is already pre-sorted on ' + str(plan['Presorted Key']) + ' and is thus faster.'
        except:
            annotation_text = 'Execute Incremental Sort on the database using attributes as the Sort Keys.'

    elif node_op_type == 'Memoize':
        # memoize plans for caching results from parameterized scans inside nested-loop joins
        annotation_text = 'This query is Memoized. As scans to the underlying plans are skipped when the results for the current parameters are already in the cache.'


    elif node_op_type == 'Materialize':
        # Stores the result of the child operation in memory, to allow fast, repeated access to it by parent operations.
        annotation_text = 'This part of the query is stored in memory. By storing the result of the child operation in memory, this facilitates fast, repeated access to it by parent operations.'

    elif node_op_type == 'Group':
        # GROUP BY clauses
        try:
            annotation_text = 'This GROUPBY on ' + str(plan['Group Keys']) + ' is implemented using the ' + str(plan['Strategy']) +  'Strategy.'
            if 'Hash Key' in plan:
                annotation_text += 'The Hashing is done on attribute ' + str(plan['Hash Key'])
            if 'Group Key' in plan:
                annotation_text += 'The grouping is done on the attributes ' + str(plan['Group Key'])
        except:
            annotation_text = 'Execute group using a key'
    
    elif node_op_type == 'Aggregate':
        # Combines rows together to produce result(s).
        # Can be a combination of GROUP BY, UNION or SELECT DISTINCT clauses, and/or functions like COUNT, MAX or SUM.
        try:
            annotation_text = 'Execute ' + node_op_type + ' operation with '
            if 'Filter' in plan:
                annotation_text += 'filter on ' + str(plan['Filter'])
            if 'Group Key' in plan:
                annotation_text += 'grouping on the attributes ' + str(plan['Group Key'])
            if 'Hash Key' in plan:
                annotation_text += 'hashing on attribute ' + str(plan['Hash Key']) + '.'
        except:
            annotation_text = 'Execute ' + node_op_type

    elif node_op_type == 'WindowAgg':
        # WindowAgg nodes represent window functions, which are caused by OVER statements.
        annotation_text = 'This OVER statement is processed by window functions.'

    elif node_op_type == 'Unique':
        # Removes duplicates from a sorted result set.
        annotation_text = 'Duplicates are removed from a sorted result set.'

    elif node_op_type == 'SetOp':
        # A set operation like INTERSECT or EXCEPT.
        # UNION operations are handled by Append or MergeAppend.
        try:
            annotation_text = 'This set operation of ' + str(plan['Command']) + ' is done by ' + str(plan['Strategy']) + ' strategy.'
        except:
            annotation_text = 'This is a set operation.'

    elif node_op_type == 'LockRows':
        # Lock the rows in question to block other queries from writing to them (reads are allowed).
        try:
            annotation_text = 'This operation has blocked other queries from accessing specific rows ' + str(plan['Output'])
        except:
            annotation_text = 'This operation has blocked other queries from accessing specific rows.'

    elif node_op_type == 'ProjectSet':
        # Executes set-returning functions.
        annotation_text = 'Executes set-returning functions.'

    elif node_op_type == 'Result':
        # Result nodes return a value without a scan (like a hardcoded value).
        annotation_text = 'This is a result which was returned without a scan.'

    annotation_text += cost
    annotation_text += duration

    print("annotation text: ")
    print(annotation_text)
    return annotation_text


def tree2json(tree_array):
    tree_output = []
    for node in tree_array:
        single_node = {}
        single_node["x1"] = node.x1
        single_node["y1"] = node.y1
        single_node["x2"] = node.x2
        single_node["y2"] = node.y2
        single_node["op_type"] = node.op_type
        single_node["annotation_text"] = node.annotation_text
        single_node["center"] = node.center

        tree_output.append(single_node)

    return tree_output

# Software-for-Analysing-SQL-Queries
Real-world users may write SQL queries to search relational databases for different tasks. The RDBMS query optimizer will execute a query execution plan (QEP) to process each query, which is chosen from a large number of alternative query plans (AQP). Typically, the plan selected as the QEP is estimated to have least/lower cost than other AQP. However, an SQL query and its query plan-related information are disconnected. In this project, the broad goal is to integrate them by retrieving relevant information from a QEP and AQP to annotate the corresponding SQL query to explain how different components of the query are executed by the underlying query processor and why the operators are chosen among other alternatives. Part of the project also involves creating a TPC-H database in PostgreSQL. 



## Instructions
### Install Dependencies
- Ensure that Python is installed
You will need to run these commands to install dependencies before running `project.py`:
```
python -m pip install psycopg2
python -m pip install tk
python -m pip install PySimpleGUI
python -m pip install sqlparse
python -m pip install Pmw
```
### Program Execution
- Ensure you have the above dependencies installed
- Go into the project directory containing the `project.py` file. In this case, it is the `/project2` folder.
Run these commands to execute the `project.py` program:
```
python project.py
```


## Sample Queries
Here are some samples queries for you to test out our software's functionality

1. SELECT l_returnflag, l_linestatus, sum(l_quantity) as sum_qty, sum(l_extendedprice) as sum_base_price, sum(l_extendedprice * (1 - l_discount)) as sum_disc_price, sum(l_extendedprice * (1 - l_discount) * (1 + l_tax)) as sum_charge, avg(l_quantity) as avg_qty, avg(l_extendedprice) as avg_price, avg(l_discount) as avg_disc, count(*) as count_order FROM lineitem WHERE l_shipdate <= date '1998-12-01' - interval '90' day GROUP BY l_returnflag, l_linestatus ORDER BY l_returnflag, l_linestatus;
2. SELECT l_orderkey, sum(l_extendedprice * (1 - l_discount)) as revenue, o_orderdate, o_shippriority FROM customer, orders, lineitem WHERE c_mktsegment = 'BUILDING' AND c_custkey = o_custkey AND l_orderkey = o_orderkey AND o_orderdate < date '1995-03-15' AND l_shipdate > date '1995-03-15' GROUP BY l_orderkey, o_orderdate, o_shippriority ORDER BY revenue desc, o_orderdate LIMIT 20;
3. SELECT n_name, sum(l_extendedprice * (1 - l_discount)) as revenue FROM customer, orders, lineitem, supplier, nation, region WHERE c_custkey = o_custkey AND l_orderkey = o_orderkey AND l_suppkey = s_suppkey AND c_nationkey = s_nationkey AND s_nationkey = n_nationkey AND n_regionkey = r_regionkey AND r_name = 'ASIA' AND o_orderdate >= date '1994-01-01' AND o_orderdate < date '1994-01-01' + interval '1' year GROUP BY n_name ORDER BY revenue desc;
4. SELECT sum(l_extendedprice * l_discount) as revenue FROM lineitem WHERE l_shipdate >= date '1994-01-01' AND l_shipdate < date '1994-01-01' + interval '1' year AND l_discount between 0.06 - 0.01 AND 0.06 + 0.01 AND l_quantity < 24;
5. SELECT l_shipmode, sum(case when o_orderpriority = '1-URGENT' OR o_orderpriority = '2-HIGH' then 1 else 0 end) as high_line_count, sum(case when o_orderpriority <> '1-URGENT' AND o_orderpriority <> '2-HIGH' then 1 else 0 end) AS low_line_count FROM orders, lineitem WHERE o_orderkey = l_orderkey AND l_shipmode in ('MAIL', 'SHIP') AND l_commitdate < l_receiptdate AND l_shipdate < l_commitdate AND l_receiptdate >= date '1994-01-01' AND l_receiptdate < date '1994-01-01' + interval '1' year GROUP BY l_shipmode ORDER BY l_shipmode;
6. SELECT 100.00 * sum(case when p_type like 'PROMO%' then l_extendedprice * (1 - l_discount) else 0 end) / sum(l_extendedprice * (1 - l_discount)) as promo_revenue FROM lineitem, part WHERE l_partkey = p_partkey AND l_shipdate >= date '1995-09-01' AND l_shipdate < date '1995-09-01' + interval '1' month;

Samples queries are taken from this source: https://examples.citusdata.com/tpch_queries.html

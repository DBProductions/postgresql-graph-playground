import argparse
import psycopg2
import psycopg2.extras
from tabulate import tabulate

conn = psycopg2.connect(database='postgres',
                        host='127.0.0.1',
                        user='postgres',
                        password='postgres',
                        port='5432')

cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

parser = argparse.ArgumentParser('sql_queries')
parser.add_argument('node', help='node id to query', nargs='?', type=int, default=11)
args = parser.parse_args()
node_to_query = args.node

def print_table(sql):
    cursor.execute(sql)
    result = cursor.fetchall()
    print(tabulate(result, headers={}, tablefmt='grid'))  

current_node_sql = f"""SELECT nodes.* FROM nodes WHERE id = {node_to_query};"""

outgoing_sql = f"""
SELECT nodes.*
  FROM nodes
JOIN edges ON nodes.id = edges.next_node
  WHERE edges.previous_node = {node_to_query};
"""

outgoing_outgoing_sql = f"""
SELECT DISTINCT e2.next_node, *
  FROM edges AS e1 
JOIN edges AS e2 ON e1.next_node = e2.previous_node 
  WHERE  
    e1.previous_node = {node_to_query} AND 
    e1.next_node <> {node_to_query} AND 
    e2.next_node <> {node_to_query};
"""

union_sql = f"""
SELECT DISTINCT nodes.id, 1 AS depth
  FROM nodes 
JOIN edges ON nodes.id = edges.next_node AND edges.previous_node = {node_to_query} 
UNION
SELECT DISTINCT e2.next_node, 2 AS depth
  FROM edges AS e1 
JOIN edges AS e2 ON e1.next_node = e2.previous_node 
  WHERE 
    e1.previous_node = {node_to_query} AND 
    e1.next_node <> {node_to_query} AND 
    e2.next_node <> {node_to_query};
"""

recursive_sql = f"""
WITH RECURSIVE likes AS (
  SELECT
    next_node AS id,
    1 AS depth,
    ARRAY[previous_node] AS path
  FROM edges
    WHERE previous_node = {node_to_query} AND label = 'LIKES'
  UNION ALL
  SELECT
    edges.next_node,
    likes.depth + 1,
    likes.path || edges.previous_node
  FROM likes
    JOIN edges ON edges.previous_node = likes.id
    WHERE NOT edges.next_node = ANY(likes.path) AND edges.label = 'LIKES'
)
SELECT id, depth, path || id AS path
FROM likes
WHERE depth <= 1;
"""

print('\n --- current node')
print_table(current_node_sql)
print('\n --- outgoing results')
print_table(outgoing_sql)
print('\n --- depth outgoing results')
print_table(outgoing_outgoing_sql)
print('\n --- union results')
print_table(union_sql)
print('\n --- recursive results')
print_table(recursive_sql)
import argparse
import requests
from datetime import datetime, timedelta
from random import sample, choices

parser = argparse.ArgumentParser('generate_sql')
parser.add_argument('nodes', help='Amount of nodes to create', nargs='?', type=int, default=500)
args = parser.parse_args()

nodes = args.nodes
url = f'https://randomuser.me/api/?gender=male&nat=gb&inc=email,name&results={nodes}'
response = requests.get(url)
json_data = response.json()

sql_file = open('./initdb/init.sql', 'w')

# products
products = []
for p in range(10):
    products.append(f'Product {p + 1}')

# prepare dates in a range
numdays = 100
base = datetime.today()
res_dates = [base - timedelta(days=x) for x in range(numdays)]

create_tables = """
CREATE TABLE nodes (
  id SERIAL PRIMARY KEY,
  label VARCHAR(255) NOT NULL,
  props jsonb not null default '{}'::jsonb
);

CREATE INDEX nodes_id ON nodes (id);
CREATE INDEX nodes_label ON nodes (label);

CREATE TABLE edges (
  previous_node INTEGER REFERENCES nodes(id),
  next_node INTEGER REFERENCES nodes(id),
  label VARCHAR(255) NOT NULL,
  props jsonb not null default '{}'::jsonb,
  CHECK (previous_node != next_node)
);

CREATE INDEX edges_label ON edges (label);
CREATE INDEX edges_next_node ON edges (next_node);
\n"""

sql_file.write(create_tables)
sql_file.write('-- products\n')
for product in products:
    s = ('INSERT INTO nodes (label, props) VALUES '
         f'(\'Product\', \'{{"name": "{product}"}}\')'
         ';\n')
    sql_file.write(s)

sql_file.write('\n')

sql_file.write('-- random user\n')
for result in json_data['results']:
    res = choices(res_dates)
    ts = round(res[0].timestamp())
    name = result['name']['first'] + ' ' + result['name']['last']
    s = ('INSERT INTO nodes (label, props) VALUES '
         f'(\'User\', \'{{"name": "{name}", "email": "{result['email']}", "created": {str(ts)}}}\')'
         ';\n')
    sql_file.write(s)

sql_file.write('\n')

sql_file.write('-- edges for first user\n')
random_list = sample(range(12, nodes), 15)
for i in random_list:
    res = choices(res_dates)
    ts = round(res[0].timestamp())
    s = ('INSERT INTO edges (previous_node, next_node, label, props) VALUES '
         f'(11, {i}, \'LIKES\', \'{{"since": {ts}}}\')'
        ';\n')
    sql_file.write(s)

sql_file.write('\n')

sql_file.write('-- edges for second user\n')
random_list = sample(range(13, nodes), 10)
for i in random_list:
    res = choices(res_dates)
    ts = round(res[0].timestamp())
    s = ('INSERT INTO edges (previous_node, next_node, label, props) VALUES '
         f'(12, {i}, \'LIKES\', \'{{"since": {ts}}}\')'
        ';\n')
    sql_file.write(s)

sql_file.write('\n')

sql_file.write('-- random edges for user\n')
r = sample(range(11, nodes), nodes - 11)
for i in range(11, round(nodes/4)):
    _r = choices(r)
    while i == _r[0]:
        _r = choices(r)
    res = choices(res_dates)
    ts = round(res[0].timestamp())
    s = ('INSERT INTO edges (previous_node, next_node, label, props) VALUES '
         f'({i}, {_r[0]}, \'LIKES\', \'{{"since": {ts}}}\')'
        ';\n')
    sql_file.write(s)

sql_file.write('\n')

sql_file.write('-- user product relationships\n')
user_product_relationships = ['CONTRIBUTES', 'USES']
for i in range(nodes):
    product = choices(products)
    label = choices(user_product_relationships)[0]
    if label == 'CONTRIBUTES':
        previous = i + 11
        next = product[0].split(' ')[1]
    elif label == 'USES':
        previous = product[0].split(' ')[1]
        next = i + 11
    s = ('INSERT INTO edges (previous_node, next_node, label, props) VALUES '
        f'({previous}, {next}, \'{label}\', \'{{"since": {ts}}}\')'
        ';\n')
    sql_file.write(s)

sql_file.close()
print('SQL file created')
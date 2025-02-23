import random
import argparse
import requests
from datetime import date, datetime, timedelta
from random import choices

parser = argparse.ArgumentParser('generate_sql')
parser.add_argument('nodes', help='Amount of nodes to create', nargs='?', type=int, default=500)
args = parser.parse_args()

nodes = args.nodes
url = f'https://randomuser.me/api/?gender=male&nat=gb&inc=email,name&results={nodes}'
response = requests.get(url)
json_data = response.json()

# prepare dates in a range
test_date1, test_date2 = datetime(2024, 5, 3, 22, 30, 0), datetime(2025, 2, 1, 22, 30, 0)
res_dates = [test_date1]
# loop to get each date till end date
while test_date1 != test_date2:
    test_date1 += timedelta(days=1)
    res_dates.append(test_date1)

sql_file = open('./initdb/init.sql', 'w')

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

CREATE INDEX edges_label ON nodes (label);
\n"""

sql_file.write(create_tables)
sql_file.write('-- random user\n')
for result in json_data['results']:
    res = choices(res_dates)
    ts = round(res[0].timestamp())
    s = ('INSERT INTO nodes (label, props) VALUES '
         f'(\'User\', \'{{"name": "{result['name']['first']} {result['name']['last']}", "email": "{result['email']}", "created": {str(ts)}}}\')'
         ';\n')
    sql_file.write(s)

sql_file.write('\n')

sql_file.write('-- edges for first user\n')
random_list = random.sample(range(1, nodes), 10)
for i in random_list:
    res = choices(res_dates)
    ts = round(res[0].timestamp())
    s = ('INSERT INTO edges (previous_node, next_node, label, props) VALUES '
         f'(1, {i}, \'LIKES\', \'{{"since": {ts}}}\')'
        ';\n')
    sql_file.write(s)

sql_file.write('\n')

sql_file.write('-- edges for second user\n')
random_list = random.sample(range(2, nodes), 10)
for i in random_list:
    res = choices(res_dates)
    ts = round(res[0].timestamp())
    s = ('INSERT INTO edges (previous_node, next_node, label, props) VALUES '
         f'(2, {i}, \'LIKES\', \'{{"since": {ts}}}\')'
        ';\n')
    sql_file.write(s)

sql_file.write('\n')

sql_file.write('-- random edges for user\n')
r = random.sample(range(2, nodes), nodes - 2)
for i in range(3, nodes):
    _r = choices(r)
    if i == _r[0]:
        while i == _r[0]:
            _r = choices(r)
    res = choices(res_dates)
    ts = round(res[0].timestamp())
    s = ('INSERT INTO edges (previous_node, next_node, label, props) VALUES '
         f'({i}, {_r[0]}, \'LIKES\', \'{{"since": {ts}}}\')'
        ';\n')
    sql_file.write(s)

sql_file.close()
print('SQL file created')
import psycopg2
from pyvis.network import Network

conn = psycopg2.connect(database='postgres',
                        host='127.0.0.1',
                        user='postgres',
                        password='postgres',
                        port='5432')

cursor = conn.cursor()

g = Network(width='100%',
            height='800px', 
            directed =True,
            neighborhood_highlight=True)

cursor.execute('SELECT * FROM nodes')
for i in cursor.fetchall():
    g.add_node(i[0], size=20, label=f'{i[0]} {i[2]['name']}', title=f'{i[2]}')

cursor.execute('SELECT * FROM edges')
for i in cursor.fetchall():
    g.add_edge(i[0], i[1], title=f'{i[2]}\n{i[3]}')

g.show('show.html', notebook=False)
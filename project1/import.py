import psycopg2
import csv


#
# conn = psycopg2.connect("dbname='d31etsp4aep187' user='nhedgifrbqclmi' host='ec2-54-217-205-90.eu-west-1.compute.amazonaws.com' password='9d969bc86ee5bcb1ddbe7ffa81ad51003003fa99ae916a4ded2fd2486db2db1b'")
# cur = conn.cursor()
# with open('books.csv', 'r') as file:
#     f = csv.reader(file)
#     count = 0
#     for i in [k for k in f][1:]:
#         #print(i)
#         count += 1
#         if i:
#             for l in range(len(i)):
#                 if "'" in i[l]:
#                     i[l] = i[l].replace("'", "''")
#             cur.execute("""INSERT INTO books (isbn, title, author, year) VALUES ('%s','%s','%s','%s');""" % (i[0], i[1], i[2], i[3]))
#             print(count)
# conn.commit()
#print(cur.fetchall())
conn = psycopg2.connect("dbname='d31etsp4aep187' user='nhedgifrbqclmi' host='ec2-54-217-205-90.eu-west-1.compute.amazonaws.com' password='9d969bc86ee5bcb1ddbe7ffa81ad51003003fa99ae916a4ded2fd2486db2db1b'")
cur = conn.cursor()
cur.execute("""CREATE TABLE reviews (
                                    id SERIAL,
                                    book_id int references books(id),
                                    user_id int references users(id),
                                    rating int,
                                    review varchar(1000)
                                    );""")
conn.commit()
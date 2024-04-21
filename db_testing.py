import sqlite3
import json

con= sqlite3.connect("revhire.db")
cur=con.cursor()

# cur.execute("DELETE from applications where id = 1")

# cur.execute("insert into applications (id,application_id,application_status)values(?,?,?)",
#          (1,"101,102","approved, approved"))



x = cur.execute("""
    SELECT * FROM job where job_id = 1
""")

# y = list(x.fetchone())
# print(y)
# applied_jobs = str(y[1]).split(",")
# jobs_status = str(y[2]).split(",")

# z = dict(zip(applied_jobs, jobs_status))
# print(z)






print(x.fetchone()[3])


# for i in x:
#     print(i[0])

# print(x.fetchall())
# print(type(x))
# y = cur.fetchall()
# print(y)



# columns = [column[0] for column in cur.description]
# data = [dict(zip(columns, row)) for row in cur.fetchall()]

# z = json.dumps(data)
# z = json.loads(z)

# print(z, len(z), type(z[0]))
# dic = {}
# j = 0
# for i in z:
#     dic[j] = i
#     j+=1
# print(dic)

con.commit()
con.close()
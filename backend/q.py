import csv, sqlite3
import os.path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "db.sqlite3")
con = sqlite3.connect(db_path)
cur = con.cursor()

# cur.execute("DELETE FROM recipes_ingredient")
# con.commit()
# con.close()
# recipes_ingredient
with open('backend/ingredients.csv','r') as fin:
    n = 1
    for row in fin:
        a = row.split(',')
        n += 1
        while len(a) != 2:
            d = a.pop(1)
            a[0] = a[0] + d

        cur.execute("INSERT INTO recipes_ingredient VALUES (NULL,?,?)", a)
        con.commit()
con.close()
print('\n records')



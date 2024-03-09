import sqlite3 as db
from Include.sql import *

def testSqlite():
    connect = db.connect("./db/test.db")
    cursor = connect.cursor()

    with open("./db/sql_scripts/initTestDB.sql", "r") as file:
        script = ""
        for line in file.readlines():
            script += line
        print( script )
        cursor.executescript(script)
        file.close()

    cursor.execute("SELECT * FROM images")
    print( cursor.fetchall() )
    cursor.execute("SELECT * FROM verification")
    print( cursor.fetchall() )

    cursor.execute("INSERT INTO images (imgURL, labelID) VALUES(\"soup.png\", 2)")
    cursor.execute("""INSERT INTO verification (imageID) SELECT i.id FROM images i LEFT JOIN verification v ON i.id = v.imageID WHERE v.imageID IS NULL;""")
    print("===== AFTER =====")
    cursor.execute("SELECT * FROM images")
    print( cursor.fetchall() )
    cursor.execute("SELECT * FROM verification")
    print( cursor.fetchall() )


def testSql():
    runScript("initTestDB")
    print( select("*", "labels") )
    print( select("*", "images") )
    
    print( verify() )
    print( updateImages() )

    

#////////// EXECUTE //////////////////////////
testSql()
#testSqlite()
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

    print( updateImages([{'id': 1, 'label': 'frog'}, {'id': 2, 'label': 'bird'}]) )
    print( select("id, imgURL, label", "images") )


def testAll():
    runScript("initTestDB")

    outTest(select("imgURL", "images"), [('chicken.png',), ('dino.png',), ('dog.png',)])
    outTest(select("imgURL", "images", "id = 2"), [('dino.png',)])

    outTest(insertImages([{'imgURL': 'soup123.png', 'label': 'cat'}]), 1)
    outTest(insertLabels(['tag1', 'tag2', 'tag3']), 3)
    outTest(insertLabels('tag4'), 1)

    outTest(verify([2,3]), 2)
    outTest(len(select("id", "images", "verified = 1")), 2)

    outTest(verify([1], 2), 1)
    outTest(len(select("id", "images", "verified = 2")), 1)



def outTest(output, expected):
    if output == expected:
        print(True)
    else:
        print(f"""===== TEST FAIL ===================
            RETURNED : {output}
            EXPECTED : {expected}
===================================
    """)


    

#////////// EXECUTE //////////////////////////
#testSql()
#testSqlite()
testAll()
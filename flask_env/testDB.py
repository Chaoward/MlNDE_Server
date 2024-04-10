import sqlite3 as db
from Include.model import create_base_model
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
    outTest(insertModel_Label( [{'modelID': 1, 'labelID': 404, 'count': 3}, {'modelID': 1, 'labelID': 500, 'count': 7}] ), 2)
    outTest(select("*", "model_label"), [])
    #outTest(select("imgURL", "images", where="verified=0"), [])
    #outTest(select("DISTINCT classID", "labels"), [])
    #outTest(select("count(*)", "labels"), [(1875,)])
    #outTest(insertImages([{'sys_label': 'tiger shark'}], True), 1)
    #outTest(select("*", "labels"), [('chicken',), ('dino',), ('dog',)])
    


def testAll():
    outTest(select("imgURL", "images"), [('chicken.png',), ('dino.png',), ('dog.png',)])
    outTest(select("imgURL", "images", "id = 2"), [('dino.png',)])

    outTest(insertImages([{'imgURL': 'soup123.png', 'label': 'cat'}]), 1)
    outTest(insertLabels(['tag1', 'tag2', 'tag3']), 3)
    outTest(insertLabels('tag4'), 1)

    outTest(verify([2,3]), 2)
    outTest(len(select("id", "images", "verified = 1")), 2)

    outTest(verify([1], 2), 1)
    outTest(len(select("id", "images", "verified = 2")), 1)

def test():
    create_base_model().save("./db/1-model.h5")


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
#test()
testSql()
#testSqlite()
#testAll()
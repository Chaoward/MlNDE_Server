import sqlite3 as db

SQL_SCRIPT_DIR = "../db/sql_scripts/"
DB_PATH = "../db/test.db"


def select(cols, table, where):
    try:
        connect = db.connect(DB_PATH)
        cur = connect.cursor()
        
        #parse columns
        if type(cols) == list:
            strCols = ""
            for i in range(0, len(cols)):
                strCols += (", " if i > 0 else "") + cols[i]
            cols = strCols

        cur.execute(f"SELECT {cols} FROM {table} {"WHERE " + where if len(where) > 0 else ""};")
        return cur.fetchall()
    except db.OperationalError as e:
        print(e)
        raise
    finally:
        connect.close()


# imgs = [ {imageURl, label} ]
def insertImages(imgs):
    try:
        connect = db.connect(DB_PATH)
        cur = connect.cursor()

        for ele in imgs:
            cur.execute("INSERT INTO images (imgURL, labelID) VALUES(?, ?);", (ele["imageURl"], ele["label"]) )

        #update verification table
        cur.executescript("""
            INSERT INTO verification (imageID)
            SELECT i.id FROM images i LEFT JOIN verification v ON i.id = v.imageID
            WHERE v.imageID IS NULL;
        """)
    except db.OperationalError as e:
        print(e)
        raise
    finally:
        connect.close()



# TODO: inserting labels
def insertLabels():
    pass



import sqlite3 as db

DB_PATH = "./db/labels.db"
LABELS_TXT = "./db/labels.txt"

def importLabels():
    try:
        connect = db.connect(DB_PATH)
        cur = connect.cursor()

        cur.execute("CREATE TABLE IF NOT EXISTS labels (classID INT, label TEXT);")

        file = open(LABELS_TXT, "r")
        line = file.readline()
        while line != "":
            #parse line
            line = line.strip().split("~")
            for label in line[1].split(","):
                cur.execute(f"INSERT INTO labels VALUES ({line[0]}, \"{label.strip()}\");")
            line = file.readline()
        cur.execute("SELECT count(*) FROM labels;")
        print(cur.fetchall())
        
        connect.commit()
    except FileNotFoundError as e:
        print(e)
        raise
    finally:
        connect.close()

importLabels()
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



#===== insertImages ==================================
# Inserts new images with labels into DB.
# 
# PARAM: imgs : [ {imageURl, label} ]
#=====================================================
def insertImages(imgs):
    try:
        connect = db.connect(DB_PATH)
        cur = connect.cursor()

        for ele in imgs:
            cur.execute("INSERT INTO images (imgURL, label) VALUES(?, ?);", (ele["imageURl"], ele["label"]) )

        #update verification table
        cur.executescript("""
            INSERT INTO verification (imageID)
            SELECT i.id FROM images i LEFT JOIN verification v ON i.id = v.imageID
            WHERE v.imageID IS NULL;
        """)
    except db.OperationalError as e:
        print(e)
        connect.rollback()
        raise
    finally:
        connect.close()



#===== insertLabels ==================================
# Attempts a list of string labels and inserts to DB.
# 
# PARAM: labels : [ label<String> ]
#
# RETURNS: int, number of successful inserts
#=====================================================
def insertLabels(labels):
    try:
        connect = db.connect(DB_PATH)
        cur = connect.cursor()
        
        count = 0
        for label in labels:
            #check if label exist
            cur.execute("SELECT label FROM labels WHERE label = ?", (label) ) 
            if cur.fetchone() is not None:
                continue 

            #insert
            cur.execute("INSERT INTO labels VALUES(?);", (label) )
            count += 1
    except db.OperationalError as e:
        print(e)
        raise
    finally:
        connect.close()
        return count



#===== setRelease ====================================
# Updates models table to mark a target version
# and unmarks the current release version.
# 
# RETURNS: int
#   0 : Success
#   1 : Failed to find target version
#  -1 : target version already the release version
#======================================================
def setRelease(verNum):
    try:
        connect = db.connect(DB_PATH)
        cur = connect.cursor()
        
        cur.execute(f"SELECT release FROM models WHERE versionNum = {verNum};")
        result = cur.fetchall()
        if len(result) == 0:    #check if target version exist
            return 1
        elif result[0] == 1:    #check if target version is already release ver
            return -1
            
        # update release mark
        cur.executescript(f"""
            UPDATE models SET release = 0 WHERE release = 1;
            UPDATE models SET release = 1 WHERE versionNum = {verNum}
            SELECT release FROM models WHERE versionNum = {verNum};
        """)
        result = cur.fetchall()
        if result[0] == 1:
            return 0
        else:
            return 1
    except db.OperationalError as e:
        print(e)
        raise
    finally:
        connect.close()


#===== runScript =========================
def runScript(scriptName):
    try:
        connect = db.connect(DB_PATH)
        cur = connect.cursor()

        file = open(f"{SQL_SCRIPT_DIR}{scriptName}.sql", "r")
        script = ""
        for line in file.readlines():
            script += line
            if line.endswith(";"):
                cur.executescript(script)
                script = ""
        file.close()
    except FileNotFoundError as e:
        print(e)
        raise
    finally:
        connect.close()
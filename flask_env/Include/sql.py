import sqlite3 as db

DEBUG = True

SQL_SCRIPT_DIR = "./db/sql_scripts/"
DB_PATH = "./db/main.db"


##### TABLES ######################################################################  
# 
#///// images /////
# Holds image filenames pair with their labels.
# Tagged appropiately whither they are unverfied, verfied, or trained.
# COLUMNS
#   | imgURL TEXT : File name of image on system
#   | label TEXT  : string label that exist on the labels table
#   | verified INT DEFAULT 0  : status code of the following...
#       * 0 : unverfied
#       * 1 : verfied
#       * 2 : trained
#   | id INTEGER PRIMARY KEY
# 
# 
#///// labels /////
# COLUMNS
#   | label TEXT PRIMARY KEY : String label
# 
# 
#///// models /////
# Holds information of each model 
# COLUMNS
#   | versionNum TEXT : string version number in a major.minor.patch form. EX: 1.1.1
#   | release BIT DEFAULT 0 : boolean whither the model is the release version
#   | imgsTrained INT DEFAULT 0 : Number of images used to train this model
#   | id INTEGER PRIMARY KEY
# 
# 
#///// model_label /////
# many-to-many table for models trained with new labels
# COLUMNS
#   | modelID INTEGER NOT NULL
#   | labelID INTEGER NOT NULL
#######################################################################################  




def select(cols, table, where=""):
    try:
        connect = db.connect(DB_PATH)
        cur = connect.cursor()
        
        #parse columns
        if type(cols) == list:
            strCols = ""
            for i in range(0, len(cols)):
                strCols += (", " if i > 0 else "") + cols[i]
            cols = strCols

        cur.execute(f"SELECT {cols} FROM {table} {'WHERE ' + where if len(where) > 0 else ''};")
        return cur.fetchall()
    except db.OperationalError as e:
        print(e)
        raise
    finally:
        connect.close()



#===== insertImages ==================================
# Accepts new images with labels and inserts them into DB.
# 
# PARAM: imgs : [ {imageURl, label} ]
#
# RETURNS: int, number of successful inserts
#=====================================================
def insertImages(imgs):
    count = 0
    try:
        connect = db.connect(DB_PATH)
        cur = connect.cursor()
        wherequery = "("

        for ele in imgs:
            cur.execute("INSERT INTO images (imgURL, label) VALUES(?, ?);", (ele["imgURL"], ele["label"]) )
            wherequery += f"'{ele['imgURL']}',"
        wherequery = wherequery[:-1] + ");"

        cur.execute(f"SELECT id FROM images WHERE imgURL IN {wherequery}")
        count = len(cur.fetchall())

        connect.commit()
    except db.OperationalError as e:
        print(e)
        connect.rollback()
        count = 0
        raise
    finally:
        connect.close()
        return count


#===== updateImages ==================================
# Attempts a list of string labels and inserts to DB.
# 
# PARAM: imgList : [ {"id": int, "label": string, ...} ]
#
# RETURNS: None
#=====================================================
def updateImages(imgList):
    try:
        connect = db.connect(DB_PATH)
        cur = connect.cursor()

        for img in imgList:
            cur.execute(f"UPDATE images SET label = '{img['label']}' WHERE id = {img['id']};")
        
        connect.commit()
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
        
        #single input
        if type(labels) == str:
            labels = [ labels ]

        count = 0
        for label in labels:
            #check if label exist
            cur.execute(f"SELECT label FROM labels WHERE label = '{label}';") 
            if len(cur.fetchall()) == 0:
                #insert
                cur.execute(f"INSERT INTO labels VALUES('{label}');")
                count += 1
        connect.commit()
    except db.OperationalError as e:
        print(e)
        connect.rollback()
        count = 0
        raise
    finally:
        connect.close()
        return count
    


#===== verify =======================================
# Accepts a list of image ids and sets their verified
# code to 1 by default, or the other codes specified by a param.
# 
# PARAM: imgIDList : [ id<Int> ] | id<Int>
#        status : Int
#           * 0 : unverified
#           * 1 : verified
#           * 2 : trained
#
# RETURNS: int, number of successful verifications
#=====================================================
def verify(imgIDList, status=1):
    if (type(imgIDList) == list and len(imgIDList) == 0): 
        return 0
    count = None
    try:
        connect = db.connect(DB_PATH)
        cur = connect.cursor()
        queryList = "("

        #single inputs
        if type(imgIDList) == int:
            cur.execute(f"UPDATE images SET verified = {status} WHERE id = {imgIDList};")
            cur.execute(f"SELECT id FROM images WHERE verified = {status} AND id = {imgIDList};")
            count = len(cur.fetchall())
            connect.commit()
            return count
            
            
        #convert list into string list for sql
        for i in range( len(imgIDList) ):
            queryList += str(imgIDList[i])
            if i != len(imgIDList) - 1:
                queryList += ","
        queryList += ");"

        #Update verify tag of images in DB
        cur.execute(f"UPDATE images SET verified = {int(status)} WHERE id IN {queryList}")

        #get count of successful updates
        cur.execute(f"SELECT id FROM images WHERE verified = {int(status)} AND id IN {queryList}")
        count = len(cur.fetchall())

        connect.commit()
    except db.OperationalError as e:
        print(e)
        connect.rollback()
        raise
    finally:
        connect.close()
        return count if count is not None else 0



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
        
        cur.execute(f"SELECT release FROM models WHERE versionNum = '{verNum}';")
        result = cur.fetchall()
        if len(result) == 0:    #check if target version exist
            return 1
        elif result[0] == 1:    #check if target version is already release ver
            return -1
            
        # update release mark
        cur.executescript(f"""
            UPDATE models SET release = 0 WHERE release = 1;
            UPDATE models SET release = 1 WHERE versionNum = '{verNum}';
            SELECT * FROM models WHERE release = 1;
        """)
        result = cur.fetchall()
        if len(result) == 1 and result[0][0] == verNum:
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
        cur.executescript(script)
        file.close()
    except FileNotFoundError as e:
        print(e)
        raise
    finally:
        connect.close()


#///// DEBUG SETUP ///////////////
runScript("initDB")
if DEBUG:
    runScript("copyDB")
    DB_PATH = "./db/debug_copy.db"
import sqlite3 as db
from werkzeug.utils import secure_filename
import config
import json
from os import path


USE_TEST_DB = config.USE_TEST_DB
IMAGE_PATH = config.IMAGES_DIR
SQL_SCRIPT_DIR = config.SQL_SCRIPT_DIR
DB_PATH = config.MAIN_DB_PATH


##### TABLES ######################################################################  
# 
#///// images /////
# Holds image filenames pair with their labels.
# Tagged appropiately whither they are unverfied, verfied, or trained.
# COLUMNS
#   | imgURL TEXT : File name of image on system
#   | userLabel TEXT  : string label entered by a user
#   | sysLabel TEXT  : string label that exist on the labels table
#   | verified INT DEFAULT 0  : status code of the following...
#       * 0 : unverfied
#       * 1 : verified
#       * 2 : trained
#   | id INTEGER PRIMARY KEY
# 
# 
#///// labels /////
# COLUMNS
#   | classID INT : class ID number, not unique
#   | label TEXT : String label
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
#   | labelID TEXT NOT NULL
#   | count INT DEFAULT 0
#######################################################################################  




def select(cols, table="", where=""):
    try:
        connect = db.connect(DB_PATH)
        cur = connect.cursor()
        
        #parse columns
        if type(cols) == list:
            strCols = ""
            for i in range(0, len(cols)):
                strCols += (", " if i > 0 else "") + cols[i]
            cols = strCols

        cur.execute(f"SELECT {cols} {'FROM ' + table if table != '' else ''} {'WHERE ' + where if where != '' else ''};")
        return cur.fetchall()
    except db.OperationalError as e:
        print(e)
        raise
    finally:
        connect.close()



#===== insertImages ==================================
# Accepts new images with labels and inserts them into DB.
# 
# PARAM: imgs : [ {sys_label, file, imgURL(optional)} ]
#
# RETURNS: int, number of successful inserts
#=====================================================
def insertImages(imgs, skipFile=False):
    count = 0
    try:
        connect = db.connect(DB_PATH)
        cur = connect.cursor()
        wherequery = "("
        
        for ele in imgs:
            #insert image data to sql DB; with imgURL if skipping file saving
            cur.execute(f"INSERT INTO images (sysLabel) VALUES('{ele['sys_label']}');")
            #cur.execute("INSERT INTO images (sysLabel, userLabel, imgURL) VALUES(?, ?, ?);", (ele['sys_label'], "", "" if "imgURL" not in ele else ele["imgURL"] ))
            
            if skipFile:
                continue

            #generate and update imgURL
            cur.execute("SELECT last_insert_rowid();")
            lastID = cur.fetchall()[0][0]
            imgURL = str(lastID) + secure_filename(ele['file'].filename)
            cur.execute("UPDATE images SET imgURL=? WHERE id=?;", (imgURL, lastID))
            wherequery += f"'{imgURL}',"

            #save image file with imgURL as file name
            ele['file'].save( path.join(IMAGE_PATH, imgURL) )
        wherequery = wherequery[:-1] + ");"

        cur.execute(f"SELECT count(*) FROM images WHERE imgURL IN {wherequery}")
        count = cur.fetchall()[0][0]

        connect.commit()
    except db.OperationalError as e:
        print(e)
        connect.commit()
        raise
    except Exception as e:
        print(e)
        raise
    finally:
        connect.close()
        return count


#===== updateImages ==================================
# Accepts a list of modified images and updates them
# in the DB.
# 
# PARAM: imgList : [ {"id": int, "user_label": string, "sys_label": string, ...} ]
#
# RETURNS: None
#=====================================================
def updateImages(imgList):
    try:
        connect = db.connect(DB_PATH)
        cur = connect.cursor()

        for img in imgList:
            cur.execute(f"UPDATE images SET sysLabel='{img['sys_label']}', userLabel='{img['user_label']}' WHERE id = {img['id']};")
        
        connect.commit()
    except db.OperationalError as e:
        print(e)
        connect.rollback()
        raise
    finally:
        connect.close()


#===== insertLabels <DEPRECATED> ==================================
# Accepts list of lavels and inserts them into the DB.
# 
# PARAM: labels : [ label<String> ]
#
# RETURNS: int, number of successful inserts
#==================================================================
def insertLabels(labels):
    return 0
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



#===== setRelease =====================================
# Updates models table to mark a target version
# and unmarks the current release version.
# 
# PARAMS: int, id of the model version
# 
# RETURNS: int
#   0 : Success
#   1 : Failed to find target version
#  -1 : target version already the release version
#======================================================
def setRelease(verID):
    try:
        connect = db.connect(DB_PATH)
        cur = connect.cursor()
        
        cur.execute(f"SELECT release FROM models WHERE id = {verID};")
        result = cur.fetchall()
        if len(result) == 0:    #check if target version exist
            return 1
        elif result[0][0] == 1:    #check if target version is already release ver
            return -1
            
        # update release mark
        cur.execute("UPDATE models SET release = 0 WHERE release = 1;")
        cur.execute(f"UPDATE models SET release = 1 WHERE id = {verID};")
        cur.execute("SELECT id FROM models WHERE release = 1;")

        result = cur.fetchall()
        if len(result) == 1 and result[0][0] == verID:
            return 0
        else:
            return 1
    except db.OperationalError as e:
        print(e)
        raise
    finally:
        connect.commit()
        connect.close()



#===== insertModel =====================================
# PARAM: model : kesas model reference
#        numOfImgs : int, number of images this new model is trained on
#
# RETURNS: int : modelID of newly inserted model else -1
#=======================================================
def insertModel(model, numOfImgs):
    try:
        connect = db.connect(DB_PATH)
        cur = connect.cursor()
        
        #record version on DB
        lastest_version = cur.execute("SELECT versionNum FROM models;").fetchall()[-1][0].split('.')
        cur.execute(f"INSERT INTO models(versionNum, imgsTrained) VALUES('{lastest_version[0]}.{int(lastest_version[1])+1}.0', {numOfImgs});")
        cur.execute(f"SELECT id FROM models WHERE versionNum='{lastest_version[0]}.{int(lastest_version[1])+1}.0';")
        newModelId = cur.fetchall()[0][0]

        #use id to save model as a file
        model.save(f"{config.MODELS_DIR}{newModelId}-model.h5")

        #save as a json format
        with open(f"{config.MODELS_DIR}{newModelId}.json", "w+") as file:
            file.write( json.dumps(model.to_json()) )
            file.close()

        connect.commit()
    except db.OperationalError as e:
        print(e)
        connect.rollback()
        newModelId = -1
        raise
    except Exception as e:
        print(e)
        connect.rollback()
        newModelId = -1
        raise
    finally:
        connect.close()
        return newModelId
    


#===== insertModel_Label ==============================
# Add a new entry to model_label table
# 
# PARAM: entries : [ {modelID, labelID(label's classID), count}... ]
#
# RETURNS : int : count of successful entries
#======================================================
def insertModel_Label(entries):
    count = 0
    try:
        connect = db.connect(DB_PATH)
        cur = connect.cursor()

        for entry in entries:
            cur.execute("INSERT INTO model_label (modelID, labelID, count) VALUES(?, ? ,?)", (entry['modelID'], entry['labelID'], entry['count']) )
            count += 1
        
        connect.commit()
    except db.OperationalError as e:
        print(e)
        connect.commit()
        raise
    except Exception as e:
        print(e)
        connect.rollback()
        count = 0
        raise
    finally:
        connect.close()
        return count


#===== runScript =====================================
# Runs a sql script from the sql_scripts folder
# 
# PARAM: scriptName : string, filename of the script
#                             without file extension 
#====================================================
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


#===== changeDB ===========================
# changes the DB_PATH to specified DB file
#==========================================
def changeDB(database):
    global DB_PATH
    try:
        if not path.exists(f"./db/{database}.db"):
            raise FileNotFoundError
        DB_PATH = f"./db/{database}.db"
    except FileNotFoundError as e:
        print(e)
        raise


#///// DATABASE SETUP ///////////////
if config.USE_TEST_DB:
    DB_PATH = config.TEST_DB_PATH
    runScript("initTestDB")
else:
    runScript("initDB")

if config.DEBUG and not config.USE_TEST_DB:
    runScript("copyDB")
    DB_PATH = "./db/debug_copy.db"
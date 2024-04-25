from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from Include import sql
from Include.model import create_training_set, fine_tune_model, saveModel, recycleModel
from keras import saving, models
import json
import config

app = Flask(__name__)
CORS(app)

LAST_MODID_REQUEST = None;  

def isAllowedFile(fileName):
   ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif"}
   return "." in fileName and fileName.split(".")[1] in ALLOWED_EXTENSIONS



@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

#===== LABELS ==================================================

@app.route("/labels", methods=["GET", "POST"])
def handleLabels():
    if request.method == "GET":
        try:
            labels = sql.select("label", "labels")
            return jsonify( list( map(lambda x: x[0], labels) ) )
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    elif request.method == "POST":
        return jsonify({"success": False, "error": "POST Method for labels is deprecated, at least temporay."}), 500  
        try:
            labels = request.json
            if type(labels) != list:
                return jsonify({"success": False, "error": "No labels provided"}), 400
            
            count = sql.insertLabels(labels)    
            return jsonify({"success": True, "count": count})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500


#===== IMAGES ==================================================
# image objects { id, imgURL, label }
# image upload form data { file[], label[] }
@app.route("/images/unverified", methods=["GET", "POST"])
def handleUnverified():
    if request.method == "GET":
        try:
            images_data = sql.select("imgURL, sysLabel, userLabel, id", "images", where="verified=0")
            images = []
            for img_data in images_data:
                img_dict = {
                    "imgURL": img_data[0],
                    "sysLabel": img_data[1],
                    "userLabel": img_data[2],
                    "id": img_data[3]
                }
                images.append(img_dict)
            return jsonify(images)
        except Exception as e:
            print(e.with_traceback())
            return jsonify({"success": False, "error": str(e)}), 500
    elif request.method == "POST":
        try:
            if 'file' not in request.files:
                return jsonify({"success": False, "error": "No file part"}), 400
            if 'label' not in request.form:
                return jsonify({"success": False, "error": "No label part"}), 400
        
            file = request.files.getlist("file")
            sys_labels = request.form.getlist("label")
            user_labels = None if 'userLabel' not in request.form else request.form.getlist("userLabel")

            if len(file) != len(sys_labels):
                return jsonify({"success": False, "error": "file and label amount mismatch"}), 400
        
            imgList = []
            for i in range( len(file) ):
                if file[i].filename == '' or not isAllowedFile(file[i].filename):
                    continue
                imgList.append({
                    "file": file[i],
                    "sysLabel": sys_labels[i],
                    "userLabel": "" if user_labels == None else user_labels[i]
                })
                print(file[i].name)
                print(sys_labels[i])

            return jsonify({"success": True, "count": sql.insertImages(imgList)}), 200
        except Exception as e:
            print(e.with_traceback())
            return jsonify({"success": False, "error": str(e)}), 500

        """
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)  # Save the uploaded file
        
            # Insert image details into the database
            label = request.form.get('label')
            sql.insertImages([{'imgURL': filename, 'label': label}])
        """
        
        return jsonify({"success": True, "message": "File uploaded successfully"}), 200
        


@app.route("/images/unverified/verify", methods=["PUT"])
def verify():
    if request.method != "PUT":
        return jsonify({'success': False, 'error': 'PUT request ONLY.'})
    try:
        imgList = request.json
        """
        for i in range(len(imgList)):
            imgList[i]["sys_label"] = imgList[i].pop("label")
            imgList[i]["user_label"] = ""   # temp
        """
        sql.updateImages(imgList)
        count = sql.verify( list(map(lambda img: img['id'], imgList)) )
        return jsonify( {'success': True, 'count': count} if count != 0 else {'success': False, 'error': "Problem occured while verifying images"} )
    except Exception as e:
        print(e.with_traceback())
        return jsonify({'success': False, "error": str(e)}), 500



@app.route("/images/verified", methods=["GET", "POST"])
def handleVerified():
    try:
        images = sql.select("*", "images", where="verified=1")
        return jsonify({"success": True, "images": images})
    except Exception as e:
        print(e.with_traceback())
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/images/<filename>")
def serveImage(filename):
    return send_file(f"./db/images/{filename}")


@app.route("/images/train", methods=["PUT"])
def trainImages():
    global IS_TRAINING
    if (IS_TRAINING):
        return jsonify({"success": False, "error": "Server Already in the Process of Fine Tuning"}), 400
    try:
        IS_TRAINING = True

        # Get all verified images with their labels
        verified = sql.select("imgURL, sysLabel", "images", where="verified=1")
        if (len(verified) == 0):
            return jsonify({"success": False, "error": "No Verified Images to Train"}), 400
        
        #split labels and imgURLs
        img_urls = list( map(lambda x: x[0], verified) )
        label_ids = list( map(lambda x: x[1], verified) )

        # query and change all string labels to their classIDs
        for i in range(0, len(label_ids)):
            label_ids[i] = sql.select("classID", "labels", f"label='{label_ids[i]}'")[0][0]

        # create image training set
        print("===== Create Training Set =====")
        training_set = create_training_set(img_urls)

        #read current model file from folder
        print("===== Loading Model =====")
        lastest_model_id = sql.select("id", "models")[-1][0]
        model = saving.load_model(f"{config.MODELS_DIR}{lastest_model_id}.h5")

        # fine tune
        print("===== Fine Tune =====")
        model = fine_tune_model(model, training_set, label_ids)

        # save newly updated model in file_sys and DB
        print("===== Saving Model =====")
        modelID = sql.insertModel(len(img_urls))  #create record on DB
        if modelID < 0:
            return jsonify({"success": False, "error": "Failed to save Model"}), 500
        saveModel(model, modelID)                 #saving as a file

        # Update their verified status to 2 (trained)
        print("===== Updating Verify =====")
        img_ids = sql.select("id", "images", "verified=1")
        img_ids = list( map(lambda x: x[0], img_ids) )
        count = sql.verify(img_ids, status=2)

        # record model_label entries for the new model
        entries = {}
        for id in label_ids:
            if (entries.get(str(id)) == None):
                entries[str(id)] = {"modelID": modelID, "labelID": id, "count": 1}
            else:
                entries[str(id)]["count"] += 1
        sql.insertModel_Label( list( entries.values() ) )

        return jsonify({"success": True, "count": count})
    except Exception as e:
        print(e)
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        IS_TRAINING = False



 # TODO : recycle model file 
#===== MODELS ==================================================
@app.route("/models/", methods=["GET", "DELETE"])
def handleModel():
    if request.method == "GET":
        try:
            from os import path
            modelPath = f"{config.MODELS_DIR}{request.args.get('id')}/model.json"
            
            if not path.exists(modelPath):
                return jsonify({"success": False, "error": f"Model with id \'{request.args.get('id')}\' Not Found!"}), 400

            file = open(modelPath, "r")
            global LAST_MODID_REQUEST
            LAST_MODID_REQUEST = request.args.get('id')
            return jsonify(json.load(file)), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    elif request.method == "DELETE":
        try:
            idList = request.json["id"]
            if type(idList) != list and type(idList) != int:
                return jsonify({"success": False, "error": f"id must be an int or list<int> : Got {str(type(idList))}"}), 400
            
            count = sql.removeModel(idList)
            if type(idList) == list:
                if (count != len(idList)):
                    existingId = sql.select("id", "models")
                    for Id in existingId:
                        try:
                            idList.remove(Id[0])
                        except ValueError:
                            pass
                for Id in idList:
                    recycleModel(Id)
            else:
                recycleModel(idList)

            return jsonify({"success": True, "count": count})
        except Exception as e:
            print(e.with_traceback())
            return jsonify({"success": False, "error": str(e)}), 500
        



@app.route("/models/info", methods=["GET"])
def handleModelInfo():
    from os import path
    try:
        models = sql.select("*", "models")
        payload = []

        #temp
        print( sql.select("*", "model_label") )
        
        for mod in models:
            mod_labals = sql.select("l.label, m.count", "model_label AS m INNER JOIN labels AS l ON m.labelID = l.classID", f"m.modelID={mod[4]}")
            
            payload.append({
                "version": mod[0],
                "date": mod[1],
                "release": mod[2] == 1,
                "images": mod[3],
                "id": mod[4],
                "labels": list( map(lambda x: {"label": x[0], "count": x[1]}, mod_labals) ),
                "size": path.getsize(f"{config.MODELS_DIR}{mod[4]}.h5")   #bytes
            })

        return jsonify(payload)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/models/release", methods=["GET", "PUT"])
def handleRelease():
    if request.method == "GET":
        modelID = sql.select("id", "models", "release=1")
        if len(modelID) == 0:
            return jsonify({"success": False, "error": "Release not Found"}), 500
        modelID = modelID[0][0]

        file = open(f"{config.MODELS_DIR}{modelID}/model.json", "r")
        global LAST_MODID_REQUEST
        LAST_MODID_REQUEST = modelID
        return jsonify(json.load(file)), 200
    elif request.method == "PUT":
        try:
            version_id = request.json["verID"]
            result = sql.setRelease(version_id)

            if result == 0:
                return jsonify({"success": True}), 200
            elif result == 1:
                return jsonify({"success": False, "error": f"Model with id : {version_id} not found"}), 404
            elif result == -1:
                return jsonify({"success": False, "error": f"Model with id : {version_id} is already the release version"}), 400
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500


@app.route("/models/release/info", methods=["GET"])
def handleReleaseInfo():
    try:
        queryData = sql.select("*", "models", "release=1")[0]
        queryData = {
            "version": queryData[0],
            "date": queryData[1],
            "release": queryData[2],
            "images": queryData[3],
            "id": queryData[4]
        }
        return jsonify(queryData), 200
    except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    


@app.route("/models/<binshard>")
def fetchBinShards(binshard):
    return send_file(f"{config.MODELS_DIR}{LAST_MODID_REQUEST}/{binshard}")
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from Include import sql
from Include.model import create_training_set, fine_tune_model
from keras import saving, models
import config

app = Flask(__name__)
CORS(app)


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
            images_data = sql.select("imgURL, sysLabel, id", "images", where="verified=0")
            images = []
            for img_data in images_data:
                img_dict = {
                    "imgURL": img_data[0],
                    "label": img_data[1],
                    "id": img_data[2]
                }
                images.append(img_dict)
            return jsonify(images)
        except Exception as e:
            print(e)
            return jsonify({"success": False, "error": str(e)}), 500
    elif request.method == "POST":
        try:
            if 'file' not in request.files:
                return jsonify({"success": False, "error": "No file part"}), 400
            if 'label' not in request.form:
                return jsonify({"success": False, "error": "No label part"}), 400
        
            file = request.files.getlist("file")
            labels = request.form.getlist("label")

            if len(file) != len(labels):
                return jsonify({"success": False, "error": "file and label amount mismatch"}), 400
        
            imgList = []
            for i in range( len(file) ):
                if file[i].filename == '' or not isAllowedFile(file[i].filename):
                    continue
                imgList.append({
                    "file": file[i],
                    "sys_label": labels[i]
                })
                print(file[i].name)
                print(labels[i])

            return jsonify({"success": True, "count": sql.insertImages(imgList)}), 200
        except Exception as e:
            print(e)
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
        for i in range(len(imgList)):
            imgList[i]["sys_label"] = imgList[i].pop("label")
            imgList[i]["user_label"] = ""   # temp
        sql.updateImages(imgList)
        count = sql.verify( list(map(lambda img: img['id'], imgList)) )
        return jsonify( {'success': True, 'count': count} if count != 0 else {'success': False, 'error': "Problem occured while verifying images"} )
    except Exception as e:
        return jsonify({'success': False, "error": str(e)}), 500



@app.route("/images/verified", methods=["GET", "POST"])
def handleVerified():
    try:
        images = sql.select("*", "images", where="verified=1")
        return jsonify({"success": True, "images": images})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/images/<filename>")
def serveImage(filename):
    return send_file(f"./db/images/{filename}")


@app.route("/images/train", methods=["PUT"])
def trainImages():
    try:
        # Get all verified images with their labels
        verified = sql.select("imgURL, sysLabel", "images", where="verified=1")
        if (len(verified) == 0):
            return jsonify({"success": False, "error": "No Verified Images to Train"}), 400
        
        #split labels and imgURLs
        img_urls = list( map(lambda x: x[0], verified) )
        label_ids = list( map(lambda x: x[1], verified) )

        # query and change all string labels to their classIDs
        for i in range(0, len(label_ids)):
            label_ids[i] = sql.select("classID", "labels", f"label='{label_ids[i]}'")

        # create image training set
        print("===== Create Training Set =====")
        training_set = create_training_set(img_urls)

        #read current model file from folder
        print("===== Loading Model =====")
        lastest_model_id = sql.select("id", "models")[-1][0]
        model = saving.load_model(f"{config.MODELS_DIR}{lastest_model_id}-model.h5")

        # fine tune
        print("===== Fine Tune =====")
        model = fine_tune_model(model, training_set, label_ids)

        # save newly updated model in file_sys and DB
        print("===== Saving Model =====")
        sql.insertModel(model, len(img_urls))

        # Update their verified status to 2 (trained)
        print("===== Updating Verify =====")
        img_ids = sql.select("id", "images", "verified=1")
        img_ids = list( map(lambda x: x[0], img_ids) )
        count = sql.verify(img_ids, status=2)

        return jsonify({"success": True, "count": count})
    except Exception as e:
        print(e)
        return jsonify({"success": False, "error": str(e)}), 500



# TODO : implement file size return 
#===== MODELS ==================================================
@app.route("/models", methods=["GET"])
def getModels():
    try:
        models = sql.select("*", "models")
        payload = []
        
        for mod in models:
            mod_labals = sql.select("label", "model_label", f"modelID={mod[3]}")
            payload.append({
                "versionNum": mod[0],
                "release": mod[1] == 1,
                "imgsTrained": mod[2],
                "id": mod[3],
                "labels": list( map(lambda x: x[0], mod_labals) ),
                "size": "100MB"
            })

        return jsonify(payload)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


#   TODO : implement GET, returns the release model file
@app.route("/models/release", methods=["GET", "PUT"])
def handleRelease():
    if request.method == "GET":
        modelID = sql.select("id", "models", "release=1")
        if len(modelID) == 0:
            return jsonify({"success": False, "error": "Release not Found"}), 500
        modelID = modelID[0][0]

        return jsonify({"success": True, "model": models.load_model(f"{config.MODELS_DIR}{modelID}-model.h5").to_json() })
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
            return jsonify({"error": str(e)}), 500
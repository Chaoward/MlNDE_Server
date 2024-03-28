from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from json import load as json_load

app = Flask(__name__)
app.config.from_file("config.json", load=json_load)
CORS(app)

# * IMPORTANT * : imports using flask app configs go in this block
with app.app_context():
    from Include import sql



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
        # Get all verified images
        verified_images = sql.select("*", "images", where="verified=1")
        # Update their verified status to 2 (trained)
        img_ids = [img["id"] for img in verified_images]
        count = sql.verify(img_ids, status=2)
        return jsonify({"success": True, "count": count})
    except Exception as e:
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
    
@app.route("/models/release", methods=["PUT"])
def setRelease():
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
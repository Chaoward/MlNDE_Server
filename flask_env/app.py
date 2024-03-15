from flask import Flask, send_from_directory, request, jsonify
from Include import sql
from werkzeug.utils import secure_filename
import os


app = Flask(__name__)
UPLOAD_FOLDER = "./db/images/"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# images, labels, models

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
@app.route("/images/unverified", methods=["GET", "POST"])
def handleUnverified():
    if request.method == "GET":
        try:
            images_data = sql.select("imgURL, label, id", "images", where="verified=0")
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
            return jsonify({"success": False, "error": str(e)}), 500
    elif request.method == "POST":
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No file part"}), 400
    
        file = request.files['file']
    
        if file.filename == '':
            return jsonify({"success": False, "error": "No selected file"}), 400
    
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)  # Save the uploaded file
        
            # Insert image details into the database
            label = request.form.get('label')
            sql.insertImages([{'imgURL': filename, 'label': label}])
        
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
    return send_from_directory(app.static_folder, filename)



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
                "labels": list( map(lambda x: x[0], mod_labals) )
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
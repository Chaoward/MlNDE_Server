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
            return jsonify(labels)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    elif request.method == "POST":  
        try:
            data = request.json
            labels = data.get("labels", [])
            if not labels:
                return jsonify({"success": False, "error": "No labels provided"}), 400
            
            count = sql.insertLabels(labels)    
            return jsonify({"success": True, "message": f"{count} labels inserted successfully"})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500


#===== IMAGES ==================================================
# image objects { id, imgURL, label }
@app.route("/images/unverified", methods=["GET", "POST"])
def handleUnverified():
    if request.method == "GET":
        try:
            images_data = sql.select("*", "images", where="verified=0")
            images = []
            for img_data in images_data:
                img_dict = {
                    "imgURL": img_data[0],
                    "label": img_data[1],
                    "verified": img_data[2],
                    "id": img_data[3]
                }
                images.append(img_dict)
            return jsonify({"images": images})
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
        return jsonify({"models": models})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/model/release", methods=["POST"])
def setRelease():
    try:
        data = request.json
        version_num = data.get("versionNum")

        result = sql.setRelease(version_num)

        if result == 0:
            return jsonify({"success": f"Model {version_num} is now marked as the release version"}), 200
        elif result == 1:
            return jsonify({"error": f"Model {version_num} not found"}), 404
        elif result == -1:
            return jsonify({"error": f"Model {version_num} is already the release version"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
from flask import Flask, send_from_directory, request, jsonify
from Include import sql


app = Flask(__name__)
UPLOAD_FOLDER = './uploads'



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
                return jsonify({"error": "No labels provided"}), 400
            
            count = sql.insertLabels(labels)    
            return jsonify({"success": f"{count} labels inserted successfully"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500


#===== IMAGES ==================================================
# image objects { id, imgURL, label }
@app.route("/images/unverified", methods=["GET", "POST"])
def handleUnverified():
    if request.method == "GET":
        try:
            images = sql.select("*", "images", where="verified=0")
            return jsonify({"images": images})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    elif request.method == "POST":
        try:
            data = request.json
            imgs = data.get("images", [])
            if not imgs:
                return jsonify({"error": "No images provided"}), 400
            
            sql.insertImages(imgs)
            return jsonify({"success": "Images uploaded successfully"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route("/images/verified", methods=["GET", "POST"])
def handleVerified():
    try:
        images = sql.select("*", "images", where="verified=1")
        return jsonify({"images": images})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
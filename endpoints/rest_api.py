#from Include.globals import UNVERIFIED_PATH, VERIFIED_PATH, LABELS_PATH, IMAGE_PATH, readJsonFile, overwriteJsonFile, isAllowedFile
import time
from Include.globals import *
from flask import jsonify, request, Blueprint
from os import path
from werkzeug.utils import secure_filename

rest_web = Blueprint('rest_web', __name__, template_folder='endpoints')

#TODO: version removing test, multi-upload image

########### rest_web ROUTES ####################################################################################

@rest_web.route("/uploadImages", methods=["GET", "POST"])
def uploadImages():
    if request.method == "GET":
        return '''
        <form action="/uploadImages" method="post" enctype="multipart/form-data">
            <label for="file">Choose file:</label>
            <input type="file" name="file" required><br><br>

            <label for="file">Choose file:</label>
            <input type="file" name="file" required><br><br>

            <label for="Label">Label:</label>
            <input type="text" name="Label" required><br><br>

            <label for="confidence">Confidence:</label>
            <input type="number" name="confidence" required><br><br>

            <input type="submit" value="Upload">
        </form>
      '''
    if request.method != "POST":
        return jsonify({"success": False, "error": "Unknown Request Method : \'GET\' & \'POST\' only"})
    if "file" not in request.files and request.files['file'].filename == '':
        return jsonify({"success": False, "error": "Must supply a \'file\' property with a file attached!"})
    
    res = {"success": True, "successCount": 0}
    unverJson = readJsonFile(UNVERIFIED_PATH)
    i = 1
    for file in request.files.getlist('file'):
        if not isAllowedFile(file.filename):
            if "error" not in res:
                res["error"] = "Must be a valid image file extension : " + str(ALLOWED_EXTENSIONS)
            i += 1
            continue
        #save image
        curTime = str(time.time())[-5:] #last 5 digits of the current time in miliseconds
        fileHead, fileExtension = path.splitext( secure_filename(file.filename) )   #splits filename and file extension
        newFileName = f"{fileHead}{curTime}{fileExtension}"
        file.save(path.join(IMAGE_PATH, newFileName ))
        
        #append as new json entry
        unverJson.append({
            "id": newFileName,
            "Label": request.form[f"Label{i}"] if f"Label{i}" in request.form else "",
            "confidence": request.form[f"confidence{i}"] if f"confidence{i}" in request.form else 0,
            "imageUrl": f"images/{newFileName}"
        })

        res["successCount"] += 1
        i += 1
    #save json
    overwriteJsonFile(UNVERIFIED_PATH, unverJson)

    return jsonify(res)



@rest_web.route("/versionHistory")
def versionHistory():
    try:
        return jsonify(readJsonFile(VERSION_PATH))
    except Exception as e:
        print(e)
        return 500



@rest_web.route("/setRelease", methods=['POST'])
def setRelease():
        trgt = request.json["release"]
        versionHistory = readJsonFile(VERSION_PATH)
        #verify version exit
        for i, ver in enumerate(versionHistory["versions"]):
            if ver["version"] == trgt:
                versionHistory["release"]["index"] = i
                versionHistory["release"]["version"] = trgt
                overwriteJsonFile(VERSION_PATH, versionHistory)
                return jsonify({"success": True})
        return jsonify({"success": False})



@rest_web.route("/removeVersion", methods=['POST'])
def removeVersion():
    if request.method != "POST":
        return jsonify({"success": False, "error": "\'POST\' method only!"})
    
    versionHistory = readJsonFile(VERSION_PATH)
    removeList = request.json["removeList"]
    res = {"success": True, "successCount": 0}

    for trgt in removeList:
        if trgt == versionHistory["release"]["version"]:
            res["error"] = "Cannot remove the Release Version, try marking amother version as release then try removing again"
            continue
        for i, ver in versionHistory["versions"]:
            if ver["version"] == trgt:
                res["successCount"] += 1
                versionHistory["versions"].pop(i)
                break

    overwriteJsonFile(VERSION_PATH, versionHistory)
    if res["successCount"] == 0:
        res["success"] = False
    return jsonify(res)
            



@rest_web.route("/web_getUnverfified")
def web_getUnverfified():
    images = readJsonFile(UNVERIFIED_PATH)
    labels = readJsonFile(LABELS_PATH)

    return jsonify({"imageCount": len(images), "labels": labels,  "images": images})



@rest_web.route("/web_verify", methods=['POST'])
def web_verify():
    if not request.is_json or type(request.json) != list:
        return jsonify({"success": False, "error": "[Format Error]: JSON array with objects \{id, imageUrl, Label, coinfidence\}"}), 400
    
    markedList = request.json
    unverified = readJsonFile(UNVERIFIED_PATH)
    verified = readJsonFile(VERIFIED_PATH)

    for img in markedList:
        #search unverified list to find matching id, use index to remove
        for i in range(0, len(unverified)):
            if unverified[i]['id'] != img['id']:
                continue
            unverified.remove(unverified[i])
            verified.append(img)
            break      #breaks search loop
    
    #update all files 
    overwriteJsonFile(UNVERIFIED_PATH, unverified)
    overwriteJsonFile(VERIFIED_PATH, verified)

    return jsonify( {"success": True, "count": len(verified)} )

        


@rest_web.route("/web_addLabels", methods=['POST'])
def web_addLabels():
    if not request.is_json or "labels" not in request.json:
        return jsonify({"success": False, "error": "[Format Error]: JSON with string array 'labels' is needed!"})
    labelsList = readJsonFile(LABELS_PATH)

    res = {"denied": [], "successCount": 0, "success": True}

    for l in request.json["labels"]:
        if l not in labelsList:
            labelsList.append(l)
            res["successCount"] += 1
        else:
            res["denied"].append(l)
    overwriteJsonFile(LABELS_PATH, labelsList)

    return jsonify(res)
    
    
@rest_web.route("/web_getLabels")
def web_getLabels():
    return readJsonFile(LABELS_PATH)
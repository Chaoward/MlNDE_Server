import os
from flask import Flask, request, jsonify, url_for, send_from_directory, redirect
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import json
import random
from flask_cors import CORS
#import requests
import time
import logging
import boto3
#import tensorflow as tf


load_dotenv()

s3_client = boto3.client('s3', aws_access_key_id='AKIAYFWKBKPEVTKRZT6S', aws_secret_access_key='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')


#UPLOAD_FOLDER = './imagebucket/'
UNVERIFIED_BUCKET = './unverifiedbucket/'
API_ENDPOINT = 'https://mt5t6im18f.execute-api.us-west-1.amazonaws.com/dev'
#S3_BUCKET = "https://seniorcapstone.s3.amazonaws.com/"
S3_BUCKET = "seniorcapstone"
VERIFIED_BUCKET = './verifiedbucket/'

OTHER_BUCKET = './otherbucket/'
unverifiedObjectsJSON = './otherbucket/unverifiedObjects.json'
verifiedObjectsJSON = './otherbucket/verifiedObjects.json'
labelsJSON = './otherbucket/labels.json'
MODEL = './demodel'

#app = Flask(__name__)
app = Flask(__name__, static_folder=UNVERIFIED_BUCKET)

CORS(app)

logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.DEBUG)


#===== imports the routes for web =================
from endpoints.rest_api import rest_web
app.register_blueprint(rest_web)
#==================================================


data = []
unverifiedData = []
Labels = []


# model = tf.keras.applications.MobileNetV2(
#     input_shape=None,
#     alpha=1.0,
#     include_top=True,
#     weights="imagenet",
#     input_tensor=None,
#     pooling=None,
#     classes=1000,
#     classifier_activation="softmax"
# )


# # # @app.route('/getModel', methods=['GET'])
# # # def download_model():
# # #     return redirect(url_for('download_bin', filename='model.json'))

# # # @app.route('/model-bin/<path:filename>', methods=['GET'])
# # # def download_bin(filename):
# # #     MODEL = '/path/to/mobilenet_v2_tfjs'
# # #     return send_from_directory(MODEL, filename)


@app.route("/")
def hello_world():
  getInitialData()    
  return x


@app.route("/getUnverifiedXs")
def getUnverifiedXs():
  images = []
  imageCount = 0
  datalabels = []
  for data in unverifiedData:
    images.append({
        "id": data.get("id"),
        "imageUrl": '/images/' + data.get("id"),
        "Label": data.get("Label"),
        "confidence": data.get("confidence"),
    })
    datalabels.append(data.get("Label"))
    imageCount += 1
  response_data = {"imageCount": len(images), "labels": datalabels,  "images": images}
  return jsonify(response_data)

@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory(app.static_folder, filename)

def getInitialData():
  try:
    if os.path.isfile(labelsJSON) and os.path.getsize(labelsJSON) > 0:
      with open(labelsJSON, 'r') as json_file:
        Labels.clear()
        Labels.extend(json.load(json_file))
  except Exception as e:
    app.logger.error(f"An error occurred: {e}")
    return "oh no i messed up"
  try:
    if os.path.isfile(unverifiedObjectsJSON) and os.path.getsize(unverifiedObjectsJSON) > 0:
      with open(unverifiedObjectsJSON, 'r') as json_file:
        unverifiedObjects = json.load(json_file)
        unverifiedData.clear()
        unverifiedData.extend(unverifiedObjects)
    else:
      app.logger.warning(f"File {unverifiedObjectsJSON} does not exist or is empty.")
  except json.JSONDecodeError as e:
   app.logger.error(f"JSON decode error: {e}")
  except Exception as e:
    app.logger.error(f"An error occurred: {e}")
  return unverifiedData

def getTimeTxt():
  timestamp = time.time()
  timestamp_str = str(timestamp)
  last_five_digits = timestamp_str[-5:]
  return last_five_digits


@app.route('/uploadV2', methods=["GET", "POST"])
def uploadV2():
  if request.method == "GET":
    return '''
        <form action="/uploadV2" method="post" enctype="multipart/form-data">
            <label for="file">Choose file:</label>
            <input type="file" name="file" required><br><br>

            <label for="Label">Label:</label>
            <input type="text" name="Label" required><br><br>

            <label for="confidence">Confidence:</label>
            <input type="number" name="confidence" required><br><br>

            <input type="submit" value="Upload">
        </form>
      '''
  elif request.method == "POST":
    print("hello")
    currTime = getTimeTxt()
    print("some")
    file = request.files["file"]
    print("thing")
    original_filename = secure_filename(file.filename)
    print("is")
    file_name, file_extension = os.path.splitext(original_filename)
    print("not")
    filename = f"{file_name}{currTime}{file_extension}"
    print("making")
    filepath = os.path.join(UNVERIFIED_BUCKET, filename)
  #  s3path = f"{S3_BUCKET}{filename}"
    print("okay")
    try:
      file.save(filepath)
      newUnverified = {
        "id": filename,
        "imageUrl": f"{filename}",
        "Label": request.form["Label"],
        "confidence": request.form["confidence"]
      }
      if newUnverified.get("Label") not in Labels:
        addLabelHandler(newUnverified.get("Label"))
      if os.path.isfile(unverifiedObjectsJSON) and os.path.getsize(unverifiedObjectsJSON) > 0:
          with open(unverifiedObjectsJSON, "r") as f:
              unverifiedObjects = json.load(f)
      else:
          unverifiedObjects = []
      unverifiedObjects.append(newUnverified)
      with open(unverifiedObjectsJSON, "w") as f:
          json.dump(unverifiedObjects, f)
      unverifiedData.append(newUnverified)
    except Exception as e:
      app.logger.error(f"Failed to upload: {e}")
      return jsonify({"error": "Failed to upload"}), 500
    return jsonify(unverifiedData), 200


def addLabelHandler(label):
    if label not in Labels:
        Labels.append(label)  # Tentatively add the label
        try:
            if not os.path.isfile(labelsJSON):
                with open(labelsJSON, 'w') as file:
                    json.dump([], file)
            with open(labelsJSON, 'r') as file:
                existing_labels = json.load(file)
            existing_labels.append(label)
            with open(labelsJSON, 'w') as file:
                json.dump(existing_labels, file)   
            return
        except Exception as e:
            if label in Labels:
                Labels.remove(label)
            return
    else:
        return "Label already exists"


@app.get('/seeUnverified')
def seeUnverified():
  return jsonify(unverifiedObjectsJSON)


@app.route('/clearLabels')
def clearLabels():
  Labels.clear()
  with open(labelsJSON, 'w') as file:
      json.dump([], file)
  return jsonify(Labels)

@app.get('/getLabels')
def getLabels():
  return jsonify(Labels)

@app.route('/addLabel', methods=['POST'])
def addLabel():
    print("original labels:")
    print(Labels)
    
    # Adjusted to handle the nested 'labels' key
    data = request.get_json()
    labelArray = data.get('labels', [])
    print(labelArray)
    
    for i in labelArray:
        if i not in Labels:
            addLabelHandler(i)
            # Assuming addLabelHandler modifies the Labels list

    print("new labels:")
    print(Labels)
    return jsonify(Labels)  # Return a JSON response


def removeJSON(bucketname, filename):
    with open(bucketname, 'r+') as file:
        data = json.load(file)
    filtered = [item for item in data if item['id'] != filename]
    with open(bucketname, 'w') as file:
        json.dump(filtered, file)


def updateVerifiedJSON(filename):
    with open(unverifiedObjectsJSON, 'r+') as file:
      app.logger.debug("This will show debug messages and above")
      data = json.load(file)
    newVerified = next((item for item in data if item['id'] == filename), None)
    if not newVerified:
        return "Object not found."
    if os.path.exists(verifiedObjectsJSON):
        with open(verifiedObjectsJSON, 'r+') as file:
            verifiedData = json.load(file)
            verifiedData.append(newVerified)
            file.seek(0)
            json.dump(verifiedData, file, indent=4)
            file.truncate()
    else:
        with open(verifiedObjectsJSON, 'w') as file:
            json.dump([newVerified], file, indent=4)
    return


def moveToVerifiedLocalBucket(filename):
  filepath = os.path.join(UNVERIFIED_BUCKET, filename)
  if os.path.isfile(filepath):
    os.rename(filepath, os.path.join(VERIFIED_BUCKET, filename))
  else:
    print("File not found")
  return

#move to verifiedJSON and VERIFIED_BUCKET, then remove from unverifiedJSOn and UNVERIFIED_BUCKET
@app.route('/verifyObject', methods=["POST"])
def verifyObject():
  imageData = request.get_json()
  filename = imageData['id']
  label = imageData['Label']
  confidence = imageData['confidence']
  moveToVerifiedLocalBucket(filename)
  updateVerifiedJSON(filename)
  removeJSON(unverifiedObjectsJSON, filename)
  return "Success!"


def deleteFromBucket(filename):
    filePath = VERIFIED_BUCKET + filename
    if os.path.isfile(filePath):
        try:
            os.remove(filePath)
            print(f"File {filePath} has been deleted.")
        except Exception as e:
            print(f"An error occurred: {e}")
    else:
        print(f"{filePath} not found.")


@app.route('/updateTrainingData', methods=["POST"])
def send_file_to_s3():
    image_data = request.get_json()
    filename = image_data['id']
    label = image_data['Label']
    confidence = image_data['confidence']
    image_url = image_data['imageUrl']
    file_path = VERIFIED_BUCKET + filename
    try:
        with open(file_path, 'rb') as file:
            s3_client.upload_fileobj(
                Fileobj=file,
                Bucket=S3_BUCKET,
                Key=filename,
                ExtraArgs={
                    "Tagging": f"Label={label}&Confidence={confidence}"
                }
            )
    except FileNotFoundError:
        return "The file was not found.", 404
    except Exception as e:
        return str(e), 500
    removeJSON(verifiedObjectsJSON, filename)
    deleteFromBucket(filename)
#    removeFromLocal(filename, VERIFIED_BUCKET)
#    removeFromJSON(filename, VERIFIED_BUCKET)
    return "File uploaded successfully!", 200


@app.route("/checkModelVersion")
def checkModelVersion():
  return "Current model version#_____"

@app.route("/downloadModel")
def downloadModel():
  return "Downloading model #_____"

@app.route("/approve")
def approve():
  return "Approved"

@app.route("/reject")
def reject():
   return "Rejected"


@app.route("/signupAdmin")
def signupAdmin():
  return "Hey New Admin"


@app.route("/signinAdmin")
def signinAdmin():
  return "Admin signed in"


@app.route("/signoutAdmin")
def signoutAdmin():
  return "Signed out Admin"


@app.route("/trainModel")
def trainModel():
  return "Training"


@app.route("/updateAndArchiveModel")
def updateAndArchiveModel():
  return "New Model Up"


x = getInitialData()
if __name__ == '__main__':
    port = int(os.environ.get('FLASK_RUN_PORT', 2000))
    app.run(port=port, debug=True)


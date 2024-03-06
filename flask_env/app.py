from flask import Flask, send_from_directory

app = Flask(__name__)


# images, labels, models

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

#===== LABELS ==================================================

@app.route("/labels", methods=["GET", "POST"])
def handleLabels():
    pass


#===== IMAGES ==================================================
# image objects { id, imgURL, label }
@app.route("/images/unverified", methods=["GET", "POST"])
def handleUnverified():
    pass

@app.route("/images/verified", methods=["GET", "POST"])
def handleVerified():
    pass

@app.route("/images/<filename>")
def serveImage(filename):
    return send_from_directory(app.static_folder, filename)



#===== MODELS ==================================================

from flask import Flask

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



#===== MODELS ==================================================

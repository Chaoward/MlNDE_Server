import json

DEBUG = True
UNVERIFIED_PATH = './otherbucket/unverifiedObjects.json' if not DEBUG else './otherbucket/debug_unverifed.json'
VERIFIED_PATH = './otherbucket/verifiedObjects.json' if not DEBUG else './otherbucket/debug_verifed.json'
LABELS_PATH = './otherbucket/labels.json' if not DEBUG else './otherbucket/debug_labels.json'
VERSION_PATH = './otherbucket/version_list.json' if not DEBUG else './otherbucket/debug_verisons.json'
IMAGE_PATH = './unverifiedbucket/'

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif"}

def readJsonFile(path):
  with open(path, 'r') as jsonFile:
      data = json.load(jsonFile)
      jsonFile.close()
  return data

def overwriteJsonFile(path, data):
  with open(path, 'w') as jsonFile:
    jsonFile.write( json.dumps(data) )
    jsonFile.close()


def isAllowedFile(fileName):
   return "." in fileName and fileName.split(".")[1] in ALLOWED_EXTENSIONS


###### DEBUG ############################
    
def debug_populateData():
    PATH_UNVER = './otherbucket/unverifiedObjects.json'
    PATH_VER = './otherbucket/verifiedObjects.json'
    PATH_LABEL = './otherbucket/labels.json'
    PATH_VERSION = './otherbucket/version_list.json'

    unver = readJsonFile(PATH_UNVER)
    lab = readJsonFile(PATH_LABEL)
    ver = readJsonFile(PATH_VER)
    version = readJsonFile(PATH_VERSION)

    overwriteJsonFile(UNVERIFIED_PATH, unver)
    overwriteJsonFile(VERIFIED_PATH, ver)
    overwriteJsonFile(LABELS_PATH, lab)
    overwriteJsonFile(VERSION_PATH, version)
if DEBUG: debug_populateData()
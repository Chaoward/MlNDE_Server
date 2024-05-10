# MlNDE Server

The server application for Machine Learning in Network Denied Enviornments(MlNDE) Senior capstone project.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Sponser](#sponsor)

## Overview
The server stands as the main controller both handling machine learning models and its' datasets.
In the case for the MlNDE project, the server controls the fine tuning process and handles the model versions and datasets that go with it.
The server interfaces with a SQLite database that houses the images with their labels, and models with their training information.
RESTful Web API endpoints are provided for both web-client and mobile client to interact with.

### MlNDE Systems
- [Mobile Client](https://github.com/kevinmaravillas/MobileClient/tree/Main)
- [Web Client]()

## Features
- **RESTful Web API**
- **SQLite Interface**
- **MobileNet Model with TensorflowJS Conversion**
- **Test and Debugging Database**

##Installation

###Getting Started
The server is a flask application that can be installed via python virtual enivornment from the requirements.txt.
With that said however, it is recommended to setup the server on a Unix system as a core feature of tensorflowjs conversion is only available on unix as of now.

### 1. Creating Python Virtual Enviornment
First, create a new python venv preferably in the *flask_env* folder.
```sh
py -m venv flask_env
or
python3 -m venv flask_env
```

### 2. Installing Dependencies
After creating the venv, cd into the **bin** directory or **Scripts** on windows and activate the enivornment.
```sh
source activate
or
activate
```
On the terminal you should see (flask_env) or the name of your environment left of the terminal.

Then pip install the requirements file.
```sh
pip install -r requirements.txt
```

### 3. Runnung Flask
```sh
flask run
```

## Sponser
Proudly sponsored by NSIN/ICT USC
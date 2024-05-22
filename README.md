# MlNDE Server

Machine Learning for Network-Denied Environments (MINDE) is a machine learning project aimed at demonstrating the effectiveness of a hybrid approach to distributing software solutions to network-denied environments. The project combines cloud-based servers and web clients with an offline mobile client that can perform image classification and be incrementally fine-tuned.

The server component includes the web client that acts as an UI for the server's functionalities and the server itself which is responsible for fine-tuning and managing the training data.

## Overview
The server stands as the main controller both handling machine learning models and its' datasets.
In the case for the MlNDE project, the server controls the fine tuning process and handles the model versions and datasets that go with it.
The server interfaces with a SQLite database that houses the images with their labels, and models with their training information.
RESTful Web API endpoints are provided for both web-client and mobile client to interact with.

### PowerPoint Demo Slides:
https://docs.google.com/presentation/d/13EFhmbbCMPtfYBnF4iBhyzKesb5ix88vZ7o3OJCPOOM/edit?usp=sharing

### MlNDE Systems
- [Mobile Client](https://github.com/kevinmaravillas/MobileClient/tree/Main)
- [Web Client](https://github.com/Chaoward/Senior-Cap_WebClient)

## Features
- **RESTful Web API**
- **SQLite Interface**
- **MobileNet Model with TensorflowJS Conversion**
- **Test and Debugging Database**

## Installation

### Getting Started
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

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Sponser](#sponser)

## Sponser
Proudly sponsored by NSIN/ICT USC and Cal State LA Senior Capstone

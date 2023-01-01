from flask import Flask, request, render_template, redirect, url_for, jsonify, send_file
import os, shutil
from io import BytesIO
from werkzeug.utils import secure_filename
from demo import RunModel
from PIL import Image
import glob
import base64
from PIL import Image
from flask_cors import CORS
from codecs import encode

path = os.getcwd()
UPLOAD_FOLDER = "/samples/tests"
OUTPUT_FOLDER = "/samples/outputs"
STATIC_FOLDER = "/static"
ALLOWED_EXTENSIONS = set([ 'png', 'jpg', 'jpeg'])
ENCODING = 'utf-8'


app = Flask(__name__, template_folder='templates')
CORS(app)
app.secret_key = "secret key"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = OUTPUT_FOLDER
app.config["STATIC_FOLDER"] = STATIC_FOLDER

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def deleteFile(filename):
    if os.path.exists(filename) and not os.path.isdir(filename) and not os.path.islink(filename):
        os.remove(filename)

# @app.route('/')
# def upload_form():
#     return render_template('demo.html')

@app.route('/uploads', methods=['GET','POST'])
def upload_file():
    params = request.args.to_dict()
    task = params["task"]
    print("Task", task)
    data = request.get_json()
    base64_code = data["img"]
    
    img_data = base64_code.encode()
    content = base64.b64decode(img_data)
    im = Image.open(BytesIO(content))
    mid_path = os.path.join(path, task)
    im.save("./" + task + app.config["UPLOAD_FOLDER"] + "/test.png")
    RunModel(task)
    files = list(filter(os.path.isfile, glob.glob("./" + task + app.config['OUTPUT_FOLDER'] + "/*" )))
    files.sort(key=lambda x: os.path.getmtime(x))
    fileName =  os.path.basename(files[-1])
    output = path + "/" + task + app.config['OUTPUT_FOLDER'] + "/" + fileName   
    img = Image.open(output)        
    with open(output, "rb") as img_file:
        base64str = base64.b64encode(img_file.read()).decode(ENCODING)

        return jsonify({
        "message": "success",
        "size": [img.width, img.height],
        "format": img.format,
        'img': base64str
    })
    return "Ok"

@app.route('/downloads', methods=['GET'])
def uploaded_file():
    params = request.args.to_dict()
    task = params["task"]
    files = list(filter(os.path.isfile, glob.glob("./" + task + app.config['OUTPUT_FOLDER'] + "/*" )))
    files.sort(key=lambda x: os.path.getmtime(x))
    fileName =  os.path.basename(files[-1])

    file_path = path + "/" + app.config['STATIC_FOLDER'] + "/" + fileName
    output = path + "/" + task + app.config['OUTPUT_FOLDER'] + "/" + fileName
    img = Image.open(file_path)
    with open(file_path, "rb") as img_file:
        base64str = base64.b64encode(img_file.read()).decode(ENCODING)
        print("Encoded img", base64str)

        return jsonify({
        "message": "success",
        "size": [img.width, img.height],
        "format": img.format,
        'img': base64str
    })

    return 'Error'


   




if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
from flask import Flask, render_template, jsonify, request, send_file
from pathlib import Path
import psutil
import json
import os

folders = []

with open('dados.json', 'r', encoding="UTF-8") as file:
    temp_file = json.load(file)
    folders = temp_file['folders']

app = Flask(__name__)

@app.route("/")
def verify():
    return render_template('login.html')

@app.route("/home")
def home():
    return render_template('home.html')
# --------------------------------------- TRIGGER DISK LISTING ------------------------------------------
@app.route("/disc-listing")
def disc_listing():

    disks = []
    partitions = psutil.disk_partitions()

    for part in partitions:
        try:
            usage = psutil.disk_usage(part.mountpoint)
            free = round(usage.free / (1024 ** 3), 2)
            total = round(usage.total / (1024 ** 3), 2)
            
            disks.append({
                'name': part.device,
                'path': part.mountpoint,
                'free': f'{free} GB livres',
                'total': f'{total} GB total'
            })

        except:
            continue

    return jsonify(disks)

# ------------------------------------ TRIGGER CONTENT REQUEST ------------------------------------------
# RESPONSÁVEL POR DEVOLVER CONTEÚDO DE UM DISCO
@app.route("/trigger-content-request", methods=['POST'])
def trigger_content_request():
    requested_data = request.get_json()

    path = Path(requested_data.get("path"))
    obj_list = path.iterdir()

    place_holder = []

    for i in obj_list:
        if i.is_dir() and i.name in folders:
            continue
        else:
            place_holder.append(i)

    data = list(map(
        lambda item: 
            {   
                "name": item.name,
                "id": str(item.resolve()),
                "type": "folder" if item.is_dir() else item.suffix,
            },
            place_holder
        ))
    
    return jsonify(data)

# ------------------------------------ TRIGGER PICTURE REQUEST ------------------------------------------ 
@app.route("/request-picture", methods=['GET'])
def picture_request():
    requested_path = request.args.get("path")

    return send_file(requested_path, as_attachment=True)

# -------------------------------------- TRIGGER UPLOAD FILE --------------------------------------------
@app.route("/trigger-upload-file", methods=['POST'])
def upload_file():
    data_list = request.files.getlist("data")
    path = request.form.get('path')

    for item in data_list:
        item.save(f"{path}/{item.filename}")

    return jsonify("nenhum erro encontrado!")

# --------------------------------------- TRIGGER MAKE DIR ----------------------------------------------
@app.route("/trigger-make-dir", methods=["POST"])
def foo():
    name_dir = request.form.get("name_dir")
    curr_dir = request.form.get("curr_dir")

    full_path = f"{curr_dir}/{name_dir}"

    try:
        os.mkdir(full_path)
        return jsonify("no errors were found dyring the directory creation")
    except Exception as e:
        return jsonify(e)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

'''
SUGESTÃO
- Tenho a impressão de que eu consigo melhorar meu código 
'''
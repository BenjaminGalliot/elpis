import os
from pathlib import Path
from flask import Blueprint, redirect, request, url_for, escape
from werkzeug.utils import secure_filename
from ..blueprint import Blueprint
from ..paths import CURRENT_MODEL_DIR
import json

bp = Blueprint("transcription", __name__, url_prefix="/transcription")


@bp.route("/name", methods=['GET', 'POST'])
def name():
    print(request.json['name'])
    file_path = os.path.join(CURRENT_MODEL_DIR, 'name.txt')
    if request.method == 'POST':
        # update the state name
        with open(file_path, 'w') as fout:
            fout.write(request.json['name'])

    # return the state
    with open(file_path, 'r') as fin:
        return f'{{ "name": "{fin.read()}" }}'


@bp.route("/date", methods=['GET', 'POST'])
def date():
    file_path = os.path.join(CURRENT_MODEL_DIR, 'date.txt')
    if request.method == 'POST':
        # update the state name
        with open(file_path, 'w') as fout:
            fout.write(request.json['date'])

    # return the state
    with open(file_path, 'r') as fin:
        return f'{{ "date": "{fin.read()}" }}'


@bp.route("/usedModelName", methods=['GET', 'POST'])
def usedModelName():
    file_path = os.path.join(CURRENT_MODEL_DIR, 'usedModelName.txt')
    if request.method == 'POST':
        # update the state name
        with open(file_path, 'w') as fout:
            fout.write(request.json['usedModelName'])

    # return the state
    with open(file_path, 'r') as fin:
        return f'{{ "usedModelName": "{fin.read()}" }}'

@bp.route("/results", methods=['GET', 'POST'])
def results():
    file_path = os.path.join(CURRENT_MODEL_DIR, 'results.txt')
    if request.method == 'POST':
        # update the state name
        with open(file_path, 'w') as fout:
            fout.write(request.json['results'])

    # return the state
    with open(file_path, 'r') as fin:
        return f'{{ "results": "{fin.read()}" }}'

@bp.route("/audio", methods=['GET', 'POST'])
def audio():
    # setup the path
    path = os.path.join(CURRENT_MODEL_DIR, 'current_transcription')
    if not os.path.exists(path):
        os.mkdir(path)

    # handle incoming data
    if request.method == 'POST':

        file = request.files['file']
        file_path = os.path.join(CURRENT_MODEL_DIR, file.filename)
        print(f'file name: {file.filename}')

        with open(file_path, 'wb') as fout:
            fout.write(file.read())
            fout.close()

    return file.filename

import os
from pathlib import Path
from flask import Blueprint, redirect, request, url_for, escape
from werkzeug.utils import secure_filename
from ..blueprint import Blueprint
from . import comp
from ..paths import CURRENT_MODEL_DIR

bp = Blueprint("model", __name__, url_prefix="/model")
bp.register_blueprint(comp.bp)


@bp.route("/new")
def new():
    return '{"status": "new model created"}'

@bp.route("/name", methods=['GET', 'POST'])
def name():
    file_path = os.path.join(CURRENT_MODEL_DIR, 'name.txt')

    if request.method == 'POST':
        # update the state name
        with open(file_path, 'w') as fout:
            fout.write(request.json['name'])
    
    # return the state
    with open(file_path, 'r') as fin:
        return f'{{ "name": "{fin.read()}" }}'
    
@bp.route("/date")
def date():
    return ''

@bp.route("/transcription-files")
def transcription_files():
    # setup the path
    path = os.path.join(CURRENT_MODEL_DIR, 'data')
    if not os.path.exists(path):
        os.mkdir(path)

    # handle incoming data
    if request.method == 'POST':
        print(f'Trans_files req: {request.json}')

    # return state update
    return f'{os.listdir(path)}'

@bp.route("/audio")
def audio():
    return ''

@bp.route("/transcription")
def transcription():
    return ''

@bp.route("/additionalWords")
def additionalWord():
    return ''

@bp.route("/pronunciation")
def pronunciation():
    return ''

@bp.route("/settings")
def settings():
    return ''



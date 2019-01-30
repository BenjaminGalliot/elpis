import os
from pathlib import Path
from flask import Blueprint, redirect, request, url_for, escape
from werkzeug.utils import secure_filename

ELPIS_ROOT_DIR = os.getcwd()
UPLOAD_FOLDER = os.path.join(ELPIS_ROOT_DIR, "uploaded_files")
ALLOWED_EXTENSIONS = {'wav', 'eaf', 'trs', 'wordlist'}
bp = Blueprint("corpus", __name__, url_prefix="/corpus")


def allowed_file(filename):
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def do():
    pass



""" 
Process incoming file
"""
def route_file_post():
    # file = request.files['file']
    uploaded_files = request.files.getlist("file[]")
    for file in uploaded_files:
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            continue
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            # return redirect(url_for('corpus.wav',
                                    # filename=filename))
    return escape(repr(uploaded_files))



"""
Return a list of all files of filetype
"""
def route_file_get(filetype):
    return '''<form method="POST" enctype="multipart/form-data" action="/corpus/">''' + filetype + '''
                <input type="file" name="file[]" multiple="">
                    <input type="submit" value="add">
                    </form>'''



@bp.route("/wav", methods=("GET", "POST"))
def wav():
    if request.method == "POST":
        # Process incoming wav file
        # file = request.files['file']
        route_post()
        return 200
    elif request.method == "GET":
        # Return a list of all wav files
        route_get('''wav''')
        return 200
        


@bp.route("/elan", methods=("GET", "POST"))
def elan():
    if request.method == "POST":
        # Process incoming elan file
        route_file_post()
        return 200
    elif request.method == "GET":
        # Return a list of all elan files
        route_file_get(eaf)
        return 200


@bp.route("/trs", methods=("GET", "POST"))
def trs():
    if request.method == "POST":
        # Process incoming trs file
        route_file_post()
        return 200
    elif request.method == "GET":
        # Return a list of all trs files
        route_file_get(trs)
        return 200


@bp.route("/wordlist", methods=("GET", "POST"))
def wordlist():
    if request.method == "POST":
        # Process incoming wordlist file
        route_file_post()
        return 200
    elif request.method == "GET":
        # Return current list of words
        route_file_get(wordlist)
        return 200

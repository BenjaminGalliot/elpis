import os
from pathlib import Path
from flask import Blueprint, redirect, request, url_for, escape
from werkzeug.utils import secure_filename
from ..blueprint import Blueprint
from ..paths import CURRENT_MODEL_DIR
import json
import subprocess
from .kaldi import bp as parent_bp
from flask import current_app as app, jsonify
from ..kaldi.interface import KaldiInterface
from ..kaldi.dataset import Dataset

bp = Blueprint("databundle", __name__, url_prefix="/databundle")
bp.register_blueprint(parent_bp)


@bp.route("/new")
def new():
    kaldi: KaldiInterface = app.config['INTERFACE']
    ds = kaldi.new_dataset(request.values.get("name"))
    app.config['CURRENT_DATABUNDLE'] = ds
    return jsonify({
        "status": "ok",
        "message": f"new data bundle created called {ds.name}",
        "data": ds.config._load()
    })

@bp.route("/list")
def list_existing():
    kaldi: KaldiInterface = app.config['INTERFACE']
    return jsonify({
        "status": "ok",
        "message": "",
        "data": kaldi.list_datasets()
    })





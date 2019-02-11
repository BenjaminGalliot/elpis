import pytest
import os
import shutil
import hashlib
from .. import paths
from . import model, KaldiError

def _clear_models_dir():
    # empty the models directory
    if os.path.exists(paths.MODELS_DIR):
        shutil.rmtree(paths.MODELS_DIR)
    os.mkdir(paths.MODELS_DIR)

def _clear_model_dir():
    # empty the current model directory
    if os.path.exists(paths.CURRENT_MODEL_DIR):
        shutil.rmtree(paths.CURRENT_MODEL_DIR)
    os.mkdir(paths.CURRENT_MODEL_DIR)

def test_get_list():
    _clear_models_dir()
    # add stub models
    os.mkdir(paths.MODELS_DIR + '/m1')
    with open(paths.MODELS_DIR + '/m1/name.txt', 'w') as fout:
        fout.write('carlos')
    os.mkdir(paths.MODELS_DIR + '/m2')
    with open(paths.MODELS_DIR + '/m2/name.txt', 'w') as fout:
        fout.write('dallis')
    os.mkdir(paths.MODELS_DIR + '/m3')
    with open(paths.MODELS_DIR + '/m3/name.txt', 'w') as fout:
        fout.write('other nic')
    # Test the results
    names = model.get_list()
    assert 'carlos' in names
    assert 'other nic' in names
    assert 'dallis' in names

def test_new():
    _clear_model_dir()
    model.new('daffy duck')
    with open(f'{paths.CURRENT_MODEL_DIR}/name.txt', 'r') as fin:
        name = fin.read()
    assert name == 'daffy duck'
    assert os.path.exists(f'{paths.CURRENT_MODEL_DIR}/date.txt')
    assert os.path.exists(f'{paths.CURRENT_MODEL_DIR}/hash.txt')
    

def test_new_model_already_exists():
    _clear_models_dir()
    _clear_model_dir()
    os.mkdir(paths.MODELS_DIR + '/m')
    with open(paths.MODELS_DIR + '/m/name.txt', 'w') as fout:
        fout.write('bugs bunny')
    with pytest.raises(KaldiError) as error:
        model.new('bugs bunny')
    assert 'model already exists with the name: \'bugs bunny\'' == str(error.value)

def test_new_invalid_name():
    _clear_model_dir()
    with pytest.raises(KaldiError) as error:
        model.new('')
    assert 'invalid model name: \'\'' == str(error.value)

import os
import hashlib
import time
import shutil
from typing import List

from . import step, KaldiError
from .. import paths

def _sync_to_kaldi():
    """Copy files from local model to kaldi helpers"""
    pass

def _sync_to_local():
    """Copy files from kaldi helpers to local model"""
    pass

def get_list() -> List[str]:
    """Returns the list of model names that have been saved. Models are saved
    in the paths.MODELS_DIR directory.
    """
    names = []
    for model_dir in os.listdir(paths.MODELS_DIR):
        with open(f'{paths.MODELS_DIR}/{model_dir}/name.txt', 'r') as fin:
            names.append(fin.read())
    return names

def _get_status(directory):
    def no_model():
        return not os.path.exists(directory) or (
            len(os.listdir(directory)) == 0
        )
    def complete_model():
        return sorted(os.listdir(directory)) == sorted([
                'data',
                'config',
                'name.txt',
                'date.txt',
                'hash.txt',
            ]) and (
                len(os.listdir(f'{directory}/data')) != 0 and sorted([
                    'letter_to_sound.txt',
                    'optional_silence.txt',
                    'silence_phones.txt'
                ]) == sorted(os.listdir(f'{directory}/config'))
            )
    if no_model(): return 'No Model'
    elif not complete_model(): return 'Incomplete Model'
    else: return 'Untrained Model'

def get_status():
    # TODO: unimplemented
    return None

def get_info_of(name):
    # TODO: unimplemented
    return {}

@step()
def new(name):
    """
    Clears the current model and creates a new model.

    Before running this command, the current_model/ directory could be in any
    state. On running this command, the contents is deleted so that a new 
    model can take its place.

    The filesystem state after running this command is:
    current_model/
        name.txt
        date.txt
        hash.txt
    
    :raise KaldiError: if there is an attempts to create a model that already
    exists or if the name is invalid.
    """
    if name in get_list():
        raise KaldiError(f'model already exists with the name: \'{name}\'')
    if name == '':
        raise KaldiError('invalid model name: \'\'')
    if os.path.exists(paths.CURRENT_MODEL_DIR):
        shutil.rmtree(paths.CURRENT_MODEL_DIR)
    os.mkdir(paths.CURRENT_MODEL_DIR)
    # write state files
    date = time.time()
    with open(f'{paths.CURRENT_MODEL_DIR}/name.txt', 'w') as fout:
        fout.write(name)
    with open(f'{paths.CURRENT_MODEL_DIR}/date.txt', 'w') as fout:
        fout.write(str(date))
    with open(f'{paths.CURRENT_MODEL_DIR}/hash.txt', 'w') as fout:
        hashname = hashlib.md5(bytes(str(date), 'utf-8')).hexdigest()
        fout.write(hashname)
    # TODO sync to the kaldi helpers directory

def get_name():
    # TODO: unimplemented
    return None

def get_date():
    return None

def get_hash():
    return None

@step(deps=[new])
def load_transcription_files(file_pairs, overwrite=False):
    """
    :param file_pairs: is a list of paired tuples of tuples... file_pairs is
    a list of (FILE, FILE), while FILE is a tuple representing a file by
    (filename, filecontent).
    :param overwrite: if true, and a file already exists, then it'll be
    overwritten, otherwise, it will just be skipped.
    :raise KaldiError: if file names in the pair don't match.
    """
    # TODO: unimplemented
    return None

def get_transcription_files():
    """
    Get a list of files 
    """
    # TODO: unimplemented
    return None

@step(deps=[load_transcription_files])
def generate_word_list():
    # TODO: unimplemented
    return ''

@step(deps=[load_transcription_files])
def load_pronunciation_dictionary(filecontent):
    # TODO: unimplemented
    return ''

def get_pronunciation_dictionary():
    """
    :return: None if the pronunciation dictionary has yet to be loaded,
    otherwise, the content of the pronunciation dictionary is returned
    """
    # TODO: unimplemented
    return None

@step(deps=[new])
def load_settings(file):
    # TODO: unimplemented
    return ''

def get_settings():
    # TODO: unimplemented
    return None

@step(deps=[load_settings, generate_word_list, load_pronunciation_dictionary])
def train():
    # TODO: unimplemented
    return ''

def load(name):
    # TODO: unimplemented
    return None

def save():
    # TODO: unimplemented
    return None

def get_training_results():
    # TODO: unimplemented
    return None
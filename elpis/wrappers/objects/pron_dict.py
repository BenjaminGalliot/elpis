import json
import shutil
import glob
import os
import threading

from pathlib import Path
from io import BufferedIOBase
from multiprocessing.dummy import Pool
from shutil import move

from elpis.wrappers.objects.dataset import Dataset
from elpis.wrappers.objects.fsobject import FSObject
from elpis.wrappers.objects.path_structure import existing_attributes, ensure_paths_exist
from elpis.wrappers.input.make_prn_dict import generate_pronunciation_dictionary


class PronDict(FSObject):

    # The configuration settings stored in the file below.
    _config_file = 'pron_dict.json'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dataset: Dataset = None
        self.config['dataset'] = None  # dataset hash has not been linked # TODO: change 'dataset' to 'dataset_name'
        self.l2s_path = self.path.joinpath('l2s.txt')
        self.lexicon_txt_path = self.path.joinpath('lexicon.txt') #TODO change to lexicon_txt_path
        self.config['l2s'] = False  # file has not been uploaded
        self.config['lexicon'] = False  # file has not been generated

    @classmethod
    def load(cls, base_path: Path):
        self = super().load(base_path)
        self.l2s_path = self.path.joinpath('l2s.txt')
        self.lexicon_txt_path = self.path.joinpath('lexicon.txt')
        self.dataset = None
        return self

    @property
    def state(self):
        """
        An API fiendly state representation of the object.

        Invarient: The returned object can be converted to JSON using json.load(...).

        :returns: the objects state.
        """
        return {
            'name': self.config['name'],
            'hash': self.config['hash'],
            'date': self.config['date'],
            'l2s': self.config['l2s'],
            'lexicon': self.config['lexicon'],
            'dataset': self.config['dataset']
        }

    def link(self, dataset: Dataset):
        self.dataset = dataset
        self.config['dataset'] = dataset.name

    def set_l2s_path(self, path: Path):
        path = Path(path)
        with path.open(mode='rb') as fin:
            self.set_l2s_fp(fin)

    def set_l2s_fp(self, file: BufferedIOBase):
        self.set_l2s_content(file.read())
        self.config['l2s'] = True

    def set_l2s_content(self, content: str):
        # TODO: this function uses parameter str, and must be bytes or UTF-16
        with self.l2s_path.open(mode='wb') as fout:
            fout.write(content)
        self.config['l2s'] = True

    def get_l2s_content(self):
        try:
            with self.l2s_path.open(mode='r') as fin:
                return fin.read()
        except FileNotFoundError:
            return False


    def get_l2s(self):
        with self.l2s_path.open(mode='r') as fin:
            return fin.read()


    def generate_lexicon(self):
        # task make-prn-dict
        # TODO this file needs to be reflected in kaldi_data_local_dict
        if self.dataset == None:
            raise RuntimeError('must link dataset before generateing lexicon')
        if self.dataset.has_been_processed == False:
            raise RuntimeError('must process dataset before generateing lexicon')
        if self.config['l2s'] == False:
            raise RuntimeError('must set letters to sound before generating lexicon')
        generate_pronunciation_dictionary(word_list=f'{self.dataset.pathto.word_list_txt}',
                                          pronunciation_dictionary=f'{self.lexicon_txt_path}',
                                          config_file=f'{self.l2s_path}')
        self.config['lexicon'] = True
    # @property
    # def lexicon(self):
    #     with self.lexicon_txt_path.open(mode='rb') as fin:
    #         return fin.read()


    def get_lexicon_content(self) -> bytes:
        try:
            with self.lexicon_txt_path.open(mode='rb') as fin:
                return fin.read()
        except FileNotFoundError:
            return None


    def save_lexicon(self, bytestring):
        # open pron dict file
        # write lexicon text to file
        with self.lexicon_txt_path.open(mode='wb') as fout:
            fout.write(bytestring)
        self.config['lexicon'] = True

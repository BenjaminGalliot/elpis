from pathlib import Path
from elpis.engines.common.objects.dataset import Dataset
from elpis.engines.common.objects.fsobject import FSObject
from elpis.objects.path_structure import KaldiPathStructure


class ModelFiles(object):
    def __init__(self, basepath: Path):
        self.kaldi = KaldiPathStructure(basepath)


class Model(FSObject):  # TODO not thread safe
    _config_file = 'model.json'
    _links = {**FSObject._links, **{"dataset": Dataset}}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dataset: Dataset = None
        self.config['dataset_name'] = None  # dataset hash has not been linked
        self.config['status'] = 'untrained'
        self.status = 'untrained'

    @classmethod
    def load(cls, base_path: Path):
        self = super().load(base_path)
        self.dataset = None
        return self

    @property
    def status(self):
        return self.config['status']

    @status.setter
    def status(self, value: str):
        self.config['status'] = value


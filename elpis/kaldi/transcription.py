from . import hasher
from pathlib import Path
from .session import Session
from .resample import resample
from .command import run
from io import BufferedIOBase
import os
import shutil
import subprocess


class Transcription(object):
    def __init__(self, basepath: Path, name:str, sesson: Session, model):
        super().__init__()
        self.name: str = name
        self.hash: str = hasher.new()
        self.path: Path = basepath.joinpath(self.hash)
        self.path.mkdir(parents=True, exist_ok=True)
        self.audio_file_path = self.path.joinpath('audio.wav')
        self.model = model

    def transcribe(self, audio):
        # copy audio to the tmp folder for resampling
        tmp_path = Path(f'/tmp/{self.hash}')
        tmp_path.mkdir(parents=True, exist_ok=True)
        tmp_file_path = tmp_path.joinpath('original.wav')
        if isinstance(audio, Path) or isinstance(audio, str):
            shutil.copy(f'{audio}', f'{tmp_path}/original.wav')
        elif isinstance(audio, BufferedIOBase):
            with tmp_file_path.open(mode='wb') as fout:
                fout.write(audio.read())
        # resample the audio fie
        resample(tmp_file_path, self.path.joinpath('audio.wav'))
        # cook the infer file generator
        # TODO fix below
        with open('/kaldi-helpers/kaldi_helpers/inference_scripts/generate-infer-files.sh', 'r') as fin:
            generator: str = fin.read()
        generator = generator.replace('working_dir/input/infer', f'{self.path}')
        generator = generator.replace('working_dir/input/output/kaldi/data/test', f"{self.model.path.joinpath('kaldi', 'data', 'test')}")
        generator = generator.replace('working_dir/input/output/kaldi/data/infer', f"{self.model.path.joinpath('kaldi', 'data', 'infer')}")
        generator_file_path = self.path.joinpath('gen-infer-files.sh')
        with generator_file_path.open(mode='w') as fout:
            fout.write(generator)
        run(f'chmod +x {generator_file_path}')
        run(f'{generator_file_path}')
        shutil.copytree(f'{self.path}', f"{self.model.path.joinpath('kaldi', 'data', 'infer')}")
        shutil.copy(f'{self.audio_file_path}', f"{self.model.path.joinpath('kaldi', 'audio.wav')}")
        p = subprocess.run('sh /kaldi-helpers/kaldi_helpers/inference_scripts/gmm-decode.sh'.split(), cwd=f'{self.model.path.joinpath("kaldi")}')

        # _transcribe:
        #     - python3.6 {{ .HELPERS_PATH }}/{{ .INPUT_SCRIPTS_PATH }}/resample_audio.py -c {{ .INFER_PATH }}
        #     - sh {{ .HELPERS_PATH }}/{{ .INFERENCE_SCRIPTS_PATH }}/generate-infer-files.sh
        #     - rm -rf {{ .KALDI_OUTPUT_PATH }}/kaldi/data/infer
        #     - cp -R working_dir/input/infer {{ .KALDI_OUTPUT_PATH }}/kaldi/data/infer
        #     - cp working_dir/input/infer/audio.wav {{ .KALDI_OUTPUT_PATH }}/kaldi/audio.wav
        #     - task infer
        #     - task copy-infer-results
    def results(self):
        return "no results yet"

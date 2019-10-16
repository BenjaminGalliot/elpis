#!/usr/bin/python3

"""
Copyright: University of Queensland, 2019
Contributors:
              Nicholas Buckeridge - (The University of Queensland, 2019)
"""

import os
import importlib
import json
import shutil
import threading

from inspect import signature
from multiprocessing.dummy import Pool
from typing import List, Dict, Callable
from pathlib import Path

from elpis.wrappers.input.resample_audio import process_item

# A json_str is the same as a normal string except must always be deserializable into JSON as an invariant.
json_str = str

AnnotationFunction = Callable[[Dict], None]
AddAudioFunction = Callable[[str, str], None]
FileImporterType = Callable[[List[str], Dict, AnnotationFunction], None]
DirImporterType = Callable[[str, Dict, AnnotationFunction, AddAudioFunction], None]
AudioProcessingFunction = Callable[[List[str], Dict, AddAudioFunction], None]

CtxChangeCallback = Callable[[dict, dict], None]


PathList = List[str] # a list of paths to file
FilteredPathList = Dict[str, PathList]

# WARNING: All other python files in this directory with the exception of this one should be a data transformer.

# Note: An instanciated data transformer can be used for on multiple datasets so a data transformer can be told to clean up it's variables for the next run by calling the clean_up function. can use @dt.on_cleanup to attach anything to this process.

# Audio and Annotaion data
# ========================
# Data transformers when importing a collection extract annotation data from a
# given transcription data structure and attach it to an ID. An ID is a name
# that identifies the audio resource. IDs are unique and are derived from the
# names of the audio files without the extention. Every ID will then start with
# en empty list of annotations. Import functions can then make calls to a
# callback (add_annotation) that appends an anotaion dictiornary to the IDs
# list.

class Functional:
    """
    Support class to keep a reference to an object containing a function. Use
    this object when a function could be changed after it's assignment.
    """
    def __init__(self, f):
        """Alwyas have a default function."""
        self._callback = f

    def __call__(self, *args, **kwargs):
        """Calling this class called the contained function."""
        self._callback(*args, **kwargs)

    @property
    def callback(self):
        """Access the function directly."""
        return self._callback

    @callback.setter
    def callback(self, f):
        """Assign a new function to this object."""
        self._callback = f


class DataTransformer:
    """
    A data transformer handles the importing and exporting of data from the
    Elpis pipeline system.
    """

    def __init__(self, context: Dict, collection_path: str, resampled_path: str, temporary_directory_path: str, importing_function: DirImporterType, audio_processing_callback: AudioProcessingFunction, context_change_callback: CtxChangeCallback):
        # self._context: Dict = context TODO: remove this line
        self._import_context: Dict = context
        self._export_context: Dict = context
        self._context_change_callback = context_change_callback

        # Path to directory containing original audio and transcription files
        self._collection_path: str = collection_path # TODO: Remove this line

        # Path to directory containing resampled audio files
        self._resampled_path: str = resampled_path

        # Callback to transcription data importing function, requires contents
        # directoru, contect and add_annotation parameters.
        self._importing_function: DirImporterType = importing_function

        # Target media audio file extention
        self._audio_ext_filter: str = 'wav' # default to wav

        # Callback to audio importing function.
        self._audio_processing_callback: AudioProcessingFunction = audio_processing_callback

        # annotation_store: collection of (ID -> List[annotaion obj]) pairs
        self._annotation_store = {}
        # audio_store: collection of (ID -> audio_file_path) pairs
        self._audio_store = {}

    def process(self):
        self._importing_function(self, self._import_context)





class DataTransformerAbstractFactory:
    """
    This Abstract Factory class instanciates DataTransformer classes on a call
    to build(). All other functions are decotators for creating methods for
    the DataTransformer being built.
    """


    # Class variable _transformer_factories contains a mapping from a
    # transformer name to the unique object factory for that transformer. As
    # per dictionary rules, tranformers must be uniquely named.
    _transformer_factories = {}

    def __init__(self, name: str):
        """
        Construct a new DataTransformerAbstractFactory. Normally one of these
        objects are made per import/export format type.

        :raises:
            ValueError: if DataTransformerAbstractFactory with name already
                exists.
        """

        self._audio_extention = 'wav'
        self._default_context_already_set = False

        # Ensure only one name exists per DataTransformerAbstractFactory
        if name in self._transformer_factories:
            raise ValueError(f'DataTransformerAbstractFactory with name "{name}" already exists')
        self._transformer_factories[name] = self

        # Context proxy variables to copy to the instanciated class
        self._import_context = {}
        self._export_context = {}

        # Concrete import function collection
        self._import_extension_callbacks: Dict[str, FileImporterType] = {}
        self._import_directory_callback: Callable = None

        self._functions_using_tempdir: List[Functional] = []
        self._attributes = {}
    
    def set_audio_extention(self, ext: str):
        """
        Setter for the audio extention that will be used to scan for audio
        files.

        :param ext: the extention part of the file.
        """
        self._audio_extention = ext
        return

    def set_default_context(self, context: dict):
        """
        Sets the default import and export context.

        :raises:
            TypeError: if the context parameter is not JSONable.
            RuntimeError: if either the import or export context already contains values.
        """
        if self._import_context != {}:
            raise RuntimeError('import context contains settings. Set defautl context at start of script')
        elif self._export_context != {}:
            raise RuntimeError('export context contains settings. Set defautl context at start of script')
        elif self._default_context_already_set:
            raise RuntimeError('Have multiple calls to set_default_context, only allowed one')
        self._default_context_already_set = True

        # perform deep copy and ensures JSONability
        jcontext = json.dumps(context)
        self._import_context = json.loads(jcontext)
        self._export_context = json.loads(jcontext)
        return

    def get_audio_extention(self) -> str:
        return self._audio_extention

    def import_files(self, extention: str):
        """
        Python Decorator with single argument (extention).

        Store the decorated function as a callback to process files with the
        given extention. The parameter to the decorator is the file extention.
        The decorated function (f) should always have three parameters, being:
            1. List containing the file paths of all the files in the import
                directory with the specified extention.
            2. A dictionary context variable that can be used to access
                specialised settings.
            3. A callback to add annotaion data to audio files.
        
        This decorator is indended for the (audio file, transcription file)
        unique distinct pair usecase.
        
        The callback is used either when the DataTransformer process() function
        is called or the if the function is called directly from the
        DataTransformer object. If called directly, then only the file_paths
        argument should be passed to the function as the DataTransformer
        automatically passes context and the add_annotation callback.

        This decorator cannot be used with the import_directory decorator.

        :param extention: extention to map the callback (decorated function) to.
        :return: a python decorator
        :raises:
            RuntimeError: if import_directory is already used.
            RuntimeError: if the extention is aleady registers.
            RuntimeError: if the decorated function name is repeated.
            RuntimeError: if the decorated function does not have three parameters.
        """
        if self._import_directory_callback is not None:
            raise RuntimeError('import_directory used, therefore cannot use import_files')
        elif extention in self._import_extension_callbacks:
            raise RuntimeError(f'"{extention}" has already been registered with import_files decorator')

        def decorator(f: Callable):
            if f.__name__ in self._attributes:
                raise RuntimeError('bad function name. Already used')
            if f.__name__ in dir(DataTransformer):
                raise RuntimeError('bad function name. Name is attribute of DataTransformer')

            sig = signature(f)
            if len(sig.parameters) != 3:
                raise RuntimeError(f'function "{f.__name__}" must have three parameters, currently has f{len(sig.parameters)}')

            # Store the closure by file extention
            self._import_extension_callbacks[extention] = f
            # Store attribute
            self._attributes[f.__name__] = f
            return f
        return decorator
    
    def import_directory(self, f):
        """
        Python Decorator (no arguments)

        Store the decorated function as a callback to process files of the
        given type. The decorated function (f) should always have four
        parameters, being:
            1. Directory path containing files/directories of interest.
            2. A Dictionary context variable that can be used to access
                specialised settings.
            3. A callback to add annotaion data to audio files.
            4. A callback to add audio files.
        
        The callback is used either when the DataTransformer process() function
        is called or the if the function is called directly from the
        DataTransformer object.

        This decorator cannot be used with the import_file decorator.

        :return: a python decorator
        :raises:
            RuntimeError: if the callback has already been specified.
            RuntimeError: if import_files had already been specified.
        """
        if self._import_directory_callback is not None:
            raise RuntimeError('import_directory already specified')
        if len(self._import_extension_callbacks) != 0:
            raise RuntimeError('import_files used, therefore cannot use import_directory')
        if f.__name__ in self._attributes:
            raise RuntimeError('bad function name. Already used')
        if f.__name__ in dir(DataTransformer):
            raise RuntimeError('bad function name. Name is attribute of DataTransformer')

        sig = signature(f)
        if len(sig.parameters) != 4:
            raise RuntimeError(f'function "{f.__name__}" must have four parameters, currently has f{len(sig.parameters)}')
        
        # Store the closure by file extention
        self._import_directory_callback = f
        self._attributes[f.__name__] = f
        return f

    def make_default_context(self, ctx: Dict):
        """
        Define a default context for the data transformer.

        :param ctx: dictionary of jsonable values.
        """
        self._default_context = json.dumps(ctx)
        return
    
    def audio_media_extention(self, extention: str):
        """
        Target media file type to process by file extention.

        :param extention: Extention part of file name.
        """
        self._audio_ext_filter = extention
        return

    def add_setting(self, figure, out, what, params):
        """"""
        pass

    def replace_reprocess_audio(self, f):
        """"""
        pass

    def export_files(self, f):
        """"""
        pass

    def export_directory(self, f):
        """"""
        pass

    def use_temporary_directory(self, f):
        """
        Python decotator.

        Postpends an argument containing the path to a temporary directory (before kwargs).

        :param f: function to be decorated.
        :return: Callable object containing the function.
        """
        
        functional = Functional(f)
        self._functions_using_tempdir.append(functional)

        return functional

    def build(self, collection_path: str, resampled_path: str, temporary_directory_path: str, transcription_json_file_path: str, context_change_callback: CtxChangeCallback):
        """"""
        # Prepare a copy of the context object.
        context = json.loads(self._default_context)

        # Choose an importing methodology and prepare it. Options:
        #   _import_files
        #   _import_directory
        # Note: This function calls the audio processing callback
        importing_method = None

        def _import_directory(dt: DataTransformer, dir_path:str, context, add_annotation, add_audio):

            #
            # TODO: Extract audio and transcription data here
            #
            pass
            
        
        def _import_files(dt: DataTransformer, _, add_annotation, add_audio):
            extention_to_files: FilteredPathList = _filter_files_by_extention(collection_path)
            audio_paths: PathList = extention_to_files.pop(dt._audio_ext_filter)
            # process audio
            dt._audio_processing_callback(audio_paths, resampled_path, add_audio)
            # process transcription data
            for extention, file_paths in extention_to_files.items():
                # only process the file type collection if a handler exists for it
                callback = self._import_extension_callbacks.get(extention, None)
                if callback is not None:
                    callback(file_paths, dt._import_context, add_annotation)
            
            # save transcription data to file
            with Path(transcription_json_file_path).open(mode='w') as fout:
                annotations = []
                for id in dt._annotation_store:
                    annotations.extend(dt._annotation_store[id])
                fout.write(json.dumps(annotations))
            return # _import_files

        if self._import_directory_callback is not None:
            importing_method = _import_directory
        else:
            importing_method = _import_files
        def _importing_closure(dt: DataTransformer, context: Dict):
            """
            A closure that prepares the call to the decided function, calls that function then saves the json result to file.
            """
            # Clean up from possible previous imports
            dt._annotation_store = {}
            dt._audio_store = {}

            # Callbacks to add data to the internal stores
            def add_annotation(id, obj):
                if id in dt._annotation_store:
                    dt._annotation_store[id].append(obj)
                else:
                    dt._annotation_store[id] = [obj]
                return # from add_annotation
            add_audio = lambda id, audio_path: dt._audio_store.update({id: audio_path})

            # Extract audio and transcription data here
            importing_method(dt, collection_path, context, add_annotation, add_audio)

            # save transcription data to file
            with Path(transcription_json_file_path).open(mode='w') as fout:
                annotations = []
                for id in dt._annotation_store:
                    annotations.extend(dt._annotation_store[id])
                fout.write(json.dumps(annotations))
            return # from process
        importing_function = _importing_closure
            

        # Prepare the audio function or use the replacement one
        audio_processing_callback = Functional(_default_audio_resampler)
        # register the default callback to have it's function restructured
        self._functions_using_tempdir.append(audio_processing_callback)

        # Note: the symbol dt is used in functions above it's definition, this
        # is intended as dt above is meant to be a pesudo-self argument which
        # will be the instance dt later.
        dt = DataTransformer(context, collection_path, resampled_path, temporary_directory_path, importing_function, audio_processing_callback, context_change_callback)

        # restructure functions that require a temporary directory
        for functional in self._functions_using_tempdir:
            original_f = functional.callback
            def wrapper(*args, **kwargs):
                # Ensure the directory is empty
                path = Path(temporary_directory_path)
                if path.exists():
                    shutil.rmtree(temporary_directory_path)
                path.mkdir(parents=True)

                # run the function with the clean directory
                original_f(*args, temporary_directory_path, **kwargs)

                # delete the temporary directory
                shutil.rmtree(temporary_directory_path)
            functional.callback = wrapper

        return dt


def _default_ctx_change_callback(ctx1, ctx2):
    """Does nothing."""
    return

def make_importer(n, c, r, tmp, t, ctx):
    return None

def make_exporter(n, c, r, tmp, t, ctx):
    return None

def make_data_transformer(name: str,
                            collection_path: str,
                            resampled_path: str,
                            temporary_directory_path: str,
                            transcription_json_file_path: str,
                            context_change_callback=_default_ctx_change_callback
                        ) -> DataTransformer:
    """
    Creates a concrete data transformer.

    :param name: type of requested data transformer.
    :param collection_path: path to the original file collection.
    :param resampled_path: path to put resampled audio into.
    :param temporary_directory_path: path to store and operate on temporary data.
    :param transcription_json_file_path: path to save json file for transcription output data to.
    :param context_change_callback: When the context is changed, this callback is called with the new context.
    :returns: a DataTransformer of the requested type if it exists, else an error is raised.
    :raises:
        ValueError: if the requested data transformer does not exist.
    """
    

    dtaf: DataTransformerAbstractFactory = DataTransformerAbstractFactory._transformer_factories[name]
    dt = dtaf.build(collection_path, resampled_path, temporary_directory_path, transcription_json_file_path, context_change_callback)
    return dt


def _filter_files_by_extention(dir_path: str) -> Dict[str, List[str]]:
    """
    Separate all files into lists by file extention.

    :param dir_path: Filesystem path to contents directory.
    :return: Dictionary of extentions as keys and lists of assocciated paths as values.
    """
    dir_path = Path(dir_path)
    extention_to_files = {}
    for file_path in dir_path.iterdir():
        if '.' not in file_path.name:
            # skip extentionless files
            continue
        if file_path.is_dir():
            # skip directories
            continue
        extention = file_path.name.split('.')[-1]
        # Make dictionary of files separated by 
        if extention not in extention_to_files:
            extention_to_files[extention] = [f'{file_path}']
        else:
            extention_to_files[extention].append(f'{file_path}')
    return extention_to_files

def _default_audio_resampler(audio_paths: List[str], resampled_dir_path: str, add_audio: AddAudioFunction, temp_dir_path: str):
    """
    A default audio resampler that converts any media accepted by sox to a
    standard format specified in process_item.

    :param audio_paths: list of paths to audio files to resample.
    :param resampled_dir_path: path to a directory to save the resampled files to.
    :param add_audio: callback to register the audio with the importer.
    :param temp_dir_path: path to a temporary directory, will exist before the
        function runs and will be deleted immediately after the function ends.
        Must be the last parameter as this path is prepended on build().
    """
    
    temp_dir_path = Path(temp_dir_path)
    resampled_dir_path = Path(resampled_dir_path)

    # Empty resampled contents
    if resampled_dir_path.exists():
        shutil.rmtree(f'{resampled_dir_path}')
    resampled_dir_path.mkdir(parents=True, exist_ok=True)

    process_lock = threading.Lock()
    temporary_directories = set()
    map_arguments = [(index, audio_path, process_lock, temporary_directories, temp_dir_path)
                        for index, audio_path in enumerate(audio_paths)]
    # Multi-Threaded Audio Re-sampling
    with Pool() as pool:
        outputs = pool.map(process_item, map_arguments)
        for audio_file in outputs:
            shutil.move(audio_file, resampled_dir_path)
            file_name = Path(audio_file).name
            id = '.'.join(file_name.split('.')[:-1])
            resampled_file_path = f'{resampled_dir_path.joinpath(file_name)}'
            add_audio(id, resampled_file_path)

# import other python files in this directory as data transformers.
def _import_instanciated_data_transformers():
    names = os.listdir('elpis/transformer')
    try:
        names.remove('__init__.py')
    except ValueError:
        pass # '__init__.py' not in the list and that's okay.
    # Only keep python files
    names = [name[:-len('.py')] for name in names if name.endswith('.py')]
    for importer_file_name in names:
        i = importlib.import_module('elpis.transformer.' + importer_file_name)
        print(dir(i))
        print(DataTransformerAbstractFactory._transformer_factories)
_import_instanciated_data_transformers()

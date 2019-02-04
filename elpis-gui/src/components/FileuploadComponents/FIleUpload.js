import React, { Component } from "react";
import classNames from "classnames";
import Dropzone from "react-dropzone";
import {fromEvent} from "file-selector";
import { translate } from 'react-i18next';
// import request from "superagent";

// import { addAudioFile, addTranscriptionFile, addAdditionalTextFile } from '../../redux/apiModelActions';
import { connect } from 'react-redux';

class FileUpload extends Component {
    state={
        files:[],
        fileNames:[]
    }

    onDrop = (acceptedFiles, rejectedFiles) => {
        console.log("file dropped:", acceptedFiles);


        // acceptedFiles.forEach(file => {
        //     //console.log(file)
        //     request
        //     .post('http://127.0.0.1:5000/corpus/wav')
        //     .attach(file.name, file.path);
        // });

        const fileNames = acceptedFiles.map(f => f.name);
        fileNames.forEach(filename => {
            if (filename.endsWith('.wav')) {
                // this.props.addAudioFile(filename);
            } else if (filename.endsWith('.eaf') || filename.endsWith('.TextGrid')) {
                // this.props.addTranscriptionFile(filename);
            } else if (filename.endsWith('.txt')) {
                // this.props.addAdditionalTextFile(filename);
            } else {
                // TODO tell the user that they can't put this type of file here
            }
        });
        //console.log(fileNames);
        // this.setState({ ...this.state, files: acceptedFiles, fileNames: fileNames  });
    };

    render(){
        const fileNameList = (this.state.fileNames) ? (this.state.fileNames.map((f) => <li key={f}>{f}</li>)) : ''
        const { t } = this.props;

        return(
            <div className="App">
            {this.props.myName}
                    <p>{t('fileUpload.audioLabel')} {this.props.audioFiles}</p>
                    <p>{t('fileUpload.transcriptionLabel')} {this.props.transcriptionFiles}</p>
                    <p>{t('fileUpload.additionalLabel')} {this.props.additionalTextFiles}</p>

                    <Dropzone className="dropzone" onDrop={this.onDrop} getDataTransferItems={evt => fromEvent(evt)}>
                        {({ getRootProps, getInputProps, isDragActive }) => {
                            return (
                                <div
                                    {...getRootProps()}
                                    className={classNames("dropzone", {
                                        "dropzone_active": isDragActive
                                    })}
                                >

                                    <input {...getInputProps()} />

                                        {isDragActive ? (
                                            <p>{t('fileUpload.dropFilesHeader')} </p>
                                        ) : (
                                            <p>
                                                {t('fileUpload.dropFilesHint')}
                                            </p>
                                        )}

                            </div>
                        );
                    }}
                    </Dropzone>

                    <ul>{fileNameList}</ul>
            </div>

        );
    }
}

const mapStateToProps = state => {
    return {
        // myName: state.myName,
        // audioFiles: state.model.audioFiles,
        // transcriptionFiles: state.model.transcriptionFiles,
        // additionalTextFiles: state.model.additionalTextFiles,
    }
}

const mapDispatchToProps = dispatch => ({
    // addTranscriptionFile: filename => {
    //     dispatch(addTranscriptionFile(filename));
    // },
    // addAudioFile: filename => {
    //     dispatch(addAudioFile(filename));
    // },
    // addAdditionalTextFile: filename => {
    //     dispatch(addAdditionalTextFile(filename));
    // },
})

export default connect(mapStateToProps, mapDispatchToProps)(translate('common')(FileUpload));

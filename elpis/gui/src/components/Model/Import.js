import React, { Component } from 'react';
import { Link } from "react-router-dom";
import classNames from "classnames";
import Dropzone from "react-dropzone";
import { Divider, Grid, Header, Segment, Icon, Button, Table, Modal } from 'semantic-ui-react';
import { connect } from 'react-redux';
import { translate } from 'react-i18next';
import { modelImport } from 'redux/actions/modelActions';
import Branding from 'components/Shared/Branding';
import SideNav from 'components/Shared/SideNav';
import CurrentModelName from "./CurrentModelName";

class ModelImport extends Component {

    componentDidMount() {
    }

    onDrop = (acceptedFiles, rejectedFiles) => {
        console.log("files dropped:", acceptedFiles)
        var formData = new FormData()
        acceptedFiles.forEach(file => {
            formData.append('file', file)
        })
        this.props.modelImport(formData)
    }

    render() {
        const { t, currentEngine, name } = this.props;

        return (
            <div>
                <Branding />
                <Segment>
                    <Grid centered>
                        <Grid.Column width={ 4 }>
                            <SideNav />
                        </Grid.Column>

                        <Grid.Column width={ 12 }>
                            <Header as='h1' text='true'>
                                { t('model.import.title') }
                            </Header>


                            <div className="FileUpload">

                                <Dropzone
                                    className="dropzone"
                                    onDrop={ this.onDrop }
                                    getDataTransferItems={ evt => fromEvent(evt) }>
                                    { ({ getRootProps, getInputProps, isDragActive }) => {
                                        return (
                                            <div
                                                { ...getRootProps() }
                                                className={ classNames("dropzone", {
                                                    "dropzone_active": isDragActive
                                                }) }
                                            >
                                                <input { ...getInputProps() } />
                                                {
                                                    isDragActive ? (
                                                        <p>{ t('dataset.fileUpload.dropFilesHintDragActive') } </p>
                                                    ) : (<p>{ t('dataset.fileUpload.dropFilesHint') }</p>)
                                                }
                                                <Button>{t('dataset.files.uploadButton')}</Button>
                                            </div>
                                        )
                                    } }
                                </Dropzone>
                            </div>

                        </Grid.Column>

                    </Grid>
                </Segment>
            </div>
        );
    }
}

const mapStateToProps = state => {
    return {
        currentEngine: state.engine.engine,
        name: state.model.name
    }
}

const mapDispatchToProps = dispatch => ({
    modelImport: postData => {
        dispatch(modelImport(postData))
    }
})

export default connect(mapStateToProps, mapDispatchToProps)(translate('common')(ModelImport));

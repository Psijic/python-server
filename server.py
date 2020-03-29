#!/usr/bin/python3
import os
import secrets

import logging
from flask import Flask, jsonify, redirect, render_template, request, send_file
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from database import Base, Video

IS_DEBUG = True  # False for release!
VIDEO_UPLOAD_DIR = 'videos/uploaded'  # Path()
VIDEO_ENCODE_DIR = 'videos/encoded/'
ALLOWED_EXTENSIONS = ['.mp4', '.mkv', '.jpg']
MAX_FILE_SIZE_MB = 512

app = Flask(__name__)
app.config['UPLOAD_DIR'] = VIDEO_UPLOAD_DIR
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE_MB * 1024 * 1024

engine = create_engine('sqlite:///videos.db', connect_args={'check_same_thread': False})
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# check the file extension
def allowed_file(filename):
    return os.path.splitext(filename)[1] in ALLOWED_EXTENSIONS


# check if filename already exists. It's possible to check by file key.
def file_exists(filename):
    return session.query(Video.id).filter_by(name=filename).scalar() is not None


def add_file_to_library(name, path, key=None, kid=None):
    logging.info('Adding file to library:', name)
    video = Video(name=name, path=path, key=key, kid=kid)
    session.add(video)
    session.commit()
    return video.id


def encode_file(path_in, path_out, key, kid):
    logging.info('Encoding file: {}'.format(path_in))
    if key is None:
        key = secrets.token_urlsafe(16)
    if kid is None:
        kid = secrets.token_urlsafe(16)

    os.system(
        'ffmpeg -y -i {path_in} {codecs} -encryption_scheme cenc-aes-ctr -encryption_key {key} -encryption_kid {kid} {path_out}'
            .format(path_in=path_in, codecs='-vcodec copy -acodec copy', key=key, kid=kid, path_out=path_out))


# def get_file_path(content_id):
#     video = session.query(Video).filter_by(id=content_id).scalar()
#     return os.path.abspath(video.path + video.name)


@app.route('/', methods=['GET', 'POST'])
def upload_file_form():
    # upload file main form
    if request.method == 'POST':
        return upload_file()
    file_types = ', '.join(ALLOWED_EXTENSIONS)
    return render_template('main.html', fileTypes=file_types, fileSize=MAX_FILE_SIZE_MB)


@app.route('/packaged_content/<int:content_id>', methods=['GET'])
def packaged_content_get(content_id):
    video = session.query(Video).filter_by(id=content_id).scalar()
    if video is None:
        abort(418, 'File not exists')
    url = os.path.abspath(video.path + video.name)
    return jsonify({'url': url, 'key': video.key, 'kid': video.kid})


@app.route('/download/<int:content_id>', methods=['GET'])
def download_file(content_id):
    video = session.query(Video).filter_by(id=content_id).scalar()
    url = os.path.abspath(video.path + video.name)
    return send_file(url, as_attachment=True)


@app.route('/play/<int:content_id>', methods=['GET'])
def play_video(content_id):
    video = session.query(Video).filter_by(id=content_id).scalar()
    url = os.path.abspath(video.path + video.name)
    return render_template('player.html', url=url)


@app.route('/packaged_content', methods=['POST'])
def packaged_content_post():
    # need to send options in JSON format
    options = request.get_json()
    logging.info('packaged_content', options)
    if not all(k in options for k in ('id', 'key', 'kid')):
        abort(400, 'Needed parameters {id, key, kid} are not in request data.')

    video = session.query(Video).filter_by(id=options['id']).scalar()
    path_in = os.path.join(app.config['UPLOAD_DIR'], video.name)
    path_out = os.path.join(VIDEO_ENCODE_DIR, video.name)
    encode_file(path_in, path_out, options['key'], options['kid'])

    # TODO: Should we clean original videos?
    # os.remove(path_in)
    # session.delete(video)
    # session.commit()

    # we don't wait for encoding result for now
    encoded_id = add_file_to_library(video.name, VIDEO_ENCODE_DIR, options['key'], options['kid'])
    return jsonify({'packaged_content_id': encoded_id})


# upload file
@app.route('/upload', methods=['POST'])
@app.route('/upload_input_content', methods=['POST'])
def upload_file():
    # check if the post request has the file part
    if 'file' not in request.files:
        abort(400, 'No file present')
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        if file_exists(filename):
            abort(400, 'Video with this name already exists')

        try:
            file.save(os.path.join(app.config['UPLOAD_DIR'], filename))
            content_id = add_file_to_library(filename, VIDEO_UPLOAD_DIR)
            return jsonify({'input_content_id': content_id})
        except Exception as e:
            abort(403, 'Something went wrong with the file uploading')
            logging.error(e)

    abort(400, 'This video format is not supported ')


@app.route('/all', methods=['GET'])
def show_all_videos():
    videos = session.query(Video).all()
    return jsonify(videos=[video.serialize for video in videos])
    # return render_template('player.html', videos=all_videos)


if __name__ == '__main__':
    # preparing environment
    if not os.path.exists(VIDEO_UPLOAD_DIR):
        os.makedirs(VIDEO_UPLOAD_DIR)
    if not os.path.exists(VIDEO_ENCODE_DIR):
        os.makedirs(VIDEO_ENCODE_DIR)

    app.debug = IS_DEBUG
    app.run(host='0.0.0.0', port=5000)

#!/usr/bin/python3
import logging
import os
import subprocess

from flask import Flask, jsonify, redirect, render_template, request, send_file
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from database import Base, EncodedVideo, UploadedVideo

IS_DEBUG = False  # False for release!
IS_AUTO_CLEAN = False
VIDEO_UPLOAD_DIR = 'videos/uploaded/'  # Path()
VIDEO_ENCODE_DIR = 'videos/encoded/'
ALLOWED_EXTENSIONS = ['.mp4', '.mkv']
MAX_FILE_SIZE_MB = 512

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = VIDEO_UPLOAD_DIR
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
    return session.query(UploadedVideo.id).filter_by(name=filename).scalar() is not None


# add a file to DB. Could be split to uploaded/encoded methods.
def add_file_to_library(name, path, key=None, kid=None):
    logging.info('Adding file to library:', name)
    if key is None and kid is None:
        video = UploadedVideo(name=name, path=path)
    else:
        video = EncodedVideo(name=name, path=path, key=key, kid=kid)
    session.add(video)
    session.commit()
    return video.id


def delete_content(path_in, video):
    os.remove(path_in)
    session.delete(video)
    session.commit()


# keys to success.
def encode_file(path_in, path_out, key, kid):
    logging.info('Encoding file: {}'.format(path_in))
    # This is simple encoding for better performance with test cases.
    # For DASH you can add -dash 1 and other parameters.
    # See https://developer.mozilla.org/en-US/docs/Web/HTML/DASH_Adaptive_Streaming_for_HTML_5_Video
    return subprocess.call([
        'ffmpeg', '-y',
        '-i', path_in,
        '-vcodec', 'copy',
        '-acodec', 'copy',
        '-encryption_scheme', 'cenc-aes-ctr',
        '-encryption_key', key,
        '-encryption_kid', kid,
        path_out
    ])


# upload file main form
@app.route('/', methods=['GET', 'POST'])
def upload_file_form():
    if request.method == 'POST':
        return upload_file()
    file_types = ', '.join(ALLOWED_EXTENSIONS)
    return render_template('main.html', fileTypes=file_types, fileSize=MAX_FILE_SIZE_MB)


@app.route('/download/<int:content_id>', methods=['GET'])
def download_file(content_id):
    video = session.query(UploadedVideo).filter_by(id=content_id).scalar()  # should be inlined
    if video is None:
        abort(418, 'File not exists')
    return send_file(os.path.join(video.path, video.name), as_attachment=True)


@app.route('/play/<int:content_id>', methods=['GET'])
def play_video(content_id):
    video = session.query(UploadedVideo).filter_by(id=content_id).scalar()  # should be inlined
    if video is None:
        abort(418, 'File not exists')
    return render_template('player.html', url=os.path.join(video.path, video.name))


@app.route('/packaged_content/<int:content_id>', methods=['GET'])
def packaged_content_get(content_id):
    video = session.query(EncodedVideo).filter_by(id=content_id).scalar()
    if video is None:
        abort(418, 'File not exists')
    url = os.path.join(video.path, video.name)

    return jsonify({'url': url, 'key': video.key, 'kid': video.kid})


@app.route('/packaged_content', methods=['POST'])
def packaged_content_post():
    # need to send options in JSON format
    options = request.get_json()
    logging.info('packaged_content', options)
    if not all(k in options for k in ('id', 'key', 'kid')):
        abort(400, 'Needed parameters {id, key, kid} are not in request data.')

    video = session.query(UploadedVideo).filter_by(id=options['id']).scalar()
    if video is None:
        abort(400, 'Content with this id not exist')

    path_in = os.path.join(video.path, video.name)
    path_out = os.path.join(VIDEO_ENCODE_DIR, video.name)
    encode_result = encode_file(path_in, path_out, options['key'], options['kid'])

    if encode_result != 0:
        abort(403, 'Error encoding video, code: {}'.format(encode_result))

    # should we clean original video?
    if IS_AUTO_CLEAN:
        delete_content(path_in, video)

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
            abort(400, 'UploadedVideo with this name already exists')

        try:
            file.save(os.path.join(VIDEO_UPLOAD_DIR, filename))
            content_id = add_file_to_library(filename, VIDEO_UPLOAD_DIR)
            return jsonify({'input_content_id': content_id})
        except Exception as e:
            abort(403, 'Something went wrong with the file uploading')
            logging.error(e)

    abort(400, 'This video format is not supported ')


@app.route('/allUploaded', methods=['GET'])
def show_all_uploaded_videos():
    videos = session.query(UploadedVideo).all()
    return jsonify(uploaded_videos=[video.serialize for video in videos])


@app.route('/allEncoded', methods=['GET'])
def show_all_encoded_videos():
    videos = session.query(EncodedVideo).all()
    return jsonify(encoded_videos=[video.serialize for video in videos])


if __name__ == '__main__':
    # preparing environment
    if not os.path.exists(VIDEO_UPLOAD_DIR):
        os.makedirs(VIDEO_UPLOAD_DIR)
    if not os.path.exists(VIDEO_ENCODE_DIR):
        os.makedirs(VIDEO_ENCODE_DIR)

    app.debug = IS_DEBUG
    app.run(host='0.0.0.0', port=5000)

#!/usr/bin/python3
import hashlib
from pathlib import Path
from random import random

from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, request, redirect, url_for
from sqlalchemy import create_engine
import os

from sqlalchemy.orm import sessionmaker
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from encrypt import encrypt_file

from database import Base, Video

IS_DEBUG = True  # False for release!
# UPLOAD_FOLDER = Path('videos')
UPLOAD_FOLDER = 'videos/'
ALLOWED_EXTENSIONS = {'mp4', 'mkv', 'jpg'}
MAX_FILE_SIZE_MB = 512
AES_KEY = 'super_secret_key'  # hashed key should be inserted externally!
# AES_HASH_KEY = hashlib.sha256(AES_KEY.encode('utf-8')).digest()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE_MB * 1024 * 1024

engine = create_engine('sqlite:///videos.db', connect_args={'check_same_thread': False})
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# check the file extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# check if filename already exists. It's possible to check by file key.
def file_exists(filename):
    return session.query(Video.id).filter_by(name=filename).scalar() is not None


def add_file_to_db(name, path, key, kid):
    # file path could be different for CDN purposes, different formats etc.
    video = Video(name=name, path=path, key=key, kid=kid, )
    session.add(video)
    session.commit()


def add_file_to_library(filename):
    encrypt_file(AES_KEY, UPLOAD_FOLDER + filename)
    add_file_to_db(filename, UPLOAD_FOLDER, "key_" + filename, "kid_" + filename)


@app.route('/packaged_content/<int:content_id>', methods=['GET'])
def packaged_content_get(content_id):
    video = session.query(Video).filter_by(id=content_id).scalar()
    url = video.path + video.name
    return jsonify({'url': url, 'key': video.key, 'kid': video.kid})


@app.route('/packaged_content', methods=['POST'])
def packaged_content_post():
    return jsonify({'input_content_id': 1, 'key': 'hyN9IKGfWKdAwFaE5pm0qg', 'kid': 'oW5AK5BW43HzbTSKpiu3SQ'})


# upload file main form
@app.route('/', methods=['GET', 'POST'])
def upload_file_form():
    if request.method == 'POST':
        return upload_file()
    return render_template('uploadFile.html', fileTypes=str(ALLOWED_EXTENSIONS)[1:-1], fileSize=MAX_FILE_SIZE_MB)


# upload file
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

        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        add_file_to_library(filename)
        return jsonify({'input_content_id': 1})
    abort(400, 'This video format is not supported ')


@app.route('/all', methods=['GET'])
def show_all_videos():
    videos = session.query(Video).all()
    return jsonify(videos=[video.serialize for video in videos])
    # return render_template('videos.html', videos=all_videos)


if __name__ == '__main__':
    # preparing environment
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    app.debug = IS_DEBUG
    app.run(host='0.0.0.0', port=5000)

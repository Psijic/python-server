from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, request, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from werkzeug.utils import secure_filename

IS_DEBUG = True  # False for release
UPLOAD_FOLDER = 'videos'
ALLOWED_EXTENSIONS = {'mp4', 'mkv'}
MAX_FILE_SIZE = 16

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE * 1024 * 1024


# engine = create_engine('sqlite:///videos.db')
# Base.metadata.bind = engine
#
# DBSession = sessionmaker(bind=engine)
# session = DBSession()

# checking the file extension
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file', filename=filename))
    return render_template('uploadFile.html', fileTypes=str(ALLOWED_EXTENSIONS)[1:-1], fileSize=MAX_FILE_SIZE)


# @app.route('/upload_input_content/<string:filename>', methods=['GET', 'POST'])


if __name__ == '__main__':
    app.debug = IS_DEBUG
    app.run(host='0.0.0.0', port=5000)

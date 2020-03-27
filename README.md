# Simple Server
Python simple video uploader server. Uses **Flask** and **SQLAlchemy**.

### Running
Just run `./server.py` in Unix terminal. Or use `python3 server.py` command. The server runs on `http://0.0.0.0:5000/` address.
If you want to stop it, press `Ctrl + C`

### File Uploading
You can upload a video file of `ALLOWED_EXTENSIONS` with `POST` request using external tools like _Postman_, _Fiddler_ etc.
The simple way is to run next Bash command:
`curl  -F 'file=@{yourfilename.mp4}' 0.0.0.0:5000/upload_input_content`
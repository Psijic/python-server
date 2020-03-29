# Simple Server
Python simple video uploader server. Uses **Flask** and **SQLAlchemy**.

### Setup
Python script makes a video storage directory `$UPLOAD_FOLDER` if it doesn't exist. 
Also, the videos.db database will be generated. If there problems with it, run database.py first

### Running
Just run `./server.py` in Unix terminal. Or execute `python3 server.py` command. 
The server runs on `http://0.0.0.0:5000/` address. If you want to stop it, press `Ctrl + C`


### File Uploading
You can upload a video file of `$ALLOWED_EXTENSIONS` with `POST` request using web form 
or external tools like _Postman_, _Fiddler_ etc. The other way is to run next Bash command:  
`curl  -F 'file=@{yourfilename.mp4}' 0.0.0.0:5000/upload_input_content`  
The syntax should be same.

### Tools
It's possible to use tools like:  
https://www.ffmpeg.org (available _encryption scheme_ is `cenc-aes-ctr`)  
https://www.bento4.com  
https://github.com/google/shaka-packager  
https://github.com/google/shaka-player

~~~~https://developer.mozilla.org/en-US/docs/Web/HTML/DASH_Adaptive_Streaming_for_HTML_5_Video

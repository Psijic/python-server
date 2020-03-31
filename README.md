# Simple Server
Python simple video encoding server. Uses **Flask**, **SQLAlchemy**, **FFmpeg**.

### Setup
You need to have [FFmpeg](https://www.ffmpeg.org) binary installed.
Python script makes a video storage directories if they don't exist.   
Also, the videos.db database will be generated. If there are problems with it, run database.py first.

For **Debian**-based derivatives you can run these commands:
```shell script
sudo apt-get -y install ffmpeg

pip3 install --upgrade pip
pip3 install flask
pip3 install sqlalchemy
```

Also **Docker** container included. Sample commands to use it:
```shell script
docker build -t video-server .
docker run -it -d -p 5000:5000 video-server
```

### Running
Just run `./server.py` in Unix terminal. Or execute `python3 server.py` command.  
The server runs on `http://0.0.0.0:5000/` address. If you want to stop it, press `Ctrl + C`.

### File Uploading
You can upload a video file of `$ALLOWED_EXTENSIONS` with `POST` request via web form 
or external tools like _Postman_, _Fiddler_ etc.  
The other way is to run next Bash command (you should use same syntax):  
`curl  -F 'file=@{yourfilename.mp4}' 0.0.0.0:5000/upload_input_content`.

### Playing encoded file
You can play encrypted video with `ffplay` command like  
`ffplay SampleVideo_encrypted.mp4 -decryption_key 76a6c65c5ea762046bd749a2e632ccbb`.  
Future plans: add web player directly in a browser (`/templates/player.html` file)

### Endpoints
  * GET, POST `/` - main web form. Visit `http://0.0.0.0:5000/` address in browser.
  * POST `/upload`, `/upload_input_content` - upload a video file with extension of `$ALLOWED_EXTENSIONS`.  
You can also do it via web form.
Sample Bash command (or you can use tools like _Postman_, _Fiddler_ etc.):  
`curl  -F 'file=@{yourfilename.mp4}' 0.0.0.0:5000/upload_input_content`.  

  * GET `/download/<int:content_id>` - download encoded file.
  * GET `/play/<int:content_id>` - play encoded video in a browser player (TBD with [Shaka Player](https://github.com/google/shaka-packager )).
  * POST `/packaged_content` - encode previously uploaded video. Need to send JSON data with {id, key, kid} in request. Sample:  
`curl -X POST -H "Content-Type: application/json" -d '{"id":1, "key":"76a6c65c5ea762046bd749a2e632ccbb", 
"kid":"a7e61c373e219033c21091fa607bf3b8"}' 0.0.0.0:5000/packaged_content` .
  * GET `/allUploaded` - list of all uploaded videos.
  * GET `/allEncoded` - list of all encoded videos.

### Next
FFmpeg encryption uses only cenc-aes-ctr scheme, so, for CBCs it's possible to use another tools like [Bento4](https://www.bento4.com ) or [Shaka Packager](https://github.com/google/shaka-packager).
For playing encoded video it's possible to implement advanced video player like [Google Shaka Player](https://github.com/google/shaka-player).
For DASH encoding we need to split the video on chunks and generate a manifest file. 
And for different resolution support, we need to encode the uploaded file with lesser resolutions. 
It's possible to separate video and audio tracks and use only one audio track. 
It's also can be done to support different language tracks.  
[DASH Adaptive Streaming for HTML 5 Video](https://developer.mozilla.org/en-US/docs/Web/HTML/DASH_Adaptive_Streaming_for_HTML_5_Video)


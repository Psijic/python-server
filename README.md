# Simple Server
python simple server

Objective:
The idea of this exercise is to be able to see your knowledge while developing a simple API with a
persistence layer than can execute some background packaging tasks.
It is not necessary to develop any administration view, ​only the backend development is necessary​.
Preconditions:
There are no limitations of technologies or languages, you can use the ones that you consider most
appropriate according to your criteria.
It is important that you apply your own criteria of quality and organization of the project. Think
about what would seem right to apply in a production development.
The delivery of the project will be done through github.
Definition:
1) Implement an upload file endpoint, the endpoint should be able to return a reference for element
tracking to be used in future calls. For the sake of this exercise consider that uploaded files will be in
the range of hundreds of MBs, for instance a trailer of 1-2 minutes.
This is just an guideline example, feel free to implement it in the way you consider appropriate:
POST​ /upload_input_content + <FILE_TO_BE_UPLOADED>
RESPONSE​: 200 OK:​ {“input_content_id”: 1}
2) Implement an endpoint launch packaging job for a given reference of a previously uploaded file.
For the sake of simplicity on this technical assessment:
- Do not need to transcode the content, I suggest to use a h.264+aac on an MP4 container as
input_content.
- Use AES cbcs clearkey encryption mechanism, so we don’t need DRM infrastructure to
protect and play this content.
- We propose you to just run this as a background task on the same computer, executing the
parameters and any external software you consider to achieve this result.
- This endpoint should return a reference to be able to playback the content once the
background packaging task is completed.
Example:
POST​{
/packaged_content
“input_content_id”: 1,
“key”: “hyN9IKGfWKdAwFaE5pm0qg”,
“kid”: “oW5AK5BW43HzbTSKpiu3SQ”
}
RESPONSE: 200 OK: ​{packaged_content_id: 55}
3) Implement an endpoint to obtain the necessary data from a completed packaging task, if the task
has failed or not completed yet, please return an appropriate response.
GET​ /packaged_content/55
RESPONSE: 200 OK:
{
“url”: “http://localhost/................./stream.mpd”,
“key”: “hyN9IKGfWKdAwFaE5pm0qg”,
“kid”: “oW5AK5BW43HzbTSKpiu3SQ”
}
4) Provide a guide to validate playback correctness of the content packaged. An explanation on how
can we test playback on a newly packaged content will suffice for this point, this will probably
include a solution to serve the manifest and media chunks and also a browser/player that is able to
playback a MPEG-DASH clearkey.
OPTIONAL BONUS tasks:
These tasks are optional and not mandatory, some of them may help you to test and develop, some
other are very common tasks we do at Rakuten.tv when we develop a service.
-

Serve the content mpd and media chunks from the developed service.
Integrate the player on the service so we can consume content directly from the service
without the need of an external player and manual manipulation.
Add some basic unit testing mechanism to the service.
Docker image to test and run your implementation.
Propose how you would modify/extend this service so we can achieve a multi
resolution/multi bitrate packaging solution. We just expect some explanation we don’t need
a real implementation for this.


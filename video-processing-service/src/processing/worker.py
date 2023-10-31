from redis import Redis
from video_processing_service import process_video

r = Redis(host='localhost', port=6379, decode_responses=True)

pubsub = r.pubsub()
pubsub.subscribe('video_upload')

for message in pubsub.listen():
    print(f"Received a message: {message}")
    if message['type'] == 'message':
        video_name = message['data']
        print(f"Processing video: {video_name}")
        process_video(video_name)




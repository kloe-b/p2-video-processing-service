from redis import Redis
from processing import process_video

r = Redis(host='localhost', port=6379, decode_responses=True)

pubsub = r.pubsub()
pubsub.subscribe('video_upload')

for message in pubsub.listen():
    if message['type'] == 'message':
        process_video(r.brpop("video_details")[1])



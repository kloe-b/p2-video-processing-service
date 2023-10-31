from flask import Flask, request, jsonify
import subprocess
import os
from rq import Worker, Queue, Connection
from redis import Redis

redis_conn = Redis(host='localhost', port=6379)

q = Queue('thumbnail_generation', connection=redis_conn)

app = Flask(__name__)

THUMBNAIL_DIR = 'thumbnails'

if not os.path.exists(THUMBNAIL_DIR):
    os.makedirs(THUMBNAIL_DIR)

def generate_thumbnail(video_file):
    if video_file:
        thumbnail_path = os.path.join(THUMBNAIL_DIR, video_file.replace('.mp4', '.jpg'))
        subprocess.run(['ffmpeg', '-i', video_file.filename, '-ss', '00:00:10', '-vframes', '1', '-q:v', '2', thumbnail_path])

        return 'Thumbnail generation complete', 'thumbnail_path ' + thumbnail_path
    else:
        return 'Video file missing'

if __name__ == '__main__':
    with Connection(redis_conn):
        worker = Worker(['thumbnail_generation'])
        worker.work()
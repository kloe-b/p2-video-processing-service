from flask import Flask, request, jsonify
import subprocess
import os
from rq import Queue, Connection
from redis import Redis

redis_conn = Redis(host='localhost', port=6379)

q = Queue('thumbnail_generator', connection=redis_conn)

app = Flask(__name__)

THUMBNAIL_DIR = 'thumbnails'

if not os.path.exists(THUMBNAIL_DIR):
    os.makedirs(THUMBNAIL_DIR)

def generate_thumbnail(video_file):
    if video_file:
        thumbnail_path = os.path.join(THUMBNAIL_DIR, video_file.replace('.mp4', '.jpg'))
        subprocess.run(['ffmpeg', '-i', video_file.filename, '-ss', '00:00:10', '-vframes', '1', '-q:v', '2', thumbnail_path])

        return jsonify({'message': 'Thumbnail generation complete', 'thumbnail_path': thumbnail_path}), 200
    else:
        return jsonify({'error': 'Video file missing'}), 400

if __name__ == '__main__':
    with Connection(redis_conn):
        print('Thumbnail Generation Worker is running...')
        while True:
            job = q.dequeue()
            if job is not None:
                video_path = job.args[0]
                generate_thumbnail(video_path)
                job.delete()
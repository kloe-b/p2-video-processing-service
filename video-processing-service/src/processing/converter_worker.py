from flask import Flask, request, jsonify
import subprocess
import os
from rq import Queue, Connection
from redis import Redis

app = Flask(__name__)

CONVERTED_VIDEO_DIR = 'converted_videos'

redis_conn = Redis(host='localhost', port=6379)

q = Queue('converter', connection=redis_conn)

if not os.path.exists(CONVERTED_VIDEO_DIR):
    os.makedirs(CONVERTED_VIDEO_DIR)

def convert_video(video_file):
    if video_file:
        video_path = os.path.join(CONVERTED_VIDEO_DIR, video_file.filename.replace('...', '.mp4'))
        video_file.save(video_path)

        subprocess.run(['ffmpeg', '-i', video_path, '-c:v', 'libx264', '-crf', '23', '-c:a', 'aac', video_path])

        return jsonify({'message': 'Video conversion complete', 'converted_video_path': video_path}), 200
    else:
        return jsonify({'error': 'Video file missing'}), 400

if __name__ == '__main__':
    with Connection(redis_conn):
        print('Video Conversion Worker is running...')
        while True:
            job = q.dequeue()
            if job is not None:
                video_path = job.args[0]
                convert_video(video_path)
                job.delete()

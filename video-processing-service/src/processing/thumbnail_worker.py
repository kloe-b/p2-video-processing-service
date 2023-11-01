from flask import Flask, request, jsonify
import subprocess
import os
from rq import Worker, Queue, Connection
from redis import Redis

redis_conn = Redis(host='localhost', port=6379)

q = Queue('thumbnail_generation', connection=redis_conn)

import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='app.log',
                    filemode='a')


THUMBNAIL_DIR = 'thumbnails'

if not os.path.exists(THUMBNAIL_DIR):
    os.makedirs(THUMBNAIL_DIR)

def generate_thumbnail(video_filename):
    if os.path.exists(video_filename):
        logging.info(f"Started processing thumbnail job for video: {video_filename}")
        thumbnail_path = os.path.join(THUMBNAIL_DIR, os.path.basename(video_filename).replace('.mp4', '.jpg'))
        subprocess.run(['ffmpeg', '-i', video_filename, '-ss', '00:00:10', '-vframes', '1', '-q:v', '2', thumbnail_path])

        logging.info(f"Completed processing thumbnail job for video: {video_filename}")
        return 'Thumbnail generation complete', 'thumbnail_path ' + thumbnail_path
    else:
        return 'Video file missing'

if __name__ == '__main__':
    with Connection(redis_conn):
        print('Video Thumbnail Worker is running...')
        worker = Worker(['thumbnail_generation'])
        worker.work()
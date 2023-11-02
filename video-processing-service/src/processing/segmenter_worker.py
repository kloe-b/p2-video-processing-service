from flask import Flask, request, jsonify
import subprocess
import os
from rq import Worker, Queue, Connection
from redis import Redis
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='app.log',
                    filemode='a')


VIDEO_SEGMENT_DIR = 'video_segments'

redis_conn = Redis(host='localhost', port=6379)

q = Queue('video_chunking', connection=redis_conn)

if not os.path.exists(VIDEO_SEGMENT_DIR):
    os.makedirs(VIDEO_SEGMENT_DIR)

def generate_segments(video_filename):

    if os.path.exists(video_filename):
        logging.info(f"Started processing chunking job for video: {video_filename}")
        hls_playlist = os.path.join(VIDEO_SEGMENT_DIR, 'playlist.m3u8')
        subprocess.run(['ffmpeg', '-i', video_filename, '-hls_time', '10', '-hls_list_size', '0', '-hls_segment_filename',
                        os.path.join(VIDEO_SEGMENT_DIR, 'segment%03d.ts'), '-f', 'hls', hls_playlist])
        
        logging.info(f"Completed processing chunking job for video: {video_filename}")
        return 'Segement generation complete', 'segments '+ hls_playlist
    else:
        return 'Video file missing'

if __name__ == '__main__':
    with Connection(redis_conn):
        print('Video Segmenter Worker is running...')
        worker = Worker(['video_chunking'])
        worker.work()

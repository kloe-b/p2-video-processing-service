from flask import Flask, request, jsonify
import subprocess
import os
from rq import Queue, Connection
from redis import Redis

app = Flask(__name__)

VIDEO_SEGMENT_DIR = 'video_segments'

redis_conn = Redis(host='localhost', port=6379)

q = Queue('segments_generator', connection=redis_conn)

if not os.path.exists(VIDEO_SEGMENT_DIR):
    os.makedirs(VIDEO_SEGMENT_DIR)

def generate_segments(video_file):

    if video_file:
        hls_playlist = os.path.join(VIDEO_SEGMENT_DIR, 'playlist.m3u8')
        subprocess.run(['ffmpeg', '-i', video_file.filename, '-hls_time', '10', '-hls_list_size', '0', '-hls_segment_filename',
                        os.path.join(VIDEO_SEGMENT_DIR, 'segment%03d.ts'), '-f', 'hls', hls_playlist])

        return jsonify({'message': 'Segement generation complete', 'segments': hls_playlist}), 200
    else:
        return jsonify({'error': 'Video file missing'}), 400

if __name__ == '__main__':
    with Connection(redis_conn):
        print('Video Segmenter Worker is running...')
        while True:
            job = q.dequeue()
            if job is not None:
                video_path = job.args[0]
                generate_segments(video_path)
                job.delete()

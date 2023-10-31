import subprocess
import os
from rq import Worker, Queue, Connection
from redis import Redis


CONVERTED_VIDEO_DIR = 'converted_videos'

redis_conn = Redis(host='localhost', port=6379)

q = Queue('video_conversion', connection=redis_conn)

if not os.path.exists(CONVERTED_VIDEO_DIR):
    os.makedirs(CONVERTED_VIDEO_DIR)

def convert_video(video_file):
    if video_file:
        video_path = os.path.join(CONVERTED_VIDEO_DIR, video_file.filename.replace('...', '.mp4'))
        video_file.save(video_path)

        subprocess.run(['ffmpeg', '-i', video_path, '-c:v', 'libx264', '-crf', '23', '-c:a', 'aac', video_path])

        return 'Video conversion complete. Converted video path: ' + video_path
    else:
        return 'Video file missing'

if __name__ == '__main__':
    with Connection(redis_conn):
        print('Video Conversion Worker is running...')
        worker = Worker(['video_conversion'])
        worker.work()

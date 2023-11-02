import subprocess
import os
from rq import Worker, Queue, Connection
from redis import Redis
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='app.log',
                    filemode='a')


CONVERTED_VIDEO_DIR = 'converted_videos'

redis_conn = Redis(host='localhost', port=6379)

q = Queue('video_conversion', connection=redis_conn)

if not os.path.exists(CONVERTED_VIDEO_DIR):
    os.makedirs(CONVERTED_VIDEO_DIR)

def convert_video(video_filename):
    if os.path.exists(video_filename):
        logging.info(f"Started processing converting job for video: {video_filename}")
        output_video_path = os.path.join(CONVERTED_VIDEO_DIR, os.path.basename(video_filename).replace('.mp4', '_converted.mp4'))
        subprocess.run(['ffmpeg', '-i', video_filename, '-c:v', 'libx264', '-crf', '23', '-c:a', 'aac', output_video_path])

        logging.info(f"Completed processing converting job for video: {video_filename}")
        return 'Video conversion complete. Converted video path: ' + output_video_path
    else:
        return 'Video file missing'

if __name__ == '__main__':
    with Connection(redis_conn):
        print('Video Conversion Worker is running...')
        worker = Worker(['video_conversion'])
        worker.work()

import subprocess
import os
from redis import Redis
import logging
import boto3
import time

AWS_ACCESS_KEY_ID = 'AKIASQQQG2XF4V573GL6'
AWS_SECRET_ACCESS_KEY = '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'
AWS_BUCKET_NAME = 'flasks3scalable'

s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='app.log',
                    filemode='a')


VIDEO_SEGMENT_DIR = 'video_segments'

redis_conn = Redis(host='localhost', port=6379)

if not os.path.exists(VIDEO_SEGMENT_DIR):
    os.makedirs(VIDEO_SEGMENT_DIR)

def generate_segments(video_filename):
    # Downloading the video from S3 to local
    download_path = os.path.join(VIDEO_SEGMENT_DIR, video_filename)
    try:
        s3_client.download_file(AWS_BUCKET_NAME, video_filename, download_path)
    except Exception as e:
        logging.error(f"Error during download from S3: {e}")
        return
    
    if os.path.exists(download_path):
        logging.info(f"Started processing chunking job for video: {video_filename}")
        hls_playlist = os.path.join(VIDEO_SEGMENT_DIR, os.path.basename(video_filename).replace('.mp4', '.m3u8'))
        
        subprocess.run(['ffmpeg', '-i', download_path, '-hls_time', '10', '-hls_list_size', '0', '-hls_segment_filename',
                        os.path.join(VIDEO_SEGMENT_DIR, os.path.basename(video_filename).replace('.mp4', '') + '_%03d.ts'), '-f', 'hls', hls_playlist])
        
        logging.info(f"Completed processing chunking job for video: {video_filename}")
        
        # Upload the segments and the playlist to S3
        for segment_file in os.listdir(VIDEO_SEGMENT_DIR):
            if segment_file.endswith('.ts') or segment_file.endswith('.m3u8'):
                with open(os.path.join(VIDEO_SEGMENT_DIR, segment_file), 'rb') as file:
                    s3_client.upload_fileobj(file, AWS_BUCKET_NAME, segment_file)
        
        # Delete local files
        os.remove(download_path)
        for segment_file in os.listdir(VIDEO_SEGMENT_DIR):
            if segment_file.endswith('.ts') or segment_file.endswith('.m3u8'):
                os.remove(os.path.join(VIDEO_SEGMENT_DIR, segment_file))
        
                redis_conn.rpush('thumbnail', os.path.basename(video_filename))
        print('Segment generation complete', 'segments ' + hls_playlist)
    else:
        print('Video file missing')

def process_queue():
    print('Starting chunker...')
    while True:
        video_name = redis_conn.lpop('chunker')
        if video_name:
            video_name = video_name.decode('utf-8')
            generate_segments(video_name)
        else:
            time.sleep(10)  # Add a delay to avoid hammering the Redis server

if __name__ == '__main__':
    process_queue()





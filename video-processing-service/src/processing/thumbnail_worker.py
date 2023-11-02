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


redis_conn = Redis(host='localhost', port=6379)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='app.log',
                    filemode='a')


THUMBNAIL_DIR = 'thumbnails'

if not os.path.exists(THUMBNAIL_DIR):
    os.makedirs(THUMBNAIL_DIR)

def generate_thumbnail(video_filename):
    # Downloading the video from S3 to local
    download_path = os.path.join(THUMBNAIL_DIR, video_filename)
    try:
        s3_client.download_file(AWS_BUCKET_NAME, video_filename, download_path)
    except Exception as e:
        logging.error(f"Error during download from S3: {e}")
        return
    
    if os.path.exists(download_path):
        logging.info(f"Started processing thumbnail job for video: {video_filename}")
        thumbnail_path = os.path.join(THUMBNAIL_DIR, os.path.basename(video_filename).replace('.mp4', '.jpg'))
        subprocess.run(['ffmpeg', '-i', download_path, '-ss', '00:00:10', '-vframes', '1', '-q:v', '2', thumbnail_path])
        
        # Upload the thumbnail to S3
        with open(thumbnail_path, 'rb') as file:
            s3_client.upload_fileobj(file, AWS_BUCKET_NAME, os.path.basename(thumbnail_path))
        
        # Delete local files
        os.remove(download_path)
        os.remove(thumbnail_path)
        
        logging.info(f"Completed processing thumbnail job for video: {video_filename}")
        print('Thumbnail generation complete', 'thumbnail_path ' + thumbnail_path)
    else:
        print('Video file missing')

def process_queue():
    print('Starting thumbnail workers...')
    while True:
        video_name = redis_conn.lpop('thumbnail')
        if video_name:
            video_name = video_name.decode('utf-8')
            generate_thumbnail(video_name)
        else:
            time.sleep(10)  # Add a delay to avoid hammering the Redis server

if __name__ == '__main__':
    process_queue()




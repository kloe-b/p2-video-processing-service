import subprocess
import os
from redis import Redis
import logging
import boto3
import requests
import time

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_BUCKET_NAME = os.environ.get('AWS_BUCKET_NAME')

s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)


REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))

redis_conn = Redis(host=REDIS_HOST, port=REDIS_PORT)

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
            s3_client.upload_fileobj(
            Fileobj=file, 
            Bucket=AWS_BUCKET_NAME, 
            Key=os.path.basename(thumbnail_path),
            ExtraArgs={
                'ContentType': 'image/jpeg',
                'ContentDisposition': 'inline'
            }
        )

        # Delete local files
        os.remove(download_path)
        os.remove(thumbnail_path)
        
        logging.info(f"Completed processing thumbnail job for video: {video_filename}")

        request_data = {
            'video_filename': os.path.basename(video_filename),
            'thumbnail_filename': os.path.basename(thumbnail_path)
        }

        # Make the POST request to the user-service
        response = requests.post('http://user-service-service.default.svc:8080/api/update-thumbnail', json=request_data)
        if response.status_code == 200:
            logging.info('Thumbnail filename updated successfully')
        else:
            logging.error(f'Failed to update thumbnail filename: {response.content}')

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




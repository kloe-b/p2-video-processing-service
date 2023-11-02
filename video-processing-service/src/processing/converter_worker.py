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


CONVERTED_VIDEO_DIR = 'converted_videos'


redis_conn = Redis(host='localhost', port=6379)

if not os.path.exists(CONVERTED_VIDEO_DIR):
    os.makedirs(CONVERTED_VIDEO_DIR)

def convert_video(video_filename):
    download_path = os.path.join(CONVERTED_VIDEO_DIR, video_filename)
    
    try:
        with open(download_path, 'wb') as data:
            s3_client.download_fileobj(AWS_BUCKET_NAME, video_filename, data)
    except Exception as e:
        logging.error(f"Error during download: {e}")
        return 'Error during download'

    if os.path.exists(download_path) and os.path.getsize(download_path) > 0:
        logging.info(f"Started processing converting job for video: {video_filename}")
        
        output_video_path = os.path.join(CONVERTED_VIDEO_DIR, os.path.basename(video_filename).replace('.mp4', '_converted.mp4'))
        subprocess.run(['ffmpeg', '-y', '-i', download_path, '-c:v', 'libx264', '-crf', '23', '-c:a', 'aac', output_video_path])
        
        # Upload the converted video to S3
        with open(output_video_path, 'rb') as file:
            s3_client.upload_fileobj(file, AWS_BUCKET_NAME, os.path.basename(output_video_path))
        
        logging.info(f"Completed processing converting job for video: {video_filename}")
        print('Video conversion complete. Converted video path: ' + output_video_path)
        
        # Pushing the filename to 'chunker' and 'thumbnail'
        redis_conn.rpush('chunker', os.path.basename(output_video_path))
        
        # Deleting the converted file after upload
        os.remove(download_path)
        os.remove(output_video_path)

        # # Delete the original file from S3
        # s3_client.delete_object(Bucket=AWS_BUCKET_NAME, Key=video_filename)
    else:
        print('Video file missing')

def process_queue():
    print('Starting converter...')
    while True:
        video_name = redis_conn.lpop('video_name')
        if video_name:
            video_name = video_name.decode('utf-8')
            convert_video(video_name)
        else:
            time.sleep(10)  # Add a delay to avoid hammering the Redis server

if __name__ == '__main__':
    process_queue()







import boto3
from rq import Queue
from redis import Redis
import logging
import os
from converter_worker import convert_video
from segmenter_worker import generate_segments
from thumbnail_worker import generate_thumbnail

AWS_ACCESS_KEY_ID = 'AKIASQQQG2XF4V573GL6'
AWS_SECRET_ACCESS_KEY = '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'
AWS_BUCKET_NAME = 'flasks3scalable'

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler('app.log', 'a'),
                              logging.StreamHandler()])


s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
redis_conn = Redis(host='localhost', port=6379)
video_conversion_queue = Queue('video_conversion', connection=redis_conn)
thumbnail_generation_queue = Queue('thumbnail_generation', connection=redis_conn)
video_chunking_queue = Queue('video_chunking', connection=redis_conn)

DOWNLOAD_DIR = 'downloaded_videos'

if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

def process_video(video_details):
    download_path = os.path.join(DOWNLOAD_DIR, video_details)
    
    try:
        with open(download_path, 'wb') as data:
            s3_client.download_fileobj(AWS_BUCKET_NAME, video_details, data)
    except Exception as e:
        logging.error(f"Error during download: {e}")
        return 'Error during download'

    if os.path.exists(download_path) and os.path.getsize(download_path) > 0:
        try:
            job1 = video_conversion_queue.enqueue(convert_video, download_path)
            logging.info(f"Enqueued video converting job with ID: {job1.id} for video: {download_path}")

            job2 = thumbnail_generation_queue.enqueue(generate_thumbnail, download_path)
            logging.info(f"Enqueued video thumbnail job with ID: {job2.id} for video: {download_path}")

            job3 = video_chunking_queue.enqueue(generate_segments, download_path)
            logging.info(f"Enqueued video chunking job with ID: {job3.id} for video: {download_path}")
        except Exception as e:
            logging.error(f"Error during enqueueing jobs: {e}")
            return 'Error during enqueueing jobs'

        return 'Video processing complete'
    else:
        logging.error(f"Failed to download video or video is empty: {video_details}")
        return 'Video file missing'


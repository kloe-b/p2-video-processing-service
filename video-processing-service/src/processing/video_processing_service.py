import boto3
from rq import Queue
from redis import Redis

AWS_ACCESS_KEY_ID = 'AKIASQQQG2XF4V573GL6'  
AWS_SECRET_ACCESS_KEY = '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'  
AWS_BUCKET_NAME = 'flasks3scalable'

s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
redis_conn = Redis(host='localhost', port=6379)
video_conversion_queue = Queue('video_conversion', connection=redis_conn)
thumbnail_generation_queue = Queue('thumbnail_generation', connection=redis_conn)
video_chunking_queue = Queue('video_chunking', connection=redis_conn)

def process_video(video_details):
    with open(video_details, 'wb') as data:
        video=s3_client.download_fileobj(AWS_BUCKET_NAME, video_details, data)
        data.seek(0)
    if video:
        video_conversion_queue.enqueue(convert_video, video)
        thumbnail_generation_queue.enqueue(generate_thumbnail, video)
        video_chunking_queue.enqueue(generate_segments, video)
        return 'Video processing complete'
    else:
        return 'Video file missing'
    

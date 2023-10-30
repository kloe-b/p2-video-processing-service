import boto3
from rq import Queue
from redis import Redis
from processing import convert_video,generate_segments, generate_thumbnail
from flask import Flask, request, jsonify

app = Flask(__name__)

AWS_ACCESS_KEY_ID = 'AKIASQQQG2XF4KSBPOMG'  
AWS_SECRET_ACCESS_KEY = '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'  
AWS_BUCKET_NAME = 'flasks3scalable' 

s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
redis_conn = Redis(host='localhost', port=6379)
video_conversion_queue = Queue('video_conversion', connection=redis_conn)
thumbnail_generation_queue = Queue('thumbnail_generation', connection=redis_conn)
video_chunking_queue = Queue('video_chunking', connection=redis_conn)

def process_video(video_details):
    with open(video_details, 'wb') as data:
        video=s3_client.s3.download_fileobj(AWS_BUCKET_NAME, video_details, data)
        data.seek(0)
    if video:
        video_conversion_queue.enqueue(convert_video, video)
        thumbnail_generation_queue.enqueue(generate_thumbnail, video)
        video_chunking_queue.enqueue(generate_segments, video)
        return jsonify({'message': 'Video processing complete'}), 200
    else:
        return jsonify({'error': 'Video file missing'}), 400
    
if __name__ == '__main__':
    app.run(debug=True)

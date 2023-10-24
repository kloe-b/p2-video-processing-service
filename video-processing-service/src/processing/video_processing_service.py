import subprocess
import os
import boto3
from botocore.exceptions import NoCredentialsError
from flask import Flask, request, jsonify

app = Flask(__name__)

SECRET_KEY = 'your_secret_key'

AWS_ACCESS_KEY_ID = 'AKIASQQQG2XF4KSBPOMG'  
AWS_SECRET_ACCESS_KEY = 'd78LendV+ExAfroowAQkIL3tN+YyNviJOANolBz4'  
AWS_BUCKET_NAME = 'flasks3scalable' 

s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

VIDEO_SEGMENT_DIR = 'video_segments'
THUMBNAIL_DIR = 'thumbnails'

if not os.path.exists(VIDEO_SEGMENT_DIR):
    os.makedirs(VIDEO_SEGMENT_DIR)

if not os.path.exists(THUMBNAIL_DIR):
    os.makedirs(THUMBNAIL_DIR)

@app.route('/process', methods=['POST'])
def process_video():
    video_file = request.files['video']
    if video_file:
        video_path = os.path.join(VIDEO_SEGMENT_DIR, video_file.filename)
        video_file.save(video_path)

        subprocess.call(f'ffmpeg -i {video_path} -hls_time 10 -hls_list_size 0 -hls_segment_filename '
                        f'{VIDEO_SEGMENT_DIR}/segment%03d.ts -f hls {VIDEO_SEGMENT_DIR}/playlist.m3u8', shell=True)

        thumbnail_path = os.path.join(THUMBNAIL_DIR, video_file.filename.replace('.mp4', '.jpg'))
        subprocess.call(f'ffmpeg -i {video_path} -ss 00:00:10 -vframes 1 -q:v 2 {thumbnail_path}', shell=True)
        upload_file_to_s3(f'{VIDEO_SEGMENT_DIR}/', AWS_BUCKET_NAME, 'video_segments/')
        upload_file_to_s3(f'{THUMBNAIL_DIR}/', AWS_BUCKET_NAME, 'thumbnails/')

        return jsonify({'message': 'Video processing complete'}), 200
    else:
        return jsonify({'error': 'Video file missing'}), 400
    
def upload_file_to_s3(local_path, bucket, s3_path):
    try:
        for root, dirs, files in os.walk(local_path):
            for file in files:
                local_file_path = os.path.join(root, file)
                s3_key = os.path.join(s3_path, file)
                s3_client.upload_file(local_file_path, bucket, s3_key)
    except NoCredentialsError:
        return jsonify({'error': 'AWS credentials not found'}), 400

if __name__ == '__main__':
    app.run(debug=True)

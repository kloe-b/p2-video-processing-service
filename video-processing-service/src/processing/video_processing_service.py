import subprocess
import os
import redis 
import boto3
from database import Video, db
from flask import Flask, request, jsonify

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://dev:devpass@localhost:3306/p2-database'
db.init_app(app)

REDIS_HOST = '...'
REDIS_PORT = ...  
REDIS_CHANNEL = '...'

SECRET_KEY = 'your_secret_key'

AWS_ACCESS_KEY_ID = 'AKIASQQQG2XF4KSBPOMG'  
AWS_SECRET_ACCESS_KEY = 'd78LendV+ExAfroowAQkIL3tN+YyNviJOANolBz4'  
AWS_BUCKET_NAME = 'flasks3scalable' 

s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

VIDEO_SEGMENT_DIR = 'video_segments'
THUMBNAIL_DIR = 'thumbnails'
VIDEO_CONVERTS_DIR = 'converts'

if not os.path.exists(VIDEO_CONVERTS_DIR):
    os.makedirs(VIDEO_CONVERTS_DIR)

if not os.path.exists(VIDEO_SEGMENT_DIR):
    os.makedirs(VIDEO_SEGMENT_DIR)

if not os.path.exists(THUMBNAIL_DIR):
    os.makedirs(THUMBNAIL_DIR)

@app.route('/process', methods=['POST'])
def process_video():
    video_id = request.form.get('video_id') 

    video=s3_client.download_fileobj(AWS_BUCKET_NAME, video_id)
    if video:
        video_path = video.video_path 
        converted_video_path = os.path.join(VIDEO_CONVERTS_DIR, video.filename.replace('.mov', '.mp4'))
        subprocess.run(['ffmpeg', '-i', video_path, '-c:v', 'libx264', '-crf', '23', '-c:a', 'aac', converted_video_path])
   
        thumbnail_path = os.path.join(THUMBNAIL_DIR, video.replace('.mp4', '.jpg'))
        subprocess.run(['ffmpeg', '-i', video_path, '-ss', '00:00:10', '-vframes', '1', '-q:v', '2', thumbnail_path])

        hls_playlist = os.path.join(VIDEO_SEGMENT_DIR, 'playlist.m3u8')
        subprocess.run(['ffmpeg', '-i', video_path, '-hls_time', '10', '-hls_list_size', '0', '-hls_segment_filename',
                        os.path.join(VIDEO_SEGMENT_DIR, 'segment%03d.ts'), '-f', 'hls', hls_playlist])

        process_video = Video( thumbnail_path,hls_playlist)
        db.session.add(process_video)
        db.session.commit()
        return jsonify({'message': 'Video processing complete'}), 200
    else:
        return jsonify({'error': 'Video file missing'}), 400
    
if __name__ == '__main__':
    app.run(debug=True)

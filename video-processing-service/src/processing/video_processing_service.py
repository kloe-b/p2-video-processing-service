from flask import Flask, request, jsonify
import subprocess  
import os

app = Flask(__name__)

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

        return jsonify({'message': 'Video processing complete'}), 200
    else:
        return jsonify({'error': 'Video file missing'}), 400

if __name__ == '__main__':
    app.run(debug=True)

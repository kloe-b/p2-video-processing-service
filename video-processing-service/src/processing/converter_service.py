from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

CONVERTED_VIDEO_DIR = 'converted_videos'

if not os.path.exists(CONVERTED_VIDEO_DIR):
    os.makedirs(CONVERTED_VIDEO_DIR)

@app.route('/convert', methods=['POST'])
def convert_video():
    video_file = request.files['video']
    if video_file:
        video_path = os.path.join(CONVERTED_VIDEO_DIR, video_file.filename.replace('...', '.mp4'))
        video_file.save(video_path)

        subprocess.run(['ffmpeg', '-i', video_path, '-c:v', 'libx264', '-crf', '23', '-c:a', 'aac', video_path])

        return jsonify({'message': 'Video conversion complete', 'converted_video_path': video_path}), 200
    else:
        return jsonify({'error': 'Video file missing'}), 400

if __name__ == '__main__':
    app.run(debug=True)

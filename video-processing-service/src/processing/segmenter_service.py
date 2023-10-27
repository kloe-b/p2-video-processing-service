from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

VIDEO_SEGMENT_DIR = 'video_segments'

if not os.path.exists(VIDEO_SEGMENT_DIR):
    os.makedirs(VIDEO_SEGMENT_DIR)

@app.route('/generate_segments', methods=['POST'])
def generate_segments():
    video_file = request.files['video']
    if video_file:
        hls_playlist = os.path.join(VIDEO_SEGMENT_DIR, 'playlist.m3u8')
        subprocess.run(['ffmpeg', '-i', video_file.filename, '-hls_time', '10', '-hls_list_size', '0', '-hls_segment_filename',
                        os.path.join(VIDEO_SEGMENT_DIR, 'segment%03d.ts'), '-f', 'hls', hls_playlist])

        return jsonify({'message': 'Segement generation complete', 'segments': hls_playlist}), 200
    else:
        return jsonify({'error': 'Video file missing'}), 400

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, request, Response
import subprocess
import os

app = Flask(__name__)

# YouTube RTMP URL (replace with your stream key)
youtube_rtmp_url = "rtmp://a.rtmp.youtube.com/live2/YOUR_STREAM_KEY"

# FFmpeg command to stream to YouTube
ffmpeg_command = [
    'ffmpeg',
    '-f', 'image2pipe',  # Input format (images piped from stdin)
    '-r', '1',           # Frame rate (1 frame per second)
    '-i', '-',           # Input from stdin
    '-c:v', 'libx264',   # Video codec
    '-preset', 'fast',   # Encoding speed
    '-pix_fmt', 'yuv420p',  # Pixel format
    '-f', 'flv',         # Output format (RTMP)
    youtube_rtmp_url     # YouTube RTMP URL
]

# Start FFmpeg process
ffmpeg_process = subprocess.Popen(ffmpeg_command, stdin=subprocess.PIPE)

@app.route('/upload', methods=['POST'])
def upload():
    try:
        # Get the image from the request
        image = request.data

        # Write the image to FFmpeg's stdin
        ffmpeg_process.stdin.write(image)
        ffmpeg_process.stdin.flush()

        return "Image received and streamed!", 200
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
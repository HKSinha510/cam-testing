from flask import Flask, request, Response
import subprocess
import logging
from threading import Lock, Thread
import time

app = Flask(__name__)

# Enable detailed logging
logging.basicConfig(level=logging.DEBUG)

# YouTube RTMP URL (replace with your stream key)
youtube_rtmp_url = "rtmp://a.rtmp.youtube.com/live2/YOUR_STREAM_KEY"

# FFmpeg command to stream to YouTube
ffmpeg_command = [
    'ffmpeg',
    '-f', 'image2pipe',  # Input format (images piped from stdin)
    '-r', '5',           # Frame rate (5 frames per second)
    '-i', '-',           # Input from stdin
    '-c:v', 'libx264',   # Video codec
    '-preset', 'fast',   # Encoding speed
    '-pix_fmt', 'yuv420p',  # Pixel format
    '-f', 'flv',         # Output format (RTMP)
    youtube_rtmp_url     # YouTube RTMP URL
]

# Start FFmpeg process with binary stdin
ffmpeg_process = subprocess.Popen(
    ffmpeg_command,
    stdin=subprocess.PIPE,  # Binary input
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Lock to ensure thread-safe writes to FFmpeg's stdin
ffmpeg_lock = Lock()

# Function to log FFmpeg output
def log_ffmpeg_output():
    while True:
        stdout = ffmpeg_process.stdout.readline()
        stderr = ffmpeg_process.stderr.readline()
        if stdout:
            app.logger.debug("FFmpeg stdout: " + stdout.decode().strip())
        if stderr:
            app.logger.error("FFmpeg stderr: " + stderr.decode().strip())
        if ffmpeg_process.poll() is not None:
            app.logger.error("FFmpeg process has terminated")
            break
        time.sleep(0.1)

# Start a thread to log FFmpeg output
ffmpeg_log_thread = Thread(target=log_ffmpeg_output)
ffmpeg_log_thread.daemon = True
ffmpeg_log_thread.start()

@app.route('/upload', methods=['POST'])
def upload():
    try:
        # Get the image from the request
        image = request.data
        app.logger.debug(f"Received image of size: {len(image)} bytes")

        # Write the binary image data to FFmpeg's stdin
        with ffmpeg_lock:
            ffmpeg_process.stdin.write(image)
            ffmpeg_process.stdin.flush()

        return "Image received and streamed!", 200
    except Exception as e:
        app.logger.error(f"Error: {str(e)}")
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
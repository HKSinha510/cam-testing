from flask import Flask, request, Response
import subprocess
import logging

app = Flask(__name__)

# Enable detailed logging
logging.basicConfig(level=logging.DEBUG)

# YouTube RTMP URL (replace with your stream key)
youtube_rtmp_url = "rtmp://a.rtmp.youtube.com/live2/6t3p-vkv2-m8fm-m9gp-brab"

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

# Start FFmpeg process with logging
ffmpeg_process = subprocess.Popen(
    ffmpeg_command,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

@app.route('/upload', methods=['POST'])
def upload():
    try:
        # Get the image from the request
        image = request.data
        app.logger.debug(f"Received image of size: {len(image)} bytes")

        # Write the image to FFmpeg's stdin
        ffmpeg_process.stdin.write(str(image))
        ffmpeg_process.stdin.flush()

        # Log FFmpeg output and errors
        stdout, stderr = ffmpeg_process.communicate(timeout=5)
        app.logger.debug("FFmpeg stdout: " + stdout)
        app.logger.debug("FFmpeg stderr: " + stderr)

        return "Image received and streamed!", 200
    except Exception as e:
        app.logger.error(f"Error: {str(e)}")
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
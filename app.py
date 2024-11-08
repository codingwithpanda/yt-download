from flask import Flask, render_template, request, jsonify, send_file
from yt_dlp import YoutubeDL
import os

app = Flask(__name__)

# Directory for saving downloaded videos
DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# Fetch available formats for a given video URL
def get_formats(url):
    with YoutubeDL() as ydl:
        info_dict = ydl.extract_info(url, download=False)
        formats = [
            {
                'format_id': fmt['format_id'],
                'resolution': fmt.get('format_note', 'unknown'),
                'ext': fmt['ext']
            }
            for fmt in info_dict['formats'] if fmt['vcodec'] != 'none'
        ]
    return formats

# Route for the main page
@app.route('/')
def index():
    return render_template('index.html')

# Endpoint to retrieve formats based on URL
@app.route('/get_formats', methods=['POST'])
def get_formats_route():
    url = request.json['url']
    formats = get_formats(url)
    return jsonify(formats)

# Route to download video based on selected format
@app.route('/download', methods=['POST'])
def download():
    url = request.json['url']
    format_id = request.json['format_id']
    output_path = os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s')

    ydl_opts = {
        'format': f'{format_id}+bestaudio',  # Download selected video format with best audio
        'outtmpl': output_path,
        'postprocessors': [
            {
                'key': 'FFmpegVideoConvertor',  # Merge video and audio
                'preferedformat': 'mp4'  # Convert to mp4 format
            }
        ],
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url)
            filename = ydl.prepare_filename(info_dict).replace(".webm", ".mp4")  # Final file name in mp4 format

        return send_file(filename, as_attachment=True)  # Serve the file for download
    except Exception as e:
        return jsonify({"status": f"An error occurred: {e}"}), 500

if __name__ == "__main__":
    app.run(debug=True)

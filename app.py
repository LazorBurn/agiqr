import os
import qrcode
import logging
import re
from flask import Flask, request, render_template, url_for, send_from_directory, jsonify
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def sanitize_filename(input_string):
    """
    Sanitize the input string to create a safe filename.
    Removes invalid characters for both Windows and Linux.
    """
    return re.sub(r'[<>:"/\\|?*]', '_', input_string)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.form['data']
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

        # Sanitize the input data for a valid filename
        sanitized_data = sanitize_filename(data).replace(' ', '_')[:10]
        filename = f"qr_{timestamp}_{sanitized_data}.png"

        # Create QR Code instance
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill='black', back_color='white')

        # Ensure the 'static' directory exists
        base_dir = os.path.dirname(os.path.abspath(__file__))  # Get the script directory
        img_dir = os.path.join(base_dir, 'static')
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)

        img_path = os.path.join(img_dir, filename)
        app.logger.debug(f"Saving QR code to: {img_path}")  # Debugging line
        img.save(img_path)

        # Pass the correct img_path to the template
        return render_template('index.html', img_path=url_for('static', filename=filename))
    return render_template('index.html')

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/list-static')
def list_static_files():
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    files = os.listdir(static_dir)
    return jsonify(files)

if __name__ == '__main__':
    app.run(debug=True)

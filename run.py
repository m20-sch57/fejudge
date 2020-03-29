import os
from app import app


if not os.path.exists(app.config['SUBMISSIONS_LOG_PATH']):
    os.makedirs(app.config['SUBMISSIONS_LOG_PATH'])
if not os.path.exists(app.config['SUBMISSIONS_DOWNLOAD_PATH']):
    os.makedirs(app.config['SUBMISSIONS_DOWNLOAD_PATH'])
if not os.path.exists(app.config['PROBLEMS_UPLOAD_PATH']):
    os.makedirs(app.config['PROBLEMS_UPLOAD_PATH'])
if not os.path.exists(app.config['PROBLEMS_PATH']):
    os.makedirs(app.config['PROBLEMS_PATH'])

app.run(host='0.0.0.0', port=3013, debug=True)

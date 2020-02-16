import os
import threading

from app import app
from judge import judge


def run_app():
    app.run(host='0.0.0.0', port=3013, debug=False, threaded=True)

def run_judge():
    judge.run(host='0.0.0.0', port=3113)


# if not os.path.exists(app.config['SUBMISSIONS_EXEC_PATH']):
#     os.makedirs(app.config['SUBMISSIONS_EXEC_PATH'])
if not os.path.exists(app.config['SUBMISSIONS_LOG_PATH']):
    os.makedirs(app.config['SUBMISSIONS_LOG_PATH'])
if not os.path.exists(app.config['SUBMISSIONS_DOWNLOAD_PATH']):
    os.makedirs(app.config['SUBMISSIONS_DOWNLOAD_PATH'])


t1 = threading.Thread(target=run_app)
t2 = threading.Thread(target=run_judge)
t1.start()
t2.start()

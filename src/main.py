import json
import os

import nltk
from waitress import serve

from src.user_interface import run

if __name__ == '__main__':
    nltk.download('punkt')

    with open(run.CONFIG_FILE) as f:
        config = json.load(f)
    port = config['port']
    run.app.secret_key = config['flask_secret_key']

    if 'mode' in os.environ and os.environ['mode'] == 'DEV':
        run.app.run(port=port)
    else:
        serve(run.app, host="0.0.0.0", port=port)

from flask import (
    Flask,
    request
)
import subprocess

import logging
log = logging.getLogger(__name__)

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"

@app.route("/register", methods=['POST'])
def register():
    try:
        hostname = request.json['public']
        subprocess.Popen(["./env/bin/fab","-H",hostname,"deploy"])
        return "ok"
    except Exception, e:
        return "ko"


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')
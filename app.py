from flask import (
    Flask,
    request,
    send_file
)
app = Flask(__name__)

from PIL import Image
import requests
import mimetypes


@app.route("/")
def hello():
    return "Hello World!"

@app.route("/resize")
def resize():
    """
    /resize/url=http://www.google.com/intl/en_ALL/images/logo.gif&size=200x200

    """
    url = request.args.get('url', 'http://www.google.com/intl/en_ALL/images/logo.gif')
    size = request.args.get('size', '200x200')

    try:
        filename = url.split('/')[-1]
        mimetype = mimetypes.guess_type(url)

        rep = requests.get(url)
        path = '/tmp/{}'.format(filename)
        outfile = '/tmp/resized_{}'.format(filename)

        with open(path, 'w') as f:
            f.write(rep.content)

        tuple_size = map(int, size.split('x'))

        im = Image.open(path)
        out = im.resize(tuple_size)
        out.save(outfile)
        return send_file(outfile, mimetype=mimetype[0])

    except Exception, e:
        return e.message


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')
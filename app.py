from flask import (
    Flask,
    request,
    send_file
)
app = Flask(__name__)

from PIL import Image
import requests
import mimetypes
import uuid


@app.route("/")
def hello():
    return "Hello World!"

@app.route("/mandelbrot")
def resize():
    """
    from http://code.activestate.com/recipes/577111-mandelbrot-fractal-using-pil/
    /mandelbrot

    """
    #url = request.args.get('url', 'http://www.google.com/intl/en_ALL/images/logo.gif')
    #size = request.args.get('size', '200x200')

    try:

        # Mandelbrot fractal
        # FB - 201003151
        # Modified Andrew Lewis 2010/04/06
        # drawing area (xa < xb and ya < yb)
        xa = -2.0
        xb = 1.0
        ya = -1.5
        yb = 1.5
        maxIt = 256 # iterations
        # image size
        imgx = 512
        imgy = 512

        #create mtx for optimized access
        image = Image.new("RGB", (imgx, imgy))
        mtx = image.load()

        #optimizations
        lutx = [j * (xb-xa) / (imgx - 1) + xa for j in xrange(imgx)]

        for y in xrange(imgy):
            cy = y * (yb - ya) / (imgy - 1)  + ya
            for x in xrange(imgx):
                c = complex(lutx[x], cy)
                z = 0
                for i in xrange(maxIt):
                    if abs(z) > 2.0: break
                    z = z * z + c
                r = i % 4 * 64
                g = i % 8 * 32
                b = i % 16 * 16
                mtx[x, y] =  r,g,b

        base_name = str(uuid.uuid4())
        filename = '{}.png'.format(base_name)

        path = '/tmp/{}'.format(filename)

        image.save(path, "PNG")

        return send_file(path, mimetype="PNG")

    except Exception, e:
        return e.message


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')
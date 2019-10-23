
import logging
import threading
import os
import multiprocessing

try:
    import urllib.request as urlrequest
except ImportError:
    import urllib as urlrequest

from flask import Flask, request, render_template, Response

name = "touchy"


display_update_interval = 20
ajax_update_interval = 40

server_port = None
server_thread = None
server_terminate = False


class Controller:

    def __init__(self):
        self.stick = (0, 0)
        self.lock = multiprocessing.Lock()
        pass

    def setData(self, stick):
        with self.lock:
            self.stick = stick

    def getStick(self):
        with self.lock:
            return self.stick


dir_path = os.path.dirname(os.path.realpath(__file__))
templates_path = os.path.join(dir_path, "templates")
static_path = os.path.join(dir_path, "static")


controller = Controller()
app = Flask("Touchy", template_folder=templates_path)


def read_file_contents(fname):
    with open(fname, 'rb') as content_file:
        return content_file.read()


def http_thread(port, host):
    app.run(debug=False, port=port, host=host)


@app.route('/shutdown')
def http_shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is not None:
        func()
    return 'Server shutting down...'


@app.route("/")
def http_index():
    return render_template(
        "touchy.html"
        , display_update_interval=display_update_interval
        , ajax_update_interval=ajax_update_interval
    )


@app.route("/api")
def http_api():

    if server_terminate:
        return http_shutdown()

    x = request.args.get("x")
    y = request.args.get("y")

    if x is not None and y is not None:
        controller.setData((float(x), float(y)))

    return "OK"


@app.route('/static', defaults={'path': ''})
@app.route('/static/<string:path>')
def http_static(path):  # pragma: no cover

    mimetypes = {
        ".css": "text/css",
        ".js": "application/javascript",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".html": "text/html",
    }

    complete_path = os.path.join(static_path, path)
    ext = os.path.splitext(path)[1]
    mimetype = mimetypes.get(ext, "text/html")

    try:
        content = read_file_contents(complete_path)
    except IOError as exc:
        content = str(exc)
        mimetype = "text/plain"

    return Response(content, mimetype=mimetype)


def start_server(port=80, host='0.0.0.0'):

    global server_port
    server_port = port

    # disable flask server info logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    # start webserver
    global server_thread
    server_thread = threading.Thread(target=http_thread, args=(port, host, ))
    server_thread.start()


def stop_server():

    global server_port
    global server_thread
    global server_terminate

    if server_thread is not None:

        server_terminate = True
        f = urlrequest.urlopen("http://127.0.0.1:" + str(server_port) + "/shutdown")
        f.read()

        server_thread.join()
        server_thread = None

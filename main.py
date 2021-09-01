import os
import socket
import jinja2
from flask import Flask, request
from flask import render_template
from pprint import pprint
import config

app = Flask(__name__)


@app.route("/")
def hello_world():
    hostname = socket.gethostname()
    pprint(dict(os.environ))
    return render_template('index.j2.html',
                           hostname=hostname,
                           headers=request.headers,
                           app_ip=os.environ.get('HELLO_WORLD_PORT', None),
                           svc_ip=os.environ.get('KUBERNETES_PORT', None),
                           )


if __name__ == '__main__':
    print(f'Ready to receive requests on {config.PORT}')
    app.run(host='0.0.0.0', port=config.PORT, threaded=True)

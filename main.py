import os
from wsgiref import simple_server
import socket
import jinja2
from flask import Flask, request
from flask import render_template
from pprint import pprint
import config


def load_template(name):
    path = os.path.join('templates', name)
    with open(os.path.abspath(path), 'r') as fp:
        return jinja2.Template(fp.read())


# class HelloResource(object):
#     def on_get(self, req, res):
#         hostname = socket.gethostname()
#
#         template = load_template('index.j2.html')
#         res.status = falcon.HTTP_200
#         res.content_type = 'text/html'
#         res.body = template.render(hostname=hostname, headers=req.headers)


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
    httpd = simple_server.make_server(config.HOST, config.PORT, app)
    print(f'Ready to receive requests on {config.PORT}')
    httpd.serve_forever()

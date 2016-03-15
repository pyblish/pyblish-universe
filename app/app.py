# Standard library
import sys
import json

# 3rd party
import flask
import flask.ext.restful
from firebase import firebase

# Local library
from . import log, formatting

app = flask.Flask(__name__)

this = sys.modules[__name__]
this.app = app
this.log = log


@app.route("/")
def home():
    return "<h3>Pyblish Universe</h3>"


class Handler(flask.ext.restful.Resource):
    def get(self):
        return "This is where you'll point events."

    def post(self):
        headers = flask.request.headers
        payload = flask.request.json

        print("An event came in!")
        print("headers: %s" % headers)
        print("payload: %s" % json.dumps(payload, indent=4))

        try:
            upayload = formatting.parse(headers, payload)
        except Exception as e:
            log.error(e)
            return str(e)

        firebase.FirebaseApplication(
            "https://pyblish-web.firebaseio.com").post(
                url="/events",
                data=upayload,
                params={'print': 'pretty'},
                headers={'X_FANCY_HEADER': 'VERY FANCY'},
                connection=None
        )

        return "%s received!" % json.dumps(upayload, indent=4)


api = flask.ext.restful.Api(app)
api.add_resource(Handler, "/handler")

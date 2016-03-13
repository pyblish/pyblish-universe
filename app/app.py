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
this.pages = {}
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
        print(json.dumps(payload, indent=4))

        event = headers.get("X-Github-Event")

        if event is None:
            log.error("unsupported event: %s" % event)
            return "Unsupported event: %s" % event

        event = formatting.convert_event(event) or event

        try:
            upayload = formatting.parse(payload, event)
        except KeyError:
            log.error("unsupported event: %s" % event)
            return "Unsupported event: %s" % event

        # Temporarily skip labels, they are sent once
        # per labelling of a new issue.
        if upayload["action"] == "labeled":
            log.warning("Skipping event: %s" % event)
            return "Skipping event: %s" % event

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

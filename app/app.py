# Standard library
import sys
import json

# 3rd party
import flask
import requests
import flask.ext.restful
from firebase import firebase

# Local library
from . import log

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
        return "<p>This is where you'll point GitHub Events</p>"

    def post(self):
        headers = flask.request.headers
        payload = flask.request.json
    
        print("An event came in!")
        print(json.dumps(payload, indent=4))

        if headers.get("X-Github-Event") == "gollum":
            for page in payload["pages"]:
                if page["action"] in ("created", "edited"):
                    payload = {
                        "icon": "book",
                        "event": "github-wiki",
                        "action": "(compare)",
                        "actionUrl": page["html_url"],
                        "author": payload["sender"]["login"],
                        "avatar": payload["sender"]["avatar_url"],
                        "message": "{action} {title} on {repo}".format(
                            action=page["action"].title(),
                            title=page["title"],
                            repo=payload["repository"]["full_name"]
                        ),
                        "target": page["html_url"],
                        "time": payload["repository"]["pushed_at"]
                    }

                    ref = firebase.FirebaseApplication('https://pyblish-web.firebaseio.com', None)
                    result = ref.post(
                        url="/events",
                        data=payload,
                        params={'print': 'pretty'},
                        headers={'X_FANCY_HEADER': 'VERY FANCY'},
                        connection=None
                    )

            return "Gollum edit received!"

        if headers.get("X-Github-Event") == "push":
            return "Push event received"


api = flask.ext.restful.Api(app)
api.add_resource(Handler, "/handler")
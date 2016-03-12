import json
import firebase

payload = {
    "action": "(compare)",
    "actionUrl": "https://github.com/pyblish",
    "author": "https://github.com/mottosso",
    "avatar": "https://avatars3.githubusercontent.com/u/243988...",
    "body": "add support for publish targets...",
    "event": "github-wiki",
    "icon": "book",
    "message": "on master",
    "target": "https://github.com/pyblish/pyblish/wiki",
    "time": "Mar 11"
}
print(json.dumps(payload, indent=4))

firebase = firebase.FirebaseApplication('https://pyblish-web.firebaseio.com', None)
result = firebase.post(
    url="/events",
    data=payload,
    params={'print': 'pretty'},
    headers={'X_FANCY_HEADER': 'VERY FANCY'},
    connection=None
)
print(result)

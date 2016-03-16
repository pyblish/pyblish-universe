import json
import requests
import datetime


def convert_event(headers, payload=None):
    """Convert external event signature to one compatible with Universe

    Arguments:
        event (str):

    Returns:
        Universe as str, or None if no event was recognised.

    """

    if "X-Github-Event" in headers:
        return {
            "gist": "github-gist",
            "ping": "github-ping",
            "commit_comment": "github-comment",
            "create": "github-create",
            "delete": "github-delete",
            "deployment": "github-deploy",
            "fork": "github-fork",
            "gollum": "github-wiki",
            "issue_comment": "github-comment",
            "issues": "github-issue",
            "member": "github-member",
            "membership": "github-member",
            "page_build": "github-page-build",
            "pull_request_review_comment": "github-comment",
            "pull_request": "github-pullrequest",
            "push": "github-push",
            "release": "github-release",
            "status": "github-status",
            "team_add": "github-team",
            "watch": "github-star"
        }.get(headers.get("X-Github-Event"), None)

    try:
        data = {}
        for item in payload:
            data.update(item)

        if "forums.pyblish.com" in data.get("referrer", ""):
            return "forum-newpost"

    except Exception as e:
        return None


def parse(headers, payload):
    """Parse `payload` based on type of `event`

    Arguments:
        payload (dict): Dictionary of payload
        event (str): Type of event

    Returns:
        dictionary of parsed payload, empty on failure.

    Raises:
        NotImplementedError on unsupported event

    """
    
    event = convert_event(headers, payload)
    
    if not event:
        raise NotImplementedError("%s not supported" % event)
    
    if event == "github-wiki":
        return github_wiki(payload)

    elif event == "github-issue":
        return github_issue(payload)

    elif event == "github-comment":
        return github_comment(payload)

    elif event == "github-star":
        return github_star(payload)

    elif event == "github-push":
        return github_push(payload)

    elif event == "forum-newpost":
        return forum_new_post(payload)
    
    elif event.startswith("github-"):
        return github_basics(event, payload)

    else:
        raise NotImplementedError("Unsupported event: %s" % event)


def github_basics(event, payload):
    return {
        "event": event,
        "author": payload["sender"]["login"],
        "avatar": payload["sender"]["avatar_url"],
        "message": "triggered \"{event}\" on".format(
            user=payload["sender"]["login"],
            event=event),
        "target": payload.get("repository", {}).get(
            "html_url", "https://github.com/pyblish"),
        "time": datetime.datetime.utcnow().isoformat()
    }


def github_wiki(payload):
    """Map GitHub wiki event to universe

    Arguments:
        payload (dict): GitHub event dictionary

    Returns:
        Modified payload (dict) if successful
        or None if unsuccessful

    """

    # Only bother with the first modified page
    page = next(iter(payload["pages"]), None)

    if page is None:
        raise TypeError("No page in edit, this is a bug")

    return {
        "event": "github-wiki",
        "author": payload["sender"]["login"],
        "avatar": payload["sender"]["avatar_url"],
        "message": "{action} {title} on {repo}".format(
            action=page["action"].title(),
            title=page["title"],
            repo=payload["repository"]["full_name"]
        ),
        "target": page["html_url"],
        "time": datetime.datetime.utcnow().isoformat()
    }


def github_comment(payload):
    data = {
        "event": "github-comment",
        "author": payload["sender"]["login"],
        "avatar": payload["sender"]["avatar_url"],
        "message": "commented on",
        "body": payload["comment"]["body"],
        "target": payload["comment"]["issue_url"],
        "time": datetime.datetime.utcnow().isoformat(),
    }
    
    if "issue" in payload:
        data.update({
        "labels": payload["issue"]["labels"]
        })
    
    return data


def github_issue(payload):
    data = {
        "event": "github-issue",
        "author": payload["sender"]["login"],
        "avatar": payload["sender"]["avatar_url"],
        "message": payload["action"],
        "body": payload["issue"]["body"],
        "target": payload["issue"]["html_url"],
        "time": datetime.datetime.utcnow().isoformat(),
        "labels": payload["issue"]["labels"]
    }
    

def github_star(payload):
    return {
        "event": "github-star",
        "author": payload["sender"]["login"],
        "avatar": payload["sender"]["avatar_url"],
        "message": "starred",
        "target": payload["repository"]["html_url"],
        "time": datetime.datetime.utcnow().isoformat(),
    }


def github_push(payload):
    return {
        "event": "github-push",
        "author": payload["sender"]["login"],
        "avatar": payload["sender"]["avatar_url"],
        "message": "pushed {commits} commit{plural} to".format(
            commits=len(payload["commits"]),
            plural="s" if len(payload["commits"]) > 1 else ""
        ),
        "body": "\n".join("- [{commit}]({commitUrl}) {message}".format(
            commit=commit["id"][:7],
            commitUrl=commit["url"],
            message=commit["message"])
                for commit in payload["commits"]),
        "target": payload["repository"]["html_url"],
        "time": datetime.datetime.utcnow().isoformat(),
    }


def forum_new_post(payload):
    """Parse webhook from forums
    
    The thing about forum events, is that they don't have any official API.
    Therefore, each event is potentially unique in its data layout.
    
    Reference:
        https://github.com/rcfox/Discourse-Webhooks

    """

    data = {}
    for item in payload:
        data.update(item)

    target = data.get("referrer")
    body = data.get("raw")
    time = data.get("updated_at", data.get("baked_at"))
    avatar_id = data.get("uploaded_avatar_id")
    topic_id = data.get("topic_id")
    user = data.get("username")
    action = "replied to" if (data.get("post_type") == 1) else "created"
    avatar = "http://{base}/user_avatar/{base}/{user}/45/{id}_1.png".format(
        base="forums.pyblish.com",
        user=user,
        id=avatar_id
    )

    # Dig deeper to find subject line.    
    response = requests.get("http://forums.pyblish.com/t/{id}.json".format(id=topic_id))
    
    if response.status_code == 403:
        raise IOError("Event came from a private source, "
                      "such as a locked topic")

    elif response.status_code != 200:
        raise IOError("Event came from a post that could not be queried: %s"
                      % topic_id)

    title = response.json().get("fancy_title", "Unknown")

    return {
        "event": "forum-newpost",
        "author": user,
        "avatar": avatar,
        "message": action,
        "body": body,
        "target": target,
        "targetName": title,
        "time": time
    }

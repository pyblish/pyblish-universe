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
            "deployment_status": "github-deploy-status",
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
            "public": "github-repository-public",
            "repository": "github-repository-created",
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

    elif event == "github-issue-comment":
        return github_issue_comment(payload)

    elif event == "github-commit-comment":
        return github_commit_comment(payload)

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
    if event in ("github-page-build",):
        raise TypeError("Skipping %s event" % event)

    return {
        "event": event,
        "author": payload["sender"]["login"],
        "avatar": payload["sender"]["avatar_url"],
        "message": "triggered a \"{event}\" on {repo}".format(
            user=payload["sender"]["login"],
            event=event,
            repo=payload.get("repository", {}).get("full_name", "GitHub")),
        "target": payload.get("repository", {}).get(
            "full_name", "https://github.com/pyblish"),
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
        "time": datetime.datetime.utcnow().isoformat()
    }


def github_commit_comment(payload):
    return {
        "event": "github-commit-comment",
        "action": "(compare)",
        "actionUrl": payload["comment"]["html_url"],
        "author": payload["sender"]["login"],
        "avatar": payload["sender"]["avatar_url"],
        "message": "commented on commit {repo}".format(
            repo=payload["comment"]["full_name"]
        ),
        "target": payload["comment"]["html_url"],
        "time": datetime.datetime.utcnow().isoformat()
    }


def github_issue_comment(payload):
    return {
        "event": "github-issue-comment",
        "action": "Go to comment",
        "actionUrl": payload["comment"]["html_url"],
        "author": payload["sender"]["login"],
        "avatar": payload["sender"]["avatar_url"],
        "message": "commented on issue #{issue}".format(
            issue=payload["issue"]["number"]
        ),
        "body": payload["comment"]["body"],
        "target": payload["comment"]["issue_url"],
        "time": datetime.datetime.utcnow().isoformat(),
        "labels": payload["issue"]["labels"]
    }


def github_issue(payload):
    if payload["action"] == "labeled":
        # These are not important
        raise TypeError("Skipping labeling event")

    return {
        "event": "github-issue",
        "action": "Go to issue",
        "actionUrl": payload["issue"]["html_url"],
        "author": payload["sender"]["login"],
        "avatar": payload["sender"]["avatar_url"],
        "message": "{action} issue {title} (#{issue})".format(
            action=payload["action"],
            issue=payload["issue"]["number"],
            title=payload["issue"]["title"]
        ),
        "body": payload["issue"]["body"],
        "target": payload["issue"]["html_url"],
        "time": datetime.datetime.utcnow().isoformat(),
        "labels": payload["issue"]["labels"]
    }
    

def github_star(payload):
    return {
        "event": "github-star",
        "action": "Go to repository",
        "actionUrl": payload["repository"]["html_url"],
        "author": payload["sender"]["login"],
        "avatar": payload["sender"]["avatar_url"],
        "message": "starred {repo}".format(
            user=payload["sender"]["login"],
            repo=payload["repository"]["html_url"]
        ),
        "target": payload["repository"]["html_url"],
        "time": datetime.datetime.utcnow().isoformat(),
    }


def github_push(payload):
    return {
        "event": "github-push",
        "action": "Go to commit",
        "actionUrl": payload["repository"]["html_url"],
        "author": payload["sender"]["login"],
        "avatar": payload["sender"]["avatar_url"],
        "message": "pushed {commits} commits to {repo}".format(
            user=payload["sender"]["login"],
            commits=len(payload["commits"]),
            repo=payload["repository"]["html_url"]
        ),
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
    action = "replied" if (data.get("post_type") == 1) else "created"
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
        "action": "Go to post",
        "actionUrl": target,
        "author": "Marcus",
        "avatar": avatar,
        "message": "{action} to {subject}".format(
            user=user,
            action=action,
            subject=title
        ),
        "body": body,
        "target": target,
        "time": time
    }

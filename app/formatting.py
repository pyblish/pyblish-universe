import json
import datetime


def convert_event(headers):
    """Convert external event signature to one compatible with Universe

    Arguments:
        event (str):

    Returns:
        Universe as str, or None if no event was recognised.

    """

    print("Finding event from headers: %s" % json.dumps(headers, indent=4))

    if headers.get("X-Github-Event") == "gollum":
        return "github-wiki"

    if headers.get("X-Github-Event") == "issues":
        return "github-issue"

    if headers.get("X-Github-Event") == "issue_comment":
        return "github-issue-comment"

    if headers.get("X-Github-Event") == "commit_comment":
        return "github-commit-comment"


def parse(payload, event):
    """Parse `payload` based on type of `event`

    Arguments:
        payload (dict): Dictionary of payload
        event (str): Type of event

    Returns:
        dictionary of parsed payload, empty on failure.

    Raises:
        NotImplementedError on unsupported event

    """

    events = {
        "github-wiki": github_wiki,
        "github-issue": github_issue,
        "github-issue-comment": github_issue_comment,
        "github-commit-comment": github_commit_comment,
    }

    if event not in events:
        raise NotImplementedError("%s not supported" % event)

    return events[event](payload)


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
    return {
        "event": "github-issue",
        "action": "Go to issue",
        "actionUrl": payload["issue"]["html_url"],
        "author": payload["sender"]["login"],
        "avatar": payload["sender"]["avatar_url"],
        "message": "{action} issue #{issue} ({title})".format(
            action=payload["action"],
            issue=payload["issue"]["number"],
            title=payload["issue"]["title"]
        ),
        "body": payload["issue"]["body"],
        "target": payload["issue"]["html_url"],
        "time": datetime.datetime.utcnow().isoformat(),
        "labels": payload["issue"]["labels"]
    }

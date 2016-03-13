/*global Firebase*/
/*global Handlebars*/


(function () {
    var ref = new Firebase("https://pyblish-web.firebaseio.com/events");

    var templates = {
        "small": Handlebars.compile($("#small-event-template").html()),
        "large": Handlebars.compile($("#large-event-template").html()),
    }

    ref.limitToLast(50).on("child_added", function(snapshot) {
        $(".loader").hide();  // Loader visible by default

        var item = snapshot.val();

        item.icon = iconFromEvent(item.event);
        item.authorName = basename(item.author);
        item.targetName = basename(item.target, -2);
        item.actionName = basename(item.action);
        item.time = relativeTime(Date.now(), Date.parse(item.time));

        console.log(item, "added");
        append(item);
    });

    function append(item) {
        var html = "body" in item ? templates.large(item) : templates.small(item);
        $("#events").append(html);
    };

})();

/**
 * Yield name of Awesome Fonts icon from event
 * @param {string} event - Name of Awesome Font icon
 */ 
function iconFromEvent(event) {
    return {
        "github-wiki": "book",
        "github-fork": "hand-scissors",
        "github-push": "code-fork",
        "github-pull-request": "exchange",
        "github-issue": "bug",
        "github-issue-comment": "comment",
        "github-commit-comment": "comment",
    }[event] || "globe" // Generic icon for unhandled events
}

/**
 * Return basename of path
 * @param {string} path - Absolute path
 * @param {string} slice - Optional levels at end to return; defaults to -1
 */
function basename (path, slice) {
    return (path ? path : "").split(/[\\/]/).slice(slice ? slice : -1).join("/");
}

/**
 * Return relative time between current previous
 */
function relativeTime(current, previous) {

    var msPerMinute = 60 * 1000;
    var msPerHour = msPerMinute * 60;
    var msPerDay = msPerHour * 24;
    var msPerMonth = msPerDay * 30;
    var msPerYear = msPerDay * 365;

    var elapsed = current - previous;
    
    if (elapsed < 1) {
        return "Just now";
    }

    else if (elapsed < msPerMinute) {
         return Math.round(elapsed/1000) + ' seconds ago';   
    }

    else if (elapsed < msPerHour) {
         return Math.round(elapsed/msPerMinute) + ' minutes ago';   
    }

    else if (elapsed < msPerDay ) {
         return Math.round(elapsed/msPerHour ) + ' hours ago';   
    }

    else if (elapsed < msPerMonth) {
        return Math.round(elapsed/msPerDay) + ' days ago';   
    }

    else if (elapsed < msPerYear) {
        return Math.round(elapsed/msPerMonth) + ' months ago';   
    }

    else {
        return Math.round(elapsed/msPerYear ) + ' years ago';   
    }
}
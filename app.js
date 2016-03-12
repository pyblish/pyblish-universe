/*global Firebase*/
/*global Handlebars*/
/*global sprintf*/


(function () {
    var ref = new Firebase("https://pyblish-web.firebaseio.com/events");
    
    var templates = {
        "small": Handlebars.compile($("#small-event-template").html()),
        "large": Handlebars.compile($("#large-event-template").html()),
    }

    ref.on("child_added", function(snapshot) {
        $(".loader").hide();  // Loader visible by default

        var item = snapshot.val();

        item.authorName = basename(item.author);
        item.targetName = basename(item.target, -2);
        item.actionName = basename(item.action);
        item.time = formatTime(item.time);

        console.log(item, "added");
        append(item);
    });
    
    function append(item) {
        var html = "body" in item ? templates.large(item) : templates.small(item);
        $("#events").append(html);
    };
    
})();

/**
 * Return basename of path
 * @param {string} path - Absolute path
 * @param {string} slice - Optional levels at end to return; defaults to -1
 */
function basename (path, slice) {
    return (path ? path : "").split(/[\\/]/).slice(slice ? slice : -1).join("/");
}

function formatTime(time) {
    var months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    var days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    
    var d = new Date(Date.parse(time));
    return sprintf(
        "%(day)s %(date)s %(month)s %(hour)s:%(minute)s",
        {
            "day": days[d.getDay()],
            "month": months[d.getMonth()],
            "date": d.getMonth(),
            "hour": d.getHours(),
            "minute": d.getMinutes()
        }
    )
}
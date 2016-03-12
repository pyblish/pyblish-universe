/*global Firebase*/
/*global Handlebars*/


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

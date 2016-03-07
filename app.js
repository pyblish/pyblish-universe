/*global Firebase*/

(function () {
    var ref = new Firebase("https://pyblish-web.firebaseio.com/events");

    ref.on("child_added", function(snapshot) {
        var item = snapshot.val();
        append(item.name);
    });
    
    function append(name) {
        $("#myEvents").append("<li><a href='url-here'>" + name + "</a></li>");
    };
})();
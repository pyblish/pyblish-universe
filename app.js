/*global Firebase*/
/*global Handlebars*/

function basename (path) {
    return path.split(/[\\/]/).pop();
}

(function () {
    var ref = new Firebase("https://pyblish-web.firebaseio.com/events");

    ref.on("child_added", function(snapshot) {
        var item = snapshot.val();
        
        item.authorUrl = item.author;
        item.author = basename(item.author);
    
        item.targetUrl = item.target;
        item.target = basename(item.target);

        console.log(item, "added");
        append(item);
    });
    
    function append(item) {
        // Template
        var source   = $("#entry-template").html();
        var template = Handlebars.compile(source);

        var context = item;
        var html = template(context);
    
        $("#events").append(html);
    };
    
})();
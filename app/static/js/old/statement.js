let loaded = false;
$("#included").on("shown.bs.collapse", function () {
    if (!loaded) {
        $("#included").load($("#included").attr("addr"));
        loaded = true;
    }
    $("#collapse").html("Свернуть условие <span class='fa fa-arrow-up'>");
})
$("#included").on("hidden.bs.collapse", function () {
    $("#collapse").html("Развернуть условие <span class='fa fa-arrow-down'>");
})

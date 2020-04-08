$("#included").on("shown.bs.collapse", function () {
    $("#collapse").html("Свернуть условие <span class='fa fa-arrow-up'>");
})
$("#included").on("hidden.bs.collapse", function () {
    $("#collapse").html("Развернуть условие <span class='fa fa-arrow-down'>");
})

$(function () {
    $("#included").load($("#included").attr("addr"));
})

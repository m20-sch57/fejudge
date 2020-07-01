'use strict'

function resize() {
    let height = $(window).height() - $("#statementsTitle").outerHeight();
    $("#statementsContentScrollable").css("height", `${height}px`);
}

function hideLoading() {
    $("#statementsLoading").css("display", "none");
}

function updateShadow() {
    if ($("#statementsContentScrollable").scrollTop() == 0) {
        $("#statementsTitle").removeClass("shadow");
    }
    else {
        $("#statementsTitle").addClass("shadow");
    }
}

window.onresize = resize;
window.onload = function() {
    resize();
    $("#statementsLoadedContent").load($("#statementsLoadedContent").attr("href"),
    () => setTimeout(hideLoading, 1500));
}

$("#statementsContentScrollable").scroll(updateShadow);

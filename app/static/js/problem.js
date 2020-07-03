'use strict'

function resize() {
    let height = $(window).height() - $("#statementsTitle").outerHeight();
    $("#statementsContentScrollable").css("height", `${height}px`);
    height = $(window).height() - $("#submitSection").outerHeight() - $("#infoSection").outerHeight();
    $("#problemNavigation").css("height", `${height}px`);
}

function hideLoading() {
    $("#statementsLoading").css("display", "none");
}

function updateStatementsShadow() {
    if ($("#statementsContentScrollable").scrollTop() == 0) {
        $("#statementsTitle").removeClass("shadow");
    }
    else {
        $("#statementsTitle").addClass("shadow");
    }
}

function expandSubmit() {
    $("#submitBox").removeClass("hidden");
    $("#statementsBox").addClass("collapsed")
}

function collapseSubmit() {
    $("#submitBox").addClass("hidden");
    $("#statementsBox").removeClass("collapsed")
}

window.onresize = resize;
window.onload = function() {
    resize();
    $("#statementsLoadedContent").load($("#statementsLoadedContent").attr("href"),
    () => setTimeout(hideLoading, 1500));
}

$("#statementsContentScrollable").scroll(updateStatementsShadow);
$("#submitExpand").click(expandSubmit);
$("#submitCollapse").click(collapseSubmit);

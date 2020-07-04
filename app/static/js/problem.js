'use strict'

function resize() {
    let height = $(window).height() - $("#statementsTitle").outerHeight();
    $("#statementsContentScrollable").css("height", `${height}px`);
    height = $(window).height() - $("#submitSection").outerHeight() - $("#infoSection").outerHeight();
    $("#problemNavigation").css("height", `${height}px`);
}

function updateStatementsShadow() {
    if ($("#statementsContentScrollable").scrollTop() == 0) {
        $("#statementsTitle").removeClass("shadow");
    }
    else {
        $("#statementsTitle").addClass("shadow");
    }
}

function extraBoxCollapse() {
    extraBoxExpanded = false;
    currentBox = "";
    $("#extraBox").addClass("collapsed");
    $("#statementsBox").removeClass("collapsed");
}

function hideBoxes() {
    boxes.forEach((it) => it.css("display", "none"));
}

function expandBox(box) {
    extraBoxExpanded = true;
    currentBox = box;
    hideBoxes();
    $("#extraBox").removeClass("collapsed");
    $("#statementsBox").addClass("collapsed");
    $(box).css("display", "");
}

function buttonPressed(box) {
    if (box == currentBox) {
        extraBoxCollapse();
    }
    else {
        expandBox(box);
    }
}

window.onresize = resize;
window.onload = function() {
    resize();
    $("#statementsLoadedContent").load($("#statementsLoadedContent").attr("href"));
}

let extraBoxExpanded = false;
let boxes = [$("#submitBox"), $("#contestInfoBox")];
let currentBox = "";

$("#statementsContentScrollable").scroll(updateStatementsShadow);
$("#extraBoxCollapse").click(extraBoxCollapse);
$("#submitExpand").click(() => buttonPressed("#submitBox"));
$("#viewContestInfo").click(() => buttonPressed("#contestInfoBox"));

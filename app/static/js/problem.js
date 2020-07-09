'use strict'

const contestId = location.href.toString().split("/").slice(-3, -1)[0];
const problemNumber = location.href.toString().split("/").slice(-3, -1)[1];
const boxes = [$("#submitBox"), $("#contestInfoBox"), $("#contestMessagesBox")];

function resize() {
    let statementsHeight = $(window).outerHeight() - $("#statementsTitle").outerHeight();
    let statementsWidth = $(window).outerWidth() - $("#rightBox").outerWidth();
    let navHeight = $(window).height() - $("#submitSection").outerHeight() - $("#infoSection").outerHeight();
    $("#statementsContentScrollable").css("max-height", `${statementsHeight}px`);
    $("#statementsContentScrollable").css("max-width", `${statementsWidth}px`);
    $("#problemNavigation").css("height", `${navHeight}px`);
}

function updateStatementsShadow() {
    if ($("#statementsContentScrollable").scrollTop() == 0) {
        $("#statementsTitle").removeClass("shadow");
    }
    else {
        $("#statementsTitle").addClass("shadow");
    }
}

function hideBoxes() {
    boxes.forEach((it) => it.css("display", "none"));
}

function expandBox(box, animate = true) {
    hideBoxes();
    localStorage.setItem("currentBox", box);
    if (animate) {
        $("#extraBox").css("transition", "all 60ms ease-out");
        $("#statementsBox").css("transition", "all 60ms ease-out");
    }
    else {
        $("#extraBox").css("transition", "none");
        $("#statementsBox").css("transition", "none");
    }
    if (box === "") {
        $("#extraBox").addClass("collapsed");
        $("#statementsBox").removeClass("collapsed");
    }
    else {
        $("#extraBox").removeClass("collapsed");
        $("#statementsBox").addClass("collapsed");
        $(box).css("display", "");
    }
}

function navButtonPressed(box) {
    if (box === localStorage.getItem("currentBox")) {
        expandBox("");
    }
    else {
        expandBox(box);
    }
}

function selectProblem(problemNumber) {
    $("#taskSelect").val(problemNumber);
}

function hideSubmitStatus() {
    $("#submitLoading").css("display", "none");
    $("#submitSuccess").css("display", "none");
    $("#submitFail").css("display", "none");
}

function hideSubmitStatusDelay(element) {
    setTimeout(() => $(element).css("opacity", 0), 5000);
}

function showSubmitSuccess() {
    hideSubmitStatus();
    $("#submitSuccess").css("display", "");
    $("#submitSuccess").css("opacity", 1);
}

function showSubmitFail(message) {
    hideSubmitStatus();
    $("#submitFail").css("display", "");
    $("#submitFail").css("opacity", 1);
    $("#submitFileButton").removeAttr("disabled");
    $("#submitFail").text(message);
}

function resetFileInput() {
    $("#chooseFileInput").val(null);
    $("#chooseFileName").text("No file chosen");
    $("#submitFileButton").attr("disabled", "");
}

function uploadFile(file) {
    if (file === undefined) {
        resetFileInput();
    }
    else {
        hideSubmitStatus();
        $("#chooseFileName").text(file.name);
        $("#submitFileButton").removeAttr("disabled");
    }
}

async function submitFile(file) {
    hideSubmitStatus();
    $("#submitFileButton").attr("disabled", "");
    $("#submitLoading").css("display", "");
    let formData = new FormData();
    formData.append("sourceFile", file);
    try {
        let response = await fetch(`/contests/${contestId}/${problemNumber}/submit`, {
            method: "POST",
            body: formData
        });
        if (response.ok) {
            showSubmitSuccess();
            hideSubmitStatusDelay("#submitSuccess");
        }
        else {
            let message = response.statusText;
            if (response.status === 413) message = "File size is > 1 MB";
            showSubmitFail(message);
            hideSubmitStatusDelay("#submitFail");
        }
        resetFileInput();
    }
    catch {
        showSubmitFail("Unable to submit");
    }
}

window.onresize = resize;
window.onload = resize;

$("#statementsContentScrollable").scroll(updateStatementsShadow);
$("#statementsLoadedContent").load($("#statementsLoadedContent").attr("href"));

if (localStorage.getItem("currentBox") !== "#submitBox") localStorage.setItem("currentBox", "");
expandBox(localStorage.getItem("currentBox"), false);

$("#extraBoxCollapse").click(() => expandBox(""));
$("#submitExpand").click(() => navButtonPressed("#submitBox"));
$("#viewContestInfo").click(() => navButtonPressed("#contestInfoBox"));
$("#viewContestMessages").click(() => navButtonPressed("#contestMessagesBox"));

selectProblem(problemNumber);

resetFileInput();
$("#chooseFileInput").change(function () {
    uploadFile(this.files[0])
});
$("#submitFileButton").click(() => submitFile($("#chooseFileInput").get(0).files[0]));

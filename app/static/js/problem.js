'use strict'

const contestId = location.href.toString().split("/").slice(-3, -1)[0];
const problemNumber = location.href.toString().split("/").slice(-3, -1)[1];

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
    hideBoxes();
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

function navButtonPressed(box) {
    if (box == currentBox) {
        extraBoxCollapse();
    }
    else {
        expandBox(box);
    }
}

function hideSubmitStatus() {
    $("#submitLoading").css("display", "none");
    $("#submitSuccess").css("display", "none");
    $("#submitFail").css("display", "none");
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

function handleSubmitErrors(response) {
    if (response.status === 413) {
        throw Error("file size > 1 MB");
    }
    else if (!response.ok) {
        throw Error(response.statusText);
    }
    return response;
}

function submitFile(file) {
    hideSubmitStatus();
    $("#submitFileButton").attr("disabled", "");
    $("#submitLoading").css("display", "");
    let formData = new FormData();
    formData.append("sourceFile", file);
    fetch(`/contests/${contestId}/${problemNumber}/submit`, {
        method: "POST",
        body: formData
    }).then(
        handleSubmitErrors
    ).then(() => {
        hideSubmitStatus();
        $("#submitSuccess").css("display", "");
        $("#submitSuccess").css("opacity", 1);
        setTimeout(() => $("#submitSuccess").css("opacity", 0), 5000);
    }).catch((error) => {
        hideSubmitStatus();
        $("#submitFail").css("display", "");
        $("#submitFail").css("opacity", 1);
        $("#submitFileButton").removeAttr("disabled");
        $("#submitFail").text(error);
        setTimeout(() => $("#submitFail").css("opacity", 0), 5000);
    }).finally(
        resetFileInput
    );
}

window.onresize = resize;
window.onload = resize;

let extraBoxExpanded = false;
let boxes = [$("#submitBox"), $("#contestInfoBox"), $("#contestMessagesBox")];
let currentBox = "";

$("#statementsContentScrollable").scroll(updateStatementsShadow);
$("#statementsLoadedContent").load($("#statementsLoadedContent").attr("href"));

hideBoxes();
$("#extraBoxCollapse").click(extraBoxCollapse);
$("#submitExpand").click(() => navButtonPressed("#submitBox"));
$("#viewContestInfo").click(() => navButtonPressed("#contestInfoBox"));
$("#viewContestMessages").click(() => navButtonPressed("#contestMessagesBox"));

resetFileInput();
$("#chooseFileInput").change(function () {
    uploadFile(this.files[0])
});
$("#submitFileButton").click(() => submitFile($("#chooseFileInput").get(0).files[0]));

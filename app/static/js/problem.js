'use strict'

const contestId = location.href.toString().split("/").slice(-3, -1)[0];
const problemNumber = location.href.toString().split("/").slice(-3, -1)[1];
const boxes = [$("#submitBox"), $("#contestInfoBox"), $("#contestMessagesBox")];
const socket = io.connect(window.location.origin);

function resize() {
    let height = $(window).height() - $("#statementsTitle").outerHeight();
    let width = $(window).width() - $("#rightBox").outerWidth();
    let navHeight = $(window).height() - $("#submitSection").outerHeight() - $("#infoSection").outerHeight();
    $("#statementsContentScrollable").css("max-height", `${height}px`);
    $("#statementsContentScrollable").css("max-width", `${width}px`);
    $("#submitContent").css("max-height", `${height}px`);
    $("#submitContent").css("max-width", `${width}px`);
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
    boxes.forEach((it) => it.hide());
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
        $(box).show();
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

function goToProblem(problemNumber) {
    window.location.replace(`/contests/${contestId}/${problemNumber}/problem`);
}

function hideSubmitStatus() {
    $("#submitLoading").hide();
    $("#submitSuccess").hide();
    $("#submitFail").hide();
}

function hideSubmitStatusDelay(element) {
    setTimeout(() => $(element).css("opacity", 0), 5000);
}

function showSubmitSuccess() {
    hideSubmitStatus();
    $("#submitSuccess").css("opacity", 1);
    $("#submitSuccess").show();
}

function showSubmitFail(message) {
    hideSubmitStatus();
    $("#submitFail").css("opacity", 1);
    $("#submitFail").show();
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
    $("#submitLoading").show();
    let formData = new FormData();
    formData.append("language", $("#languageSelect").val());
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
            if (response.status === 413) message = "File size > 1 MB";
            if (response.status === 400) message = "Incorrect data";
            showSubmitFail(message);
            hideSubmitStatusDelay("#submitFail");
        }
        resetFileInput();
    }
    catch {
        showSubmitFail("Unable to submit");
    }
}

function showSubmissionsTable() {
    $("#submissionsLoading").hide();
    if ($("#submissionsTable tbody").children().length == 0) {
        $("#submissionsNone").show();
    }
    else {
        $("#submissionsTable").show();
    }
}

window.onresize = resize;
window.onload = resize;

socket.on("connect", () => socket.emit("join"));
socket.on("new_submission", (submissionId) => console.log(`New submission ${submissionId}`));
socket.on("compiling", (submissionId) => console.log(`Compiling ${submissionId}`));
socket.on("evaluating", (submissionId) => console.log(`Evaluating ${submissionId}`));
socket.on("completed", (submissionId) => console.log(`Completed ${submissionId}`));

$("#statementsContentScrollable").scroll(updateStatementsShadow);
$("#statementsLoadedContent").load($("#statementsLoadedContent").attr("href"));

if (localStorage.getItem("currentBox") !== "#submitBox") localStorage.setItem("currentBox", "");
expandBox(localStorage.getItem("currentBox"), false);

$("#extraBoxCollapse").click(() => expandBox(""));
$("#submitExpand").click(() => navButtonPressed("#submitBox"));
$("#viewContestInfo").click(() => navButtonPressed("#contestInfoBox"));
$("#viewContestMessages").click(() => navButtonPressed("#contestMessagesBox"));

$("#taskSelect").val(problemNumber);
$("#taskSelect").change(function () {
    goToProblem(this.value);
});

resetFileInput();
$("#chooseFileInput").change(function () {
    uploadFile(this.files[0])
});
$("#submitFileButton").click(() => submitFile($("#chooseFileInput").get(0).files[0]));

showSubmissionsTable();

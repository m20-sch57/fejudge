'use strict'

const contestId = location.href.toString().split("/").slice(-3, -1)[0];
const problemNumber = location.href.toString().split("/").slice(-3, -1)[1];
const problemId = $("#problemId").text().trim();
const socket = io.connect(window.location.origin);
const languageOptions = ["cpp", "py"];
const languageMatching = {
    "cpp": "GNU C++ 9.2.0",
    "py": "Python 3.8"
};

function resize() {
    let height = $(window).height() - $("#statementsTitle").outerHeight();
    let width = $(window).width() - $("#rightBox").outerWidth();
    let navHeight = $(window).height() - $("#submitSection").outerHeight() - $("#infoSection").outerHeight();
    $("#statementsContentScrollable").css("max-height", `${height}px`);
    $("#statementsContentScrollable").css("max-width", `${width}px`);
    $(".extra-content").css("max-height", `${height}px`);
    $(".extra-content").css("max-width", `${width}px`);
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

function expandBox(box, animate = true) {
    $(localStorage.getItem("currentBox")).hide();
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
    if (box === "" || box === "#submissionDetailsBox") {
        $("#extraBoxCollapse").hide();
    }
    else {
        $("#extraBoxCollapse").show();
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
    setTimeout(() => $(element).fadeOut(300), 5000);
}

function showSubmitSuccess() {
    hideSubmitStatus();
    $("#submitSuccess").show();
}

function showSubmitFail(message) {
    hideSubmitStatus();
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
    $("#submissionsNone").hide();
    $("#submissionsTable").hide();
    if ($("#submissionsTable tbody").children().length == 0) {
        $("#submissionsNone").show();
    }
    else {
        $("#submissionsTable").show();
    }
}

function newSubmissionRow(submissionId) {
    let row = document.createElement("tr");
    let cellNames = ["id", "language", "status", "score", "details"];
    for (let name of cellNames) {
        let elem = document.createElement("td");
        $(elem).addClass(name);
        $(elem).attr("id", `submission_${submissionId}_${name}`);
        if (name === "id") $(elem).text(submissionId);
        $(row).append(elem);
    }
    return row;
}

function appendNewSubmission(submissionId) {
    let submissionRow = newSubmissionRow(submissionId);
    $("#submissionsTable tbody").append(submissionRow);
}

function prependNewSubmission(submissionId) {
    let submissionRow = newSubmissionRow(submissionId);
    $("#submissionsTable tbody").prepend(submissionRow);
}

function inQueue(submissionId, submissionLanguage) {
    $(`#submission_${submissionId}_language`).text(languageMatching[submissionLanguage]);
    $(`#submission_${submissionId}_status`).text("In queue");
    $(`#submission_${submissionId}_score`).html("&mdash;");
    $(`#submission_${submissionId}_details`).html("&mdash;");
}

function compiling(submissionId) {
    let status = $(`#submission_${submissionId}_status`);
    status.empty();
    status.addClass("col-grey");
    let spinner = document.createElement("span");
    $(spinner).addClass("lds-spinner");
    for (let it = 0; it < 12; it++) {
        spinner.append(document.createElement("div"));
    }
    status.append(spinner);
    let statusLabel = document.createElement("span");
    $(statusLabel).attr("id", `submission_${submissionId}_statusLabel`);
    $(statusLabel).text(" Compiling");
    status.append(statusLabel);
}

function evaluating(submissionId) {
    $(`#submission_${submissionId}_statusLabel`).text(" Running");
}

function completed(submissionId, submissionStatus, submissionScore) {
    let status = $(`#submission_${submissionId}_status`);
    let score = $(`#submission_${submissionId}_score`);
    let details = $(`#submission_${submissionId}_details`);
    status.empty();
    status.removeClass("col-grey");
    if (submissionStatus === "accepted") {
        status.addClass("col-green");
        status.text("OK");
    }
    else if (submissionStatus === "partial") {
        status.addClass("col-red");
        status.text("Partial");
    }
    else if (submissionStatus === "compilation_error") {
        status.addClass("col-red");
        status.text("Not compiled");
    }
    score.text(submissionScore);
    details.empty();
    let detailsButton = document.createElement("button");
    $(detailsButton).addClass("flat-link");
    $(detailsButton).addClass("link-blue");
    $(detailsButton).text("Details");
    $(detailsButton).click(() => {
        expandBox("#submissionDetailsBox");
        loadSubmissionDetails(submissionId);
    });
    details.append(detailsButton);
}

async function loadSubmissions() {
    let response = await fetch(`/contests/${contestId}/${problemNumber}/submissions`);
    let submissions = await response.json();
    for (let submission of submissions) {
        let submissionId = submission.submission_id;
        let submissionLanguage = submission.submission_language;
        let submissionStatus = submission.submission_status;
        let submissionScore = submission.submission_score;
        appendNewSubmission(submissionId);
        if (submissionStatus === "in_queue") {
            inQueue(submissionId, submissionLanguage);
        }
        else if (submissionStatus === "compiling") {
            inQueue(submissionId, submissionLanguage);
            compiling(submissionId);
        }
        else if (submissionStatus === "evaluating") {
            inQueue(submissionId, submissionLanguage);
            compiling(submissionId);
            evaluating(submissionId);
        }
        else {
            inQueue(submissionId, submissionLanguage);
            compiling(submissionId);
            evaluating(submissionId);
            completed(submissionId, submissionStatus, submissionScore);
        }
    }
    showSubmissionsTable();
}

function appendNewTestDetails(testNumber) {
    let protocolRow = document.createElement("tr");
    let cellNames = ["number", "status", "time", "memory"];
    for (let name of cellNames) {
        let elem = document.createElement("td");
        $(elem).addClass(name);
        $(elem).attr("id", `protocol_${testNumber}_${name}`);
        if (name === "number") $(elem).text(testNumber);
        $(protocolRow).append(elem);
    }
    $("#submissionProtocolTable tbody").append(protocolRow);
}

function hideAllDetails() {
    let detailsSections = ["submissionProtocol", "submissionCode", "submissionInfo"];
    detailsSections.forEach((it) => {
        $(`#${it}`).hide();
        $(`#${it}NavButton`).removeClass("active");
    });
}

function showSubmissionProtocol() {
    hideAllDetails();
    $("#submissionProtocol").show();
    $("#submissionDetailsBox .extra-content").scrollTop(0);
    $("#submissionProtocolNavButton").addClass("active");
    $("#submissionCompiler").hide();
    $("#submissionTests").hide();
    if ($("#submissionProtocolTable tbody").children().length == 0) {
        $("#submissionCompiler").show();
    }
    else {
        $("#submissionTests").show();
    }
}

function showSubmissionCode() {
    hideAllDetails();
    $("#submissionCode").show();
    $("#submissionDetailsBox .extra-content").scrollTop(0);
    $("#submissionCodeNavButton").addClass("active");
}

function showSubmissionInfo() {
    hideAllDetails();
    $("#submissionInfo").show();
    $("#submissionDetailsBox .extra-content").scrollTop(0);
    $("#submissionInfoNavButton").addClass("active");
}

async function loadSubmissionDetails(submissionId) {
    $("#submissionDetailsId").text(submissionId);
    $("#submissionProtocolTable tbody").empty();
    hideAllDetails();
    $("#submissionProtocolNavButton").addClass("active");
    let response = await fetch(`/submissions/${submissionId}/details`);
    let details = await response.json();
    $("#submissionCompilerLog").text(details.protocol.compiler);
    for (let testNumber = 1; testNumber <= details.protocol.tests.length; ++testNumber) {
        let testDetails = details.protocol.tests[testNumber - 1];
        let testStatus = testDetails.status;
        let testTime = testDetails.time_usage_s;
        let testMemory = testDetails.memory_usage_kb;
        appendNewTestDetails(testNumber);
        $(`#protocol_${testNumber}_status`).text(testStatus);
        $(`#protocol_${testNumber}_time`).text(testTime);
        $(`#protocol_${testNumber}_memory`).text(testMemory);
        if (testStatus === "OK")
            $(`#protocol_${testNumber}_status`).addClass("col-green");
        else if (testStatus === "NO")
            $(`#protocol_${testNumber}_status`).addClass("col-grey");
        else
            $(`#protocol_${testNumber}_status`).addClass("col-red");
    }
    $("#submissionSource").html(hljs.highlightAuto(details.source).value);
    $("#submissionCodeCopy").click(() => {
        navigator.clipboard.writeText(details.source).then(() => {
            $("#submissionCodeCopyHint").fadeIn(300);
            setTimeout(() => {
                $("#submissionCodeCopyHint").fadeOut(300);
            }, 5000);
        });
    });
    showSubmissionProtocol();
}

window.onresize = resize;
window.onload = resize;

socket.on("connect", () => socket.emit("join", problemId));
socket.on("new_submission", (message) => {
    prependNewSubmission(message.submission_id);
    showSubmissionsTable();
    inQueue(message.submission_id, message.submission_language);
});
socket.on("compiling", (message) => {
    compiling(message.submission_id);
});
socket.on("evaluating", (message) => {
    evaluating(message.submission_id);
});
socket.on("completed", (message) => {
    completed(message.submission_id, message.submission_status, message.submission_score);
});

$("#statementsContentScrollable").scroll(updateStatementsShadow);
$("#statementsLoadedContent").load($("#statementsLoadedContent").attr("href"));

if (localStorage.getItem("currentBox") === "#submissionDetailsBox")
    localStorage.setItem("currentBox", "#submitBox");
if (localStorage.getItem("currentBox") !== "#submitBox")
    localStorage.setItem("currentBox", "");
expandBox(localStorage.getItem("currentBox"), false);

$("#extraBoxCollapse").click(() => expandBox(""));
$("#submitExpand").click(() => navButtonPressed("#submitBox"));
$("#viewContestInfo").click(() => navButtonPressed("#contestInfoBox"));
$("#viewContestMessages").click(() => navButtonPressed("#contestMessagesBox"));

$("#taskSelect").val(problemNumber);
$("#taskSelect").change(function () {
    goToProblem(this.value);
});

languageOptions.forEach((it) => {
    $("#languageSelect").append(new Option(languageMatching[it], it));
});
$("#languageSelect").val(localStorage.getItem("currentLanguage"));
$("#languageSelect").change(function () {
    localStorage.setItem("currentLanguage", this.value);
});

resetFileInput();
$("#chooseFileInput").change(function () {
    uploadFile(this.files[0])
});
$("#submitFileButton").click(() => submitFile($("#chooseFileInput").get(0).files[0]));

loadSubmissions();

$("#submissionProtocolNavButton").click(showSubmissionProtocol);
$("#submissionCodeNavButton").click(showSubmissionCode);
$("#submissionInfoNavButton").click(showSubmissionInfo);
$("#submissionDetailsClose").click(() => expandBox("#submitBox"));

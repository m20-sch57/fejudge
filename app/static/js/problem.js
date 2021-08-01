'use strict'

const contestId = location.href.toString().split("/").slice(-4, -1)[0];
const problemNumber = location.href.toString().split("/").slice(-4, -1)[1];
const problemLanguage = location.href.toString().split("/").slice(-4, -1)[2];
const problemId = $("#problemId").text().trim();
const socket = io.connect(window.location.origin);
const languageMatching = {
    "english": "English",
    "russian": "Russian",
    "cpp": "GNU G++17",
    "java": "Java 8",
    "py": "Python 3"
};
const statusMatching = {
    "AC": "Accepted",
    "PT": "Partial solution",
    "CE": "Not compiled",
    "WA": "Wrong answer",
    "PE": "Presentation error",
    "RE": "Runtime error",
    "ML": "Memory limit hit",
    "TL": "Time limit hit",
    "IL": "Idleness limit hit",
    "FAIL": "Check failed"
};

function getLanguageName(status) {
    return languageMatching[status];
}

function getStatusName(status) {
    return statusMatching[status];
}

function getStatusColor(status) {
    return status === "AC" ? "col-green" : "col-red";
}

function goToProblem(problemNumber, problemLanguage) {
    location.replace(`/contests/${contestId}/${problemNumber}/${problemLanguage}/problem`);
}

function resize() {
    let height = $(window).height() - $("#statementsBox header").outerHeight();
    let width = $(window).width() - $("#rightBox").outerWidth();
    let navHeight = $(window).height() - $("#rightBox .submit").outerHeight() - $("#infoSection").outerHeight();
    $("#statementsScrollable").css("max-height", `${height}px`);
    $("#statementsScrollable").css("max-width", `${width}px`);
    $(".extra-box main").css("max-height", `${height}px`);
    $(".extra-box main").css("max-width", `${width}px`);
    $("#problemNavigation").css("height", `${navHeight}px`);
}

function updateStatementsShadow() {
    if ($("#statementsScrollable").scrollTop() == 0) {
        $("#statementsBox header").removeClass("shadow");
    }
    else {
        $("#statementsBox header").addClass("shadow");
    }
}

function initStatements() {
    $("#reloadStatements").click(() => goToProblem(problemNumber, problemLanguage))
    $("#problemLanguageSelect option").each(function () {
        this.innerText = getLanguageName(this.value);
    });
    $("#problemLanguageSelect").val(problemLanguage);
    $("#statementsScrollable").scroll(updateStatementsShadow);
    $("#statementsLoadedContent").load(
        `/contests/${contestId}/${problemNumber}/${problemLanguage}/problem.html`
    );
    $("#problemLanguageSelect").change(function () {
        goToProblem(problemNumber, this.value);
    });
}

function hideAllBoxes() {
    $("#extraBox .extra-box").each(function () {
        $(this).hide();
    });
}

function expandBox(box, animate = true) {
    hideAllBoxes();
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
        $(box).fadeIn(100);
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

function initProgramLanguageSelect() {
    $("#languageSelect option").each(function () {
        this.innerText = getLanguageName(this.value);
    });
    let defaultLanguage = localStorage.getItem("programLanguage");
    if ($(`#languageSelect option[value="${defaultLanguage}"]`).length == 0) {
        defaultLanguage = $("#languageSelect option:first").val();
    }
    $("#languageSelect").val(defaultLanguage);
    $("#languageSelect").change(function () {
        localStorage.setItem("programLanguage", this.value);
    });
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
        hideSubmitStatus();
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

function hideSubmissions() {
    $("#submissionsNone").hide();
    $("#submissionsTable").hide();
}

function showSubmissions() {
    hideSubmissions();
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
    $("#submissionsNone").hide();
    $("#submissionsTable tbody").append(newSubmissionRow(submissionId));
}

function prependNewSubmission(submissionId) {
    $("#submissionsNone").hide();
    $("#submissionsTable tbody").prepend(newSubmissionRow(submissionId));
}

function ringElement(fontSize) {
    let ring = document.createElement("span");
    $(ring).addClass("lds-ring");
    $(ring).css("font-size", `${fontSize}px`);
    $(ring).html("<div></div><div></div><div></div>");
    return ring;
}

function inQueue(submissionId, submissionLanguage) {
    $(`#submission_${submissionId}_language`).text(getLanguageName(submissionLanguage));
    $(`#submission_${submissionId}_status`).append(ringElement(30));
    $(`#submission_${submissionId}_score`).html("&mdash;");
    $(`#submission_${submissionId}_details`).html("&mdash;");
}

function compiling(submissionId) {
    let status = $(`#submission_${submissionId}_status`);
    status.empty();
    status.addClass("col-grey");
    status.append(ringElement(20));
    let statusLabel = document.createElement("span");
    $(statusLabel).attr("id", `submission_${submissionId}_statusLabel`);
    $(statusLabel).css("display", "inline-block");
    $(statusLabel).css("margin-left", "5px");
    $(statusLabel).css("text-align", "left");
    $(statusLabel).css("width", "80px");
    $(statusLabel).text("Compiling");
    status.append(statusLabel);
}

function evaluating(submissionId) {
    $(`#submission_${submissionId}_statusLabel`).text("Running");
}

function completed(submissionId, submissionStatus, submissionScore) {
    let status = $(`#submission_${submissionId}_status`);
    let score = $(`#submission_${submissionId}_score`);
    let details = $(`#submission_${submissionId}_details`);
    status.empty();
    status.removeClass("col-grey");
    status.addClass(getStatusColor(submissionStatus));
    status.text(getStatusName(submissionStatus));
    score.text(submissionScore);
    details.empty();
    let detailsButton = document.createElement("button");
    $(detailsButton).addClass("link");
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
        let statuses = ["evaluating", "compiling", "in_queue"];
        let submissionStatusIndex = statuses.indexOf(submissionStatus);
        if (submissionStatusIndex <= 2) {
            inQueue(submissionId, submissionLanguage);
        }
        if (submissionStatusIndex <= 1) {
            compiling(submissionId);
        }
        if (submissionStatusIndex <= 0) {
            evaluating(submissionId);
        }
        if (submissionStatusIndex == -1) {
            completed(submissionId, submissionStatus, submissionScore);
        }
    }
    $("#submissionsLoading").fadeOut(100);
    showSubmissions();
}

function appendNewTestDetails(testNumber) {
    let protocolRow = document.createElement("tr");
    let cellNames = ["number", "status", "time", "memory", "group", "score"];
    for (let name of cellNames) {
        let elem = document.createElement("td");
        $(elem).addClass(name);
        $(elem).attr("id", `protocol_${testNumber}_${name}`);
        if (name === "number") $(elem).text(testNumber);
        $(protocolRow).append(elem);
    }
    $("#submissionEvaluationTable tbody").append(protocolRow);
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
    $("#submissionDetailsBox main").scrollTop(0);
    $("#submissionProtocolNavButton").addClass("active");
    $("#submissionCompilation").hide();
    $("#submissionEvaluation").hide();
    if ($("#submissionEvaluationTable tbody").children().length == 0) {
        $("#submissionCompilation").show();
    }
    else {
        $("#submissionEvaluation").show();
    }
}

function showSubmissionCode() {
    hideAllDetails();
    $("#submissionCode").show();
    $("#submissionDetailsBox main").scrollTop(0);
    $("#submissionCodeNavButton").addClass("active");
}

function showSubmissionInfo() {
    hideAllDetails();
    $("#submissionInfo").show();
    $("#submissionDetailsBox main").scrollTop(0);
    $("#submissionInfoNavButton").addClass("active");
}

function initSubmissionProtocol(details) {
    $("#submissionResultStatus").removeClass();
    $("#submissionResultStatus").addClass(getStatusColor(details.status));
    if (details.status === "AC") {
        $("#submissionResultStatus").html(
            `<span class="fa fa-check"></span> ${getStatusName(details.status)}`
        );
    }
    else {
        $("#submissionResultStatus").html(
            `<span class="fa fa-times"></span> ${getStatusName(details.status)}`
        );
    }
    $("#submissionResultScore").text(`Score: ${details.score}`);
    $("#submissionCompilationLog").text(details.protocol.compilation);
    for (let testNumber = 1; testNumber <= details.protocol.evaluation.length; ++testNumber) {
        let testDetails = details.protocol.evaluation[testNumber - 1];
        let testStatus = testDetails.status;
        let testTime = testDetails.time_usage_s;
        let testMemory = testDetails.memory_usage_kb;
        let testGroup = testDetails.group;
        let testScore = testDetails.score;
        let testMaxscore = testDetails.maxscore;
        let testScoreStr = testMaxscore === undefined ? "" : `${testScore} (${testMaxscore})`;
        appendNewTestDetails(testNumber);
        $(`#protocol_${testNumber}_status`).text(testStatus);
        $(`#protocol_${testNumber}_time`).text(testTime);
        $(`#protocol_${testNumber}_memory`).text(testMemory);
        $(`#protocol_${testNumber}_group`).text(testGroup);
        $(`#protocol_${testNumber}_score`).text(testScoreStr);
        if (testStatus === "OK")
            $(`#protocol_${testNumber}_status`).addClass("col-green");
        else if (testStatus === "NO")
            $(`#protocol_${testNumber}_status`).addClass("col-grey");
        else
            $(`#protocol_${testNumber}_status`).addClass("col-red");
    }
}

function initSubmissionCode(details) {
    $("#submissionCodeCopyHint").hide();
    $("#submissionSource").html(hljs.highlight(details.language, details.source).value);
    $("#submissionCodeCopy").click(() => {
        navigator.clipboard.writeText(details.source).then(() => {
            $("#submissionCodeCopyHint").fadeIn(300);
            setTimeout(() => {
                $("#submissionCodeCopyHint").fadeOut(300);
            }, 2500);
        });
    });
}

function initSubmissionInfo(details) {
    $("#submissionInfoUser").text(details.user);
    $("#submissionInfoContest").text(details.contest);
    $("#submissionInfoProblem").text(details.problem);
    $("#submissionInfoLanguage").text(getLanguageName(details.language));
    $("#submissionInfoTime").text(details.time);
    $("#submissionInfoStatus").text(getStatusName(details.status));
    $("#submissionInfoScore").text(details.score);
}

async function loadSubmissionDetails(submissionId) {
    hideAllDetails();
    $("#submissionDetailsId").text(submissionId);
    $("#submissionProtocolNavButton").addClass("active");
    $("#submissionCompilationLog").text("");
    $("#submissionEvaluationTable tbody").empty();
    $("#submissionSource").empty();
    let response = await fetch(`/submissions/${submissionId}/details`);
    let details = await response.json();
    initSubmissionProtocol(details);
    initSubmissionCode(details);
    initSubmissionInfo(details);
    showSubmissionProtocol();
}

window.onresize = resize;
window.onload = resize;

socket.on("connect", () => socket.emit("join", problemId));
socket.on("new_submission", (message) => {
    prependNewSubmission(message.submission_id);
    showSubmissions();
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

initStatements();

if (localStorage.getItem("currentBox") === "#submissionDetailsBox")
    localStorage.setItem("currentBox", "#submitBox");
if (localStorage.getItem("currentBox") !== "#submitBox")
    localStorage.setItem("currentBox", "");
expandBox(localStorage.getItem("currentBox"), false);

$("#extraBoxCollapse").click(() => expandBox(""));
$("#submitExpand").click(() => navButtonPressed("#submitBox"));
$("#viewContestInfo").click(() => navButtonPressed("#contestInfoBox"));
$("#viewContestMessages").click(() => navButtonPressed("#contestMessagesBox"));

$("#problemNavigation button").each(function () {
    this.onclick = () => goToProblem(this.getAttribute("number"), problemLanguage);
});

$("#taskSelect").val(problemNumber);
$("#taskSelect").change(function () {
    goToProblem(this.value, problemLanguage);
});

initProgramLanguageSelect();

resetFileInput();
hideSubmitStatus();
$("#chooseFileInput").change(function () {
    uploadFile(this.files[0])
});
$("#submitFileButton").click(() => submitFile($("#chooseFileInput").get(0).files[0]));

loadSubmissions();

$("#submissionProtocolNavButton").click(showSubmissionProtocol);
$("#submissionCodeNavButton").click(showSubmissionCode);
$("#submissionInfoNavButton").click(showSubmissionInfo);
$("#submissionDetailsClose").click(() => expandBox("#submitBox"));

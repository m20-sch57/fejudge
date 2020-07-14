function reset() {
    fileUploadLabel.innerHTML = 'Файл не выбран';
    submit.setAttribute('disabled', '');
}

function uploadFile(file) {
    fileUploadLabel.innerHTML = file.name;
    submit.removeAttribute('disabled');
}

function uploadFiles(files) {
    if (files[0] === undefined) {
        reset();
    }
    else {
        uploadFile(files[0]);
    }
}

let fileUpload = document.getElementById('fileUpload');
let fileUploadLabel = document.getElementById('fileUploadLabel');
let submit = document.getElementById('submitForm');

fileUpload.onchange = function() {
    uploadFiles(this.files);
}
submit.onclick = function() {
    reset();
    submit.form.submit();
}

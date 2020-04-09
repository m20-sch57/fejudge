function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function highlight(e) {
    dropArea.classList.add('highlight');
}

function unhighlight(e) {
    dropArea.classList.remove('highlight');
}

function reset() {
    fileUploadLabel.innerHTML = 'Файл не выбран';
    submitAvatar.setAttribute('disabled', '');
    dropArea.innerHTML = '<span>Перетащите изображение сюда или выберите файл на вашем устройстве.</span>';
}

function error() {
    dropArea.innerHTML = '<span class="text-danger">Произошла ошибка при загрузке файла. Попробуйте ещё раз.</span>';
}

function uploadFile(file) {
    if (!file.type.match('image.*')) {
        reset();
        error();
        return;
    }
    fileUploadLabel.innerHTML = file.name;
    submitAvatar.removeAttribute('disabled');

    let reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onloadend = function() {
        let img = document.createElement('img');
        img.src = reader.result;
        img.className = 'rounded-circle image-lg';
        dropArea.innerHTML = '';
        dropArea.appendChild(img);
    }
}

function uploadFiles(files) {
    if (files[0] === undefined) {
        reset();
    }
    else {
        fileUpload.files = files;
        uploadFile(files[0]);
    }
}

function showProfileForm() {
    document.getElementById('firstName').removeAttribute('hidden');
    document.getElementById('firstNameLabel').setAttribute('hidden', '');
    document.getElementById('lastName').removeAttribute('hidden');
    document.getElementById('lastNameLabel').setAttribute('hidden', '');
    document.getElementById('email').removeAttribute('hidden');
    document.getElementById('emailLabel').setAttribute('hidden', '');
    changeProfile.setAttribute('hidden', '');
    submitProfile.removeAttribute('hidden');
    cancelProfile.removeAttribute('hidden');
}

function hideProfileForm() {
    document.getElementById('firstName').setAttribute('hidden', '');
    document.getElementById('firstNameLabel').removeAttribute('hidden');
    document.getElementById('lastName').setAttribute('hidden', '');
    document.getElementById('lastNameLabel').removeAttribute('hidden');
    document.getElementById('email').setAttribute('hidden', '');
    document.getElementById('emailLabel').removeAttribute('hidden');
    changeProfile.removeAttribute('hidden');
    submitProfile.setAttribute('hidden', '');
    cancelProfile.setAttribute('hidden', '');
}

let dropArea = document.getElementById('dropArea');
let fileUpload = document.getElementById('fileUpload');
let fileUploadLabel = document.getElementById('fileUploadLabel');
let submitAvatar = document.getElementById('submitAvatar');
let changeProfile = document.getElementById('changeProfile');
let submitProfile = document.getElementById('submitProfile');
let cancelProfile = document.getElementById('cancelProfile');

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, preventDefaults, false);
});
['dragenter', 'dragover'].forEach(eventName => {
    dropArea.addEventListener(eventName, highlight, false)
});
['dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, unhighlight, false)
});
dropArea.addEventListener('drop', eventName => uploadFiles(eventName.dataTransfer.files), false);

fileUpload.onchange = function() {
    uploadFiles(this.files);
}
submitAvatar.onclick = function() {
    reset();
    submitAvatar.form.submit();
}

changeProfile.onclick = showProfileForm;
cancelProfile.onclick = hideProfileForm;

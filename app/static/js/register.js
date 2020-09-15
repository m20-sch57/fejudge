'use strict'

let submit = document.getElementById("register");
submit.onclick = () => {
    let usernameInput = document.getElementById("usernameInput");
    let usernameHint = document.getElementById("usernameHint");
    let emailInput = document.getElementById("emailInput");
    let emailHint = document.getElementById("emailHint");
    let passwordInput = document.getElementById("passwordInput");
    let passwordHint = document.getElementById("passwordHint");
    let confirmPasswordInput = document.getElementById("confirmPasswordInput");
    let confirmPasswordHint = document.getElementById("confirmPasswordHint");
    let isValid = true;
    if (usernameInput.value == "") {
        isValid = false;
        usernameInput.classList.add("input-error");
        usernameHint.innerText = "Username should not be empty";
    }
    else {
        usernameInput.classList.remove("input-error");
        usernameHint.innerText = "";
    }
    if (emailInput.value.indexOf("@") == -1) {
        isValid = false;
        emailInput.classList.add("input-error");
        emailHint.innerText = "Please type in valid email address";
    }
    else {
        emailInput.classList.remove("input-error");
        emailHint.innerText = "";
    }
    if (passwordInput.value != confirmPasswordInput.value) {
        isValid = false;
        confirmPasswordInput.classList.add("input-error");
        confirmPasswordHint.innerText = "Confirm your password";
    }
    else {
        confirmPasswordInput.classList.remove("input-error");
        confirmPasswordHint.innerText = "";
    }
    if (isValid) {
        submit.form.submit();
    }
}

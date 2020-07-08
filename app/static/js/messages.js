'use strict'

function hideMessage(message) {
    message.style.opacity = 0;
    setTimeout(() => message.classList.add("hidden"), 300);
}

document.querySelectorAll("#messages .message .close").forEach(
    (it) => it.onclick = () => hideMessage(it.parentElement)
);

document.querySelectorAll("#messages .message.auto-dismiss").forEach(
    (it) => setTimeout(() => hideMessage(it), 5000)
);

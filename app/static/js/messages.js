'use strict'

document.querySelectorAll("#messages .message .close").forEach(
    (it) => it.onclick = () => it.parentElement.style.display = "none"
);

document.querySelectorAll("#messages .message.auto-dismiss").forEach(
    (it) => setTimeout(() => it.style.display = "none", 4000)
);

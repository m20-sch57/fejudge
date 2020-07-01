'use strict'

function repr(time) {
    let seconds = time % 60;
    time -= seconds, time /= 60;
    let minutes = time % 60;
    time -= minutes, time /= 60;
    let hours = time;
    if (seconds < 10) seconds = '0' + seconds;
    if (minutes < 10) minutes = '0' + minutes;
    if (hours < 10) hours = '0' + hours;
    return `${hours}:${minutes}:${seconds}`;
}

function start_timer(time_delta, onfinish = () => {}) {
    let timer = this;
    let time = Number(timer.innerText);
    timer.innerText = repr(time);
    setInterval(function() {
        if (time <= 0 && time_delta < 0) {
            onfinish();
            return;
        }
        else {
            time += time_delta;
            timer.innerText = repr(time);
        }
    }, 1000);
}

document.getElementsByName("timer").forEach((it) => start_timer.call(it, -1));

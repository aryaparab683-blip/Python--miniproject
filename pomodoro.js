const timerDisplay = document.getElementById('timerDisplay');
const startBtn = document.getElementById('startBtn');
const pauseBtn = document.getElementById('pauseBtn');
const resetBtn = document.getElementById('resetBtn');

let timerSeconds = 1500; // 25 min focus
let timerInterval = null;
let breakMode = false;

function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60).toString().padStart(2, '0');
    const secs = (seconds % 60).toString().padStart(2, '0');
    return `${minutes}:${secs}`;
}

function updateTimer() {
    if (!timerDisplay) return;
    timerDisplay.textContent = formatTime(timerSeconds);
}

function startTimer() {
    if (timerInterval) return;
    timerInterval = setInterval(() => {
        timerSeconds -= 1;
        if (timerSeconds <= 0) {
            clearInterval(timerInterval);
            timerInterval = null;
            breakMode = !breakMode;
            timerSeconds = breakMode ? 300 : 1500;
            const label = breakMode ? 'Break' : 'Focus';
            alert(`${label} time started!`);
        }
        updateTimer();
    }, 1000);
}

function pauseTimer() {
    clearInterval(timerInterval);
    timerInterval = null;
}

function resetTimer() {
    pauseTimer();
    breakMode = false;
    timerSeconds = 1500;
    updateTimer();
}

if (startBtn) startBtn.addEventListener('click', startTimer);
if (pauseBtn) pauseBtn.addEventListener('click', pauseTimer);
if (resetBtn) resetBtn.addEventListener('click', resetTimer);
updateTimer();

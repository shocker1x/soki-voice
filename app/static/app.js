const userInput = document.getElementById('userInput');
const sendButton = document.getElementById('sendButton');
const micButton = document.getElementById('micButton');
const traceList = document.getElementById('traceList');

async function fetchRecentTraces() {
  const resp = await fetch('/api/traces');
  const traces = await resp.json();
  traceList.innerHTML = traces
    .slice(0, 5)
    .map(
      (trace) => `
        <div class="log-item">
          <div><strong>#{trace.id}</strong> · ${trace.source}</div>
          <div>User: ${trace.transcript}</div>
          <div>Reply: ${trace.reply}</div>
        </div>
      `,
    )
    .join('');
}

async function sendTranscript(text) {
  const response = await fetch('/api/voice/mock', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ transcript: text, mode: 'browser' }),
  });

  if (!response.ok) {
    throw new Error('Voice request failed');
  }

  const payload = await response.json();
  const utterance = new SpeechSynthesisUtterance(payload.reply);
  speechSynthesis.cancel();
  speechSynthesis.speak(utterance);
  userInput.value = '';
  await fetchRecentTraces();
}

sendButton.addEventListener('click', async () => {
  const text = userInput.value.trim();
  if (!text) {
    return;
  }
  await sendTranscript(text);
});

micButton.addEventListener('click', async () => {
  const SpeechRecognitionCtor =
    window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognitionCtor) {
    alert('Speech recognition is not available in this browser. Use the typed message box instead.');
    return;
  }

  const recognition = new SpeechRecognitionCtor();
  recognition.lang = 'en-US';
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    userInput.value = transcript;
    sendTranscript(transcript);
  };

  recognition.onerror = () => {
    alert('Mic capture failed. Please try again or type a message.');
  };

  recognition.start();
  micButton.textContent = 'Listening...';
  micButton.disabled = true;

  recognition.onend = () => {
    micButton.textContent = 'Start microphone';
    micButton.disabled = false;
  };
});

fetchRecentTraces();

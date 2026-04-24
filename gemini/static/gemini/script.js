const state = {
  audio: { streamer: null, player: null, isStreaming: false },
};

const elements = {};

function initDOM() {
  const ids = [
    "model",
    "systemInstructions",
    "enableInputTranscription",
    "enableOutputTranscription",
    "enableGrounding",
    "voiceSelect",
    "temperature",
    "temperatureValue",
    "disableActivityDetection",
    "silenceDuration",
    "prefixPadding",
    "endSpeechSensitivity",
    "startSpeechSensitivity",
    "activityHandling",
    "disconnectBtn",
    "connectionStatus",
    "statusDot",
    "startSessionBtn",
    "welcomeOverlay",
    "startAudioBtn",
    "micSelect",
    "volume",
    "volumeValue",
    "chatContainer",
    "chatInput",
    "sendBtn",
    "debugInfo",
    "recordSignatureBtn",
    "cloningStatus",
    "cloningToggle"
  ];

  ids.forEach((id) => {
    elements[id] = document.getElementById(id);
  });
}

async function populateMediaDevices() {
  try {
    const devices = await navigator.mediaDevices.enumerateDevices();
    elements.micSelect.innerHTML = '<option value="">Mikrofon</option>';
    devices
      .filter((device) => device.kind === "audioinput")
      .forEach((device) => {
        const option = document.createElement("option");
        option.value = device.deviceId;
        option.textContent = device.label || `Microphone ${device.deviceId.substr(0, 8)}`;
        elements.micSelect.appendChild(option);
      });
  } catch (error) {}
}

function createMessage(text, className = "") {
  const div = document.createElement("div");
  div.textContent = text;
  if (className) div.className = className;
  return div;
}

function updateStatus(elementId, text) {
  if (elements[elementId]) {
    elements[elementId].textContent = text;
    if (elements.statusDot) {
      if (text === "Connected") {
        elements.statusDot.classList.add("online");
      } else {
        elements.statusDot.classList.remove("online");
      }
    }
  }
}

async function connect() {
  try {
    const isOverlay = elements.welcomeOverlay && !elements.welcomeOverlay.classList.contains("hidden");
    if (isOverlay) {
      elements.startSessionBtn.textContent = "Bog'lanmoqda...";
      elements.startSessionBtn.disabled = true;
    }

    const response = await fetch("/api/gemini/token/", { method: "POST" });
    const { token } = await response.json();
    const model = elements.model.value;

    state.client = new GeminiLiveAPI(token, model);
    state.client.systemInstructions = elements.systemInstructions.value;
    state.client.inputAudioTranscription = elements.enableInputTranscription.checked;
    state.client.outputAudioTranscription = elements.enableOutputTranscription.checked;
    state.client.googleGrounding = elements.enableGrounding.checked;
    state.client.voiceName = elements.voiceSelect.value;
    state.client.temperature = parseFloat(elements.temperature.value);
    state.client.automaticActivityDetection = {
      disabled: elements.disableActivityDetection.checked,
      silence_duration_ms: parseInt(elements.silenceDuration.value),
      prefix_padding_ms: parseInt(elements.prefixPadding.value)
    };
    state.client.activityHandling = elements.activityHandling.value;

    state.client.onReceiveResponse = handleMessage;
    state.client.onError = () => updateStatus("connectionStatus", "Xatolik yuz berdi");
    state.client.onOpen = () => {
      updateStatus("connectionStatus", "Connected");
      if (isOverlay) elements.welcomeOverlay.classList.add("hidden");
    };
    state.client.onClose = disconnect;

    await state.client.connect();
    state.audio.streamer = new AudioStreamer(state.client);
    state.audio.player = new AudioPlayer();
    await state.audio.player.init();
  } catch (error) {
    if (elements.startSessionBtn) {
      elements.startSessionBtn.textContent = "Qayta urinish";
      elements.startSessionBtn.disabled = false;
    }
  }
}

function disconnect() {
  if (state.client && state.client.webSocket) {
    state.client.webSocket.close();
    state.client = null;
  }
  if (state.audio.streamer) state.audio.streamer.stop();
  state.audio.isStreaming = false;
  updateStatus("connectionStatus", "Oflayn");
  if (elements.startAudioBtn) elements.startAudioBtn.classList.remove("active");
  if (elements.welcomeOverlay) {
    elements.welcomeOverlay.classList.remove("hidden");
    elements.startSessionBtn.textContent = "Suhbatni boshlash";
    elements.startSessionBtn.disabled = false;
  }
}



async function handleMessage(message) {
  switch (message.type) {
    case MultimodalLiveResponseType.TEXT:
      addMessage(message.data, "assistant", true); // Use append mode for streaming UI
      break;
    case MultimodalLiveResponseType.AUDIO:
      if (state.audio.player) state.audio.player.play(message.data);
      break;
    case MultimodalLiveResponseType.INPUT_TRANSCRIPTION:
    case MultimodalLiveResponseType.OUTPUT_TRANSCRIPTION:
      break;
    case MultimodalLiveResponseType.INTERRUPTED:
      if (state.audio.player) state.audio.player.interrupt();
      break;
    case MultimodalLiveResponseType.TURN_COMPLETE:
      console.log("Turn complete received");
      break;
    case MultimodalLiveResponseType.SETUP_COMPLETE:
      addMessage("Suhbatga tayyorman!", "system");
      break;
  }
}

async function toggleAudio() {
  if (!state.audio.isStreaming) {
    try {
      if (state.audio.streamer) {
        await state.audio.streamer.start(elements.micSelect.value);
        state.audio.isStreaming = true;
        elements.startAudioBtn.classList.add("active");
      }
    } catch (error) {}
  } else {
    if (state.audio.streamer) state.audio.streamer.stop();
    state.audio.isStreaming = false;
    elements.startAudioBtn.classList.remove("active");
  }
}

function sendMessage() {
  const text = elements.chatInput.value.trim();
  if (!text || !state.client) return;
  addMessage(text, "user");
  state.client.sendTextMessage(text);
  elements.chatInput.value = "";
}

function addMessage(text, type, append = false) {
  const messages = elements.chatContainer.querySelectorAll("div");
  const last = messages[messages.length - 1];
  if (append && last && last.classList.contains(type)) {
    last.textContent += text;
  } else {
    elements.chatContainer.appendChild(createMessage(text, type));
  }
  elements.chatContainer.scrollTop = elements.chatContainer.scrollHeight;
}

function initEventListeners() {
  if (elements.startSessionBtn) elements.startSessionBtn.addEventListener("click", connect);
  if (elements.disconnectBtn) elements.disconnectBtn.addEventListener("click", disconnect);
  if (elements.startAudioBtn) elements.startAudioBtn.addEventListener("click", toggleAudio);
  if (elements.sendBtn) elements.sendBtn.addEventListener("click", sendMessage);
  if (elements.chatInput) {
    elements.chatInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") sendMessage();
    });
  }

}

window.addEventListener("DOMContentLoaded", () => {
  initDOM();
  initEventListeners();
  populateMediaDevices();
});

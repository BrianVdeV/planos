// static/js/chatbot.js

// Variable para rastrear qué botón se está reproduciendo actualmente
let currentButtonPlaying = null;

// 👇 1. FUNCIÓN DE LIMPIEZA
function cleanTextForTTS(text) {
    return text
        .replace(/\|/g, ', ')          // Tablas a pausas
        .replace(/[\*_]/g, '')         // Quitar negritas/cursivas
        .replace(/[#`]/g, '')          // Quitar numerales/código
        .replace(/^\s*-\s+/gm, '')     // Quitar guiones de lista
        .replace(/\s+/g, ' ')          // Quitar espacios extra
        .trim();
}

// 👇 2. CAMBIO VISUAL DE BOTONES
function setButtonToStop(btn) {
    btn.innerHTML = '<i class="mdi mdi-stop-circle-outline text-danger"></i> Parar';
    btn.classList.add("text-danger");
}

function setButtonToPlay(btn) {
    btn.innerHTML = '<i class="mdi mdi-volume-high text-primary"></i> Escuchar';
    btn.classList.remove("text-danger");
}

// 👇 3. FUNCIÓN PRINCIPAL (TOGGLE SPEECH)
window.toggleSpeech = function(elementId, btnElement) {
    // A. Lógica para PARAR si ya está hablando este mismo botón
    if (currentButtonPlaying === btnElement && window.speechSynthesis.speaking) {
        window.speechSynthesis.cancel();
        setButtonToPlay(btnElement);
        currentButtonPlaying = null;
        return;
    }

    // B. Parar cualquier otro audio previo
    window.speechSynthesis.cancel();
    if (currentButtonPlaying) {
        setButtonToPlay(currentButtonPlaying);
    }

    // C. Preparar el texto
    const container = document.getElementById(elementId);
    if (!container) return;
    
    const cleanText = cleanTextForTTS(container.innerText);
    const utterance = new SpeechSynthesisUtterance(cleanText);

    // 👇 D. CONFIGURACIÓN DE VOZ ÚNICA (MICROSOFT RAUL) 👇
    const voices = window.speechSynthesis.getVoices();
    
    // Buscamos EXACTAMENTE esta voz:
    const specificVoice = voices.find(voice => voice.name === "Microsoft Raul - Spanish (Mexico)");

    if (specificVoice) {
        utterance.voice = specificVoice;
        console.log("Usando voz:", specificVoice.name);
    } else {
        // Fallback de emergencia
        console.log("No se encontró 'Microsoft Raul'. Buscando alternativa masculina...");
        const backupVoice = voices.find(voice => 
            voice.name.includes("Pablo") || // Microsoft Pablo (España)
            (voice.name.includes("Male") && voice.lang.includes("es"))
        );
        if (backupVoice) utterance.voice = backupVoice;
    }

    utterance.lang = 'es-ES';
    utterance.rate = 1.2; // Velocidad normal

    // E. Eventos para resetear el botón cuando termine
    utterance.onend = function() {
        setButtonToPlay(btnElement);
        currentButtonPlaying = null;
    };
    utterance.onerror = function() {
        setButtonToPlay(btnElement);
        currentButtonPlaying = null;
    };

    // F. Ejecutar
    currentButtonPlaying = btnElement;
    setButtonToStop(btnElement);
    window.speechSynthesis.speak(utterance);
};


document.addEventListener("DOMContentLoaded", function () {
    const submitButton = document.getElementById("chat-submit");
    const chatInput = document.getElementById("chat-input");
    const chatMessages = document.getElementById("chat-messages");
    
    // NOTA: Usamos las variables globales definidas en el HTML
    // Si por alguna razón no existen, usamos valores por defecto para no romper el JS
    const apiEndpoint = (typeof CHATBOT_API_URL !== 'undefined') ? CHATBOT_API_URL : '/chatbot/api/query/';
    const securityToken = (typeof CSRF_TOKEN !== 'undefined') ? CSRF_TOKEN : document.getElementById("chatbot-csrf-token").value;

    const converter = new showdown.Converter();
    converter.setOption("tables", true);

    // Asegúrate de que esta ruta sea correcta en tu servidor
    const BOT_IMAGE_URL = "/static/images/chat-boot-planos-peru.ico"; 

    // --- Saludo Inicial ---
    if (chatMessages && chatMessages.innerHTML.trim() === "") {
        chatMessages.innerHTML = `
            <div class="d-flex flex-row justify-content-start mb-2">
                <img src="${BOT_IMAGE_URL}" alt="Asistente" class="chatbot-avatar me-2">
                <div class="chatbot-message-bubble p-2">
                    <p class="mb-0"><strong>Asistente:</strong> ¡Hola! Soy Asistente Planos Perú. ¿En qué puedo ayudarte hoy?</p>
                </div>
            </div>`;
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // --- Listeners ---
    submitButton.addEventListener("click", () => sendMessage());
    chatInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") sendMessage();
    });

    // --- Función Enviar ---
    function sendMessage() {
        const message = chatInput.value.trim();
        if (message === "" || !chatMessages) return;

        // Mostrar usuario
        chatMessages.innerHTML += `
            <div class="user-message-container">
                <div class="user-message-bubble p-2">
                    <p class="mb-0"><strong>Tú:</strong> ${message}</p>
                </div>
            </div>`;
        chatInput.value = "";
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Mostrar escribiendo...
        chatMessages.innerHTML += `
            <div id="bot-typing" class="d-flex flex-row justify-content-start mb-2">
                <img src="${BOT_IMAGE_URL}" alt="Asistente" class="chatbot-avatar me-2">
                <div class="chatbot-message-bubble p-2">
                    <p class="mb-0"><strong>Asistente:</strong> ...</p>
                </div>
            </div>`;
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // =======================================================
        // Fetch API (CORREGIDO PARA PRODUCCIÓN)
        // =======================================================
        fetch(apiEndpoint, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": securityToken, // Usamos el token seguro
            },
            body: JSON.stringify({ message: message }),
        })
        .then((response) => {
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return response.json();
        })
        .then((data) => {
            // Quitar loader
            const typingIndicator = document.getElementById("bot-typing");
            if (typingIndicator) typingIndicator.remove();

            // Convertir respuesta
            const htmlResponse = converter.makeHtml(data.response);
            const messageId = "msg-" + Date.now(); 

            // Insertar respuesta con botón Play/Stop
            chatMessages.innerHTML += `
                <div class="d-flex flex-row justify-content-start mb-2">
                    <img src="${BOT_IMAGE_URL}" alt="Asistente" class="chatbot-avatar me-2">
                    <div class="chatbot-message-bubble p-2">
                        <div id="${messageId}">
                            ${htmlResponse}
                        </div>
                        <div class="mt-2 text-end">
                            <button class="btn btn-sm btn-light border-0" onclick="toggleSpeech('${messageId}', this)" title="Reproducir / Parar">
                                <i class="mdi mdi-volume-high text-primary"></i> Escuchar
                            </button>
                        </div>
                    </div>
                </div>`;
            chatMessages.scrollTop = chatMessages.scrollHeight;
        })
        .catch((error) => {
            const typingIndicator = document.getElementById("bot-typing");
            if (typingIndicator) typingIndicator.remove();
            
            chatMessages.innerHTML += `
                <div class="d-flex flex-row justify-content-start mb-2">
                    <img src="${BOT_IMAGE_URL}" alt="Asistente" class="chatbot-avatar me-2">
                    <div class="chatbot-message-bubble p-2">
                        <p class="mb-0 text-danger"><strong>Error:</strong> No se pudo conectar con el servidor. (${error.message})</p>
                    </div>
                </div>`;
            chatMessages.scrollTop = chatMessages.scrollHeight;
        });
    }
});
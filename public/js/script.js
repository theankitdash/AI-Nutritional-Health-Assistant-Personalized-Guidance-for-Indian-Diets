// Initialize chat history
const chatHistoryList = document.getElementById('history-list');
const chatMessagesContainer = document.getElementById('messages');
const chatForm = document.getElementById('chat-form');
const messageInput = document.getElementById('message-input');
const uploadBtn = document.getElementById('upload-btn');
const fileInput = document.getElementById('file-input');
let chatHistory = [];
let activeChat = 'General';

// Event listener for sending a message
chatForm.addEventListener('submit', function (e) {
    e.preventDefault();
    const message = messageInput.value.trim();

    if (message !== '') {
        addMessageToChat(message, 'user');
        messageInput.value = '';

        // Simulate bot response
        setTimeout(() => {
            const botResponse = generateBotResponse(message);
            addMessageToChat(botResponse, 'bot');
        }, 1000);
    }
});

// Function to add a message to the chat
function addMessageToChat(message, sender) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('chat-message', sender);
    messageElement.textContent = message;
    chatMessagesContainer.appendChild(messageElement);

    chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight; // Auto-scroll to the bottom

    // Add to chat history
    chatHistory.push({ sender, message, chat: activeChat });
}

// Simulated bot response
function generateBotResponse(userMessage) {
    const responses = [
        "That's interesting!",
        "Can you tell me more?",
        "I’m here to help!",
        "Let's talk more about that.",
        "I see, tell me more."
    ];
    return responses[Math.floor(Math.random() * responses.length)];
}

// Event listener for file upload button
uploadBtn.addEventListener('click', function () {
    fileInput.click();
});

// Event listener for file input change
fileInput.addEventListener('change', function () {
    const file = fileInput.files[0];
    if (file) {
        const fileName = file.name;
        addMessageToChat(`File uploaded: ${fileName}`, 'user');
    }
});

// Load chat history (simulated)
function loadChatHistory() {
    chatHistory.forEach(entry => {
        if (entry.chat === activeChat) {
            addMessageToChat(entry.message, entry.sender);
        }
    });
}

// Display chat history on the sidebar
function displayChatHistory() {
    chatHistoryList.innerHTML = '';

    const uniqueChats = [...new Set(chatHistory.map(entry => entry.chat))];
    uniqueChats.forEach(chat => {
        const chatItem = document.createElement('li');
        chatItem.textContent = chat;
        chatItem.addEventListener('click', () => {
            switchChat(chat);
        });
        chatHistoryList.appendChild(chatItem);
    });
}

// Switch between different chats
function switchChat(chat) {
    activeChat = chat;
    document.getElementById('chat-topic').textContent = chat;
    chatMessagesContainer.innerHTML = '';
    loadChatHistory();
}

// Initialize the app by loading chat history
loadChatHistory();
displayChatHistory();

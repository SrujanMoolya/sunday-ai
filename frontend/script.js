const userInput = document.getElementById('userInput');
const sendButton = document.getElementById('sendButton');
const chatBox = document.getElementById('chatBox');

const BACKEND_URL = 'https://your-backend-url.onrender.com/query/'; // Update this

// Function to create a chat message
function addMessage(text, type) {
    const message = document.createElement('div');
    message.classList.add('message');
    if (type === 'user') {
        message.classList.add('user-message');
    } else if (type === 'ai') {
        message.classList.add('ai-message');
    } else if (type === 'error') {
        message.classList.add('error-message');
    }
    message.textContent = text;
    chatBox.appendChild(message);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Function to show loading state
function showLoading() {
    const loading = document.createElement('div');
    loading.classList.add('loading');
    loading.textContent = 'Thinking...';
    loading.id = 'loading';
    chatBox.appendChild(loading);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Function to remove loading state
function hideLoading() {
    const loading = document.getElementById('loading');
    if (loading) {
        chatBox.removeChild(loading);
    }
}

// Function to handle sending a message
async function sendMessage() {
    const query = userInput.value.trim();
    if (!query) return;

    addMessage(query, 'user');
    userInput.value = '';
    sendButton.disabled = true;

    showLoading();

    try {
        const response = await fetch(BACKEND_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query }),
        });

        hideLoading();

        if (response.ok) {
            const data = await response.json();
            const responseText = `**Topic:** ${data.topic}\n**Summary:** ${data.summary}\n**Sources:** ${data.sources.join(', ')}\n**Tools Used:** ${data.tools_used.join(', ')}`;
            addMessage(responseText, 'ai');
        } else {
            const error = await response.json();
            addMessage(`Error: ${error.detail}`, 'error');
        }
    } catch (error) {
        hideLoading();
        addMessage(`Error: ${error.message}`, 'error');
    }

    sendButton.disabled = false;
}

// Event Listeners
sendButton.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

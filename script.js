const userInput = document.getElementById('userInput');
const sendButton = document.getElementById('sendButton');
const chatBox = document.getElementById('chatBox');

const BACKEND_URL = 'https://sunday-ai.onrender.com/query/';

async function sendMessage() {
    const userMessage = document.getElementById('user-input').value;
    if (!userMessage) return;

    displayMessage('You', userMessage);

    try {
        const response = await fetch(BACKEND_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query: userMessage })
        });

        if (!response.ok) {
            throw new Error(`Error: ${response.statusText}`);
        }

        const data = await response.json();
        displayMessage('AI', `Topic: ${data.topic}\nSummary: ${data.summary}\nSources: ${data.sources.join(', ')}\nTools Used: ${data.tools_used.join(', ')}`);
    } catch (error) {
        console.error('Error:', error);
        displayMessage('AI', 'Something went wrong. Please try again.');
    }

    document.getElementById('user-input').value = '';
}

function displayMessage(sender, message) {
    const chatBox = document.getElementById('chat-box');
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', sender.toLowerCase());
    messageElement.innerText = `${sender}: ${message}`;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;
}

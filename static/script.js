function sendMessage() {
    const messageInput = document.getElementById('message');
    const usernameInput = document.getElementById('username');
    const message = messageInput.value;
    const user = usernameInput.value.trim();

    if (!user) {
        alert("Please enter your name!");
        return;
    }

    // Lock username after first message
    if (!usernameInput.disabled) {
        usernameInput.disabled = true;
        usernameInput.style.backgroundColor = "#eee";
    }

    if (message.trim() !== "") {
        socket.emit('send_message', { user: user, message: message });
        messageInput.value = '';
    }
}

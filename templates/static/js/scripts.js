document.getElementById("chat-form").addEventListener("submit", function(event) {
    event.preventDefault();
    const query = document.getElementById("user-query").value;
    fetch(`/chatbot?query=${query}`)
        .then(response => response.json())
        .then(data => {
            const chatBox = document.getElementById("chat-box");
            chatBox.innerHTML += `<p>User: ${query}</p>`;
            chatBox.innerHTML += `<p>Bot: ${data.response}</p>`;
            document.getElementById("user-query").value = '';
        });
});

function sendMessage() {
    let input = document.getElementById("userInput");
    let chatbox = document.getElementById("chatbox");
    let typingIndicator = document.getElementById("typingIndicator");

    let text = input.value.trim();
    if (text === "") return;

    // Add user message to chat
    chatbox.innerHTML += `<div class="message user">${text}</div>`;
    chatbox.scrollTop = chatbox.scrollHeight;

    input.value = "";
    
    // Show typing indicator
    typingIndicator.style.display = 'block';
    chatbox.scrollTop = chatbox.scrollHeight;

    // Send request to server
    fetch("https://dialogflow-personal-assistant.onrender.com/webhook", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            query: text   
        })
    })
    .then(res => res.json())
    .then(data => {
        // Hide typing indicator
        typingIndicator.style.display = 'none';
        
        let reply = data.fulfillmentText || "I didn't understand that.";
        chatbox.innerHTML += `<div class="message bot">${reply}</div>`;
        chatbox.scrollTop = chatbox.scrollHeight;
    })
    .catch(err => {
        // Hide typing indicator
        typingIndicator.style.display = 'none';
        
        chatbox.innerHTML += `<div class="message bot">Sorry, there was an error connecting to the server. Please try again later.</div>`;
        chatbox.scrollTop = chatbox.scrollHeight;
    });
}

// Add event listener for Enter key
document.getElementById("userInput").addEventListener("keydown", function(e) {
    if (e.key === "Enter") {
        sendMessage();
    }
});


console.log("Script loaded successfully");

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM fully loaded");
    
    const input = document.getElementById("userInput");
    const chatbox = document.getElementById("chatbox");
    const typingIndicator = document.getElementById("typingIndicator");
    const sendButton = document.getElementById("sendButton");

    if (!input || !chatbox || !typingIndicator || !sendButton) {
        console.error("One or more required elements not found:", {
            input: !!input,
            chatbox: !!chatbox,
            typingIndicator: !!typingIndicator,
            sendButton: !!sendButton
        });
        return;
    }

    function sendMessage() {
        let text = input.value.trim();
        console.log("Sending message:", text);
        
        if (text === "") return;

        // Add user message to chat
        chatbox.innerHTML += `<div class="message user">${text}</div>`;
        chatbox.scrollTop = chatbox.scrollHeight;

        input.value = "";
        
        // Show typing indicator
        typingIndicator.style.display = 'block';
        chatbox.scrollTop = chatbox.scrollHeight;

        // Send request to your Flask backend
        fetch("/webhook", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                query: text   
            })
        })
        .then(response => {
            console.log("Response status:", response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("Response data:", data);
            // Hide typing indicator
            typingIndicator.style.display = 'none';
            
            let reply = data.fulfillmentText || "I didn't understand that.";
            chatbox.innerHTML += `<div class="message bot">${reply}</div>`;
            chatbox.scrollTop = chatbox.scrollHeight;
        })
        .catch(err => {
            console.error("Fetch error:", err);
            // Hide typing indicator
            typingIndicator.style.display = 'none';
            
            chatbox.innerHTML += `<div class="message bot">Sorry, there was an error: ${err.message}</div>`;
            chatbox.scrollTop = chatbox.scrollHeight;
        });
    }

    // Add event listener for Enter key
    input.addEventListener("keydown", function(e) {
        if (e.key === "Enter") {
            console.log("Enter key pressed");
            sendMessage();
        }
    });

    // Add event listener for send button
    sendButton.addEventListener("click", function() {
        console.log("Send button clicked");
        sendMessage();
    });

    console.log("Event listeners attached successfully");
});

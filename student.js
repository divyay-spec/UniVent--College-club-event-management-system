// // Function to handle event registration
function registerEvent(eventId, button) {
    const confirmation = confirm("Do you want to register for this event?");
    if (!confirmation) return;

    fetch('/register_event', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ event_id: eventId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("Successfully registered!");
            button.innerText = "Registered";
            button.disabled = true;
            button.style.backgroundColor = "#2ecc71";
        } else {
            alert("Registration failed: " + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("Something went wrong.");
    });
}





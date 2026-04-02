//  function registerEvent(clubId)
//  {
//     const eventName = document.getElementById("eventName").value;
//     const eventDate = document.getElementById("eventDate").value;
//     const eventDescription = document.getElementById("eventDescription").value;
//     const clubId = document.body.getAttribute("data-club-id");

//     if (eventName === "" || eventDate === "" || eventDescription === "") {
//         alert("Please fill in all fields before registering the event.");
//         return;
//     }

//     fetch(`/create_event/${clubId}`, {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json'
//         },
//         body: JSON.stringify({
//             name: eventName,
//             date: eventDate,
//             description: eventDescription
//         })
//     })
//     .then(response => response.json())
//     .then(data => {
//         if (data.success) {
//             alert(`Event "${eventName}" requested successfully for ${eventDate}! Waiting for approval`);
//             clearForm();
//         } else {
//             alert("Event registration failed.");
//         }
//     })
//     .catch(error => {
//         alert("An error occurred.");
//         console.error(error);
//     });
// }
// function clearForm() {
//     document.getElementById("eventName").value = "";
//     document.getElementById("eventDate").value = "";
//     document.getElementById("eventDescription").value = "";
// }
function registerEvent() {
    const eventName = document.getElementById("eventName").value;
    const eventDate = document.getElementById("eventDate").value;
    const eventDescription = document.getElementById("eventDescription").value;
    const clubId = document.body.getAttribute("data-club-id");

    if (!eventName || !eventDate || !eventDescription) {
        alert("Please fill in all fields before registering the event.");
        return;
    }

    fetch(`/create_event/${clubId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            name: eventName,
            date: eventDate,
            description: eventDescription
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("🎉 Event sent for approval successfully!");
            clearForm();
        } else {
            alert("⚠️ Error: " + data.message);
        }
    })
    .catch((error) => {
        console.error("❌ Error occurred:", error);
        alert("Something went wrong while registering the event.");
    });
}

function clearForm() {
    document.getElementById("eventName").value = "";
    document.getElementById("eventDate").value = "";
    document.getElementById("eventDescription").value = "";
}
function loadEvents() {
    const clubId = document.body.getAttribute("data-club-id");

    fetch(`/president_events/${clubId}`)
        .then(response => response.json())
        .then(events => {
            const tbody = document.getElementById('eventsTableBody');
            tbody.innerHTML = "";

            if (events.length === 0) {
                const row = `<tr><td colspan="3">No events found.</td></tr>`;
                tbody.innerHTML = row;
                return;
            }
            events.forEach(event => {
                const row = `
                    <tr>
                        <td>${event.event_name}</td>
                        <td>${event.date}</td>
                        <td>${event.status}</td>
                        <td>
                            <button class="event-action-btn view-btn" onclick="viewParticipants(${event.event_id})">
                                View Participants
                            </button>
                        </td>
                    </tr>
                    <tr id="participants-${event.event_id}" style="display: none;">
                        <td colspan="4">
                            <div class="participants-list" id="participants-list-${event.event_id}">Loading...</div>
                        </td>
                    </tr>
                `;
                tbody.innerHTML += row;
            });
            
        })
        .catch(error => {
            console.error("Error loading events:", error);
        });
}

function viewParticipants(eventId) {
    const row = document.getElementById(`participants-${eventId}`);
    const container = document.getElementById(`participants-list-${eventId}`);

    if (row.style.display === "none") {
        row.style.display = "table-row";
        fetch(`/event_participants/${eventId}`)
            .then(response => response.json())
            .then(data => {
                if (data.length === 0) {
                    container.innerHTML = "<em>No participants registered.</em>";
                } else {
                    let list = "<ul>";
                    data.forEach(p => {
                        list += `<li>${p.name} (${p.email})</li>`;
                    });
                    list += "</ul>";
                    container.innerHTML = list;
                }
            })
            .catch(error => {
                console.error("Error fetching participants:", error);
                container.innerHTML = "Failed to load participants.";
            });
    } else {
        row.style.display = "none";
    }
}

function loadClubMembers() {
    const clubId = document.body.getAttribute("data-club-id");

    fetch(`/club_members/${clubId}`)
        .then(res => res.json())
        .then(data => {
            const tbody = document.getElementById("membersTableBody");
            tbody.innerHTML = "";

            data.forEach(member => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${member.name}</td>
                    <td>${member.email}</td>
                    <td>
                        <input type="text" value="${member.role_in_club}" id="role-${member.user_id}">
                    </td>
                    <td>
                        <button onclick="updateRole(${member.user_id})">Update</button>
                    </td>
                    <td>
                        <button onclick="removeMember(${member.user_id})">Remove</button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        });
}

function updateRole(userId) {
    const clubId = document.body.getAttribute("data-club-id");
    const newRole = document.getElementById(`role-${userId}`).value;

    fetch('/update_club_member_role', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ club_id: clubId, user_id: userId, role: newRole })
    })
    .then(res => res.json())
    .then(() => {
        alert("✅ Role updated");
    });
}

function removeMember(userId) {
    const clubId = document.body.getAttribute("data-club-id");
    if (confirm("Are you sure you want to remove this member?")) {
        fetch('/remove_club_member', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ club_id: clubId, user_id: userId })
        })
        .then(res => res.json())
        .then(() => {
            alert("🗑️ Member removed");
            loadClubMembers();
        });
    }
}

function addClubMember() {
    const clubId = document.body.getAttribute("data-club-id");
    const email = document.getElementById("newMemberEmail").value;
    const role = document.getElementById("newMemberRole").value;

    fetch('/add_club_member', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email, club_id: clubId, role: role })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert("✅ Member added");
            loadClubMembers();
            document.getElementById("newMemberEmail").value = "";
        } else {
            alert("❌ " + data.message);
        }
    });
}


document.addEventListener("DOMContentLoaded", () => {
    loadEvents();
    loadClubMembers(); 
    loadTotalParticipants(); // add this
});


// Load events on page load
document.addEventListener("DOMContentLoaded", loadEvents);

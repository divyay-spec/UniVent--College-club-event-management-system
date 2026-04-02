document.addEventListener("DOMContentLoaded", loadPendingEvents);

function loadPendingEvents() {
    fetch('/pending_events')
        .then(res => res.json())
        .then(events => {
            const tbody = document.getElementById("pendingEventsTableBody");
            tbody.innerHTML = "";

            if (events.length === 0) {
                tbody.innerHTML = "<tr><td colspan='5'>No pending event requests.</td></tr>";
                return;
            }

            events.forEach(event => {
                const row = `
                    <tr>
                        <td>${event.event_name}</td>
                        <td>${event.club_name}</td>
                        <td>${event.date}</td>
                        <td>${event.description}</td>
                        <td>
                            <button onclick="handleEventDecision(${event.event_id}, 'Approved')">✅ Approve</button>
                            <button onclick="handleEventDecision(${event.event_id}, 'Rejected')">❌ Reject</button>
                        </td>
                    </tr>
                `;
                tbody.innerHTML += row;
            });
        });
}

function handleEventDecision(eventId, decision) {
    fetch('/update_event_status', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ event_id: eventId, status: decision })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert(`Event ${decision} successfully!`);
            loadPendingEvents(); // reload updated list
        } else {
            alert("Failed to update event.");
        }
    });
}

document.addEventListener("DOMContentLoaded", loadResourceRequests);

function loadResourceRequests() {
    fetch('/pending_resource_requests')
        .then(res => res.json())
        .then(requests => {
            const tbody = document.getElementById("resourceRequestsBody");
            tbody.innerHTML = "";

            if (requests.length === 0) {
                tbody.innerHTML = "<tr><td colspan='7'>No pending resource requests.</td></tr>";
                return;
            }

            requests.forEach(req => {
                const row = `
    <tr>
        <td>${req.event_name}</td>
        <td>${req.resource_name} (${req.hall_name})</td>
        <td>${req.requested_quantity}</td>
        <td>${req.available_quantity}</td>

        <td>${req.club_name}</td>
        <td>${req.request_date}</td>
        <td>
           <input type="number" min="1" max="${Math.min(req.available_quantity, req.requested_quantity)}" id="allocate-${req.request_id}" 
  value="${Math.min(req.available_quantity, req.requested_quantity)}"/>
        </td>
        <td>
            <button onclick="handleResourceDecision(${req.request_id}, 'Approved')">✅ Approve</button>
            <button onclick="handleResourceDecision(${req.request_id}, 'Rejected')">❌ Reject</button>
        </td>
    </tr>
`;

                tbody.innerHTML += row;
            });
        });
}

function handleResourceDecision(requestId, status) {
    const input = document.getElementById(`allocate-${requestId}`);
    const allocated = status === 'Approved' ? parseInt(input.value) : null;

    fetch('/update_resource_request', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            request_id: requestId,
            status: status,
            allocated_quantity: allocated
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert(`Request ${status} successfully!`);
            loadResourceRequests();
        } else {
            alert("Update failed.");
        }
    });
}document.addEventListener("DOMContentLoaded", loadHallBookings);

function loadHallBookings() {
    fetch('/pending_hall_bookings')
        .then(res => res.json())
        .then(bookings => {
            const tbody = document.getElementById("hallBookingBody");
            tbody.innerHTML = "";

            if (bookings.length === 0) {
                tbody.innerHTML = "<tr><td colspan='5'>No pending hall bookings.</td></tr>";
                return;
            }

            bookings.forEach(b => {
                const row = `
                    <tr>
                        <td>${b.event_name}</td>
                        <td>${b.club_name}</td>
                        <td>${b.hall_name}</td>
                        <td>${b.date}</td>
                        <td>
                            <button onclick="handleHallDecision(${b.event_id}, 'Approved')">✅ Approve</button>
                            <button onclick="handleHallDecision(${b.event_id}, 'Rejected')">❌ Reject</button>
                        </td>
                    </tr>
                `;
                tbody.innerHTML += row;
            });
        });
}

function handleHallDecision(eventId, status) {
    fetch('/update_hall_booking', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ event_id: eventId, status: status })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert(`Booking ${status}`);
            loadHallBookings();
        } else {
            alert("Failed to update.");
        }
    });
}

// document.addEventListener("DOMContentLoaded", loadClubReports);

// function loadClubReports() {
//     fetch('/club_reports')
//         .then(res => res.json())
//         .then(reports => {
//             const tbody = document.getElementById("clubReportsBody");
//             tbody.innerHTML = "";

//             if (reports.length === 0) {
//                 tbody.innerHTML = "<tr><td colspan='3'>No data found.</td></tr>";
//                 return;
//             }

//             reports.forEach(club => {
//                 const row = `
//                     <tr>
//                         <td>${club.club_name}</td>
//                         <td>${club.total_events}</td>
//                         <td>${club.total_participants}</td>
//                     </tr>
//                 `;
//                 tbody.innerHTML += row;
//             });
//         })
//         .catch(error => {
//             console.error("Error loading club reports:", error);
//         });
// }

document.addEventListener("DOMContentLoaded", loadClubReports);

function loadClubReports() {
    fetch('/club_reports')
        .then(res => res.json())
        .then(reports => {
            const tbody = document.getElementById("clubReportsBody");
            tbody.innerHTML = "";

            if (!reports || reports.length === 0) {
                tbody.innerHTML = "<tr><td colspan='5'>No report data available</td></tr>";
                return;
            }

            reports.forEach(club => {
                const row = `
                    <tr>
                        <td>${club.club_name}</td>
                        <td>${club.total_events}</td>
                        <td>${club.approved_events}</td>
                        <td>${club.pending_events}</td>
                        <td>${club.rejected_events}</td>
                    </tr>
                `;
                tbody.innerHTML += row;
            });
        })
        .catch(err => {
            console.error("❌ Error fetching club reports:", err);
        });
}

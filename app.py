from flask import Flask, render_template, request, redirect, session
from flask import jsonify
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

#Connect to MySQL database
try:
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',  # Replace with your MySQL password
        database='proj'
    )
    cursor = connection.cursor(dictionary=True)
    print("✅ Connected to MySQL database successfully!")
except Error as e:
    print("❌ Error connecting to MySQL", e)

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',  # your password
        database='proj'
    )

# Route for login page
@app.route('/')
def home():
    return render_template('login.html')

# Route for handling login logic
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
    user = cursor.fetchone()

    if user:
        session['user_id'] = user['user_id']
        session['role'] = user['role']

        if user['role'] == 'Student':
            return redirect('/student_dashboard')
        elif user['role'] == 'President':
            cursor.execute("SELECT club_id FROM Clubs WHERE president_id = %s", (user['user_id'],))
            club = cursor.fetchone()
            if club:
             return redirect(f"/president_dashboard/{club['club_id']}")
            else:
             return "Club not found for this president."
        elif user['role'] in ['Faculty', 'Mentor']:
             return redirect('/admin_dashboard')


# Student Dashboard route - fetches upcoming approved events
@app.route('/student_dashboard')
def student_dashboard():
    if 'role' in session and session['role'] == 'Student':
        user_id = session['user_id']
        cursor = connection.cursor(dictionary=True)

        # Fetch upcoming approved events
        event_query = """
            SELECT Events.event_id,Events.event_name, Events.date, Clubs.club_name 
            FROM Events 
            JOIN Clubs ON Events.club_id = Clubs.club_id 
            WHERE Events.status = 'Approved' AND Events.date >= CURDATE()
            ORDER BY Events.date ASC
        """
        cursor.execute(event_query)
        events = cursor.fetchall()

        # Fetch all club info
        club_query = """
        SELECT Clubs.club_id, Clubs.club_name, Clubs.description, Users.name AS president_name
        FROM Clubs
         JOIN Users ON Clubs.president_id = Users.user_id
        """
        cursor.execute(club_query)
        clubs = cursor.fetchall()


        # Get event IDs the student has already registered for
        reg_ids_query = """
            SELECT event_id FROM event_registrations WHERE student_id = %s
        """
        cursor.execute(reg_ids_query, (user_id,))
        registered = cursor.fetchall()
        registered_event_ids = {r['event_id'] for r in registered}

        # Fetch full details of registered events
        reg_details_query = """
            SELECT Events.event_name, Events.date, Clubs.club_name 
            FROM Events 
            JOIN Clubs ON Events.club_id = Clubs.club_id 
            JOIN event_registrations ON Events.event_id = event_registrations.event_id 
            WHERE event_registrations.student_id = %s
            ORDER BY Events.date ASC
        """
        cursor.execute(reg_details_query, (user_id,))
        registered_events = cursor.fetchall()
        # cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        # user = cursor.fetchone()
        cursor.close()
        return render_template("student.html",events=events, registered_event_ids=registered_event_ids, registered_events=registered_events,clubs=clubs)
    else:
        return redirect('/')



@app.route('/register_event', methods=['POST'])
def register_event():
    if 'user_id' not in session or session['role'] != 'Student':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    data = request.get_json()
    event_id = data.get('event_id')

    try:
        cursor.execute(
            "INSERT INTO event_registrations (event_id, student_id) VALUES (%s, %s)",
            (event_id, session['user_id'])
        )
        connection.commit()
        return jsonify({'success': True})
    except mysql.connector.Error as err:
        return jsonify({'success': False, 'message': str(err)})
    
@app.route('/create_event/<int:club_id>', methods=['POST'])
def create_event(club_id):
    try:
        data = request.get_json()  # Get JSON data from the frontend
        name = data.get('name')
        date = data.get('date')
        description = data.get('description')

        if not name or not date or not description:
            return jsonify({'success': False, 'message': 'Missing fields'}), 400

        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO Events (event_name, date, description, club_id, status) VALUES (%s, %s, %s, %s, 'Pending')",
            (name, date, description, club_id)
        )
        connection.commit()
        cursor.close()

        return jsonify({'success': True, 'message': 'Event created successfully!'}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/president_dashboard/<int:club_id>')
def president_dashboard(club_id):
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM events WHERE club_id = %s", (club_id,))
        events = cursor.fetchall()
        cursor.close()

        return render_template("president.html", club_id=club_id, events=events)
    except Exception as e:
        return f"Error loading dashboard: {str(e)}"
    
@app.route('/president_events/<int:club_id>')
def president_events(club_id):
    try:
        cursor = connection.cursor(dictionary=True)
        # cursor.execute("SELECT event_name, date, status FROM events WHERE club_id = %s", (club_id,))
        cursor.execute("SELECT event_id, event_name, date, status FROM events WHERE club_id = %s", (club_id,))
        events = cursor.fetchall()
        cursor.close()
        return jsonify(events)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/event_participants/<int:event_id>')
def event_participants(event_id):
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT u.name, u.email
            FROM event_registrations er
            JOIN users u ON er.student_id = u.user_id
            WHERE er.event_id = %s
        """, (event_id,))
        participants = cursor.fetchall()
        cursor.close()
        return jsonify(participants)
    except Exception as e:
        print("❌ Error in /event_participants:", e)
        return jsonify({'error': str(e)}), 500

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'role' in session and session['role'] in ['Faculty', 'Mentor']:
        return render_template('admin.html')
    else:
        return redirect('/')

@app.route('/pending_events')
def pending_events():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT e.event_id, e.event_name, e.date, e.description, c.club_name
            FROM events e
            JOIN clubs c ON e.club_id = c.club_id
            WHERE e.status = 'Pending'
        """)
        events = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(events)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
 

# @app.route('/update_event_status', methods=['POST'])
# def update_event_status():
#     try:
#         data = request.get_json()
#         event_id = data.get('event_id')
#         status = data.get('status')

#         cursor = connection.cursor()
#         cursor.execute("UPDATE events SET status = %s WHERE event_id = %s", (status, event_id))
#         connection.commit()
#         cursor.close()

#         return jsonify({'success': True})
#     except Exception as e:
#         print("❌ Error updating event status:", e)
#         return jsonify({'success': False, 'error': str(e)})
    

@app.route('/pending_resource_requests')
def pending_resource_requests():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT rr.request_id, rr.requested_quantity, rr.request_date,
                   e.event_name, r.resource_name, r.available_quantity,
                   c.club_name, h.hall_name
            FROM resource_requests rr
            JOIN events e ON rr.event_id = e.event_id
            JOIN clubs c ON e.club_id = c.club_id
            JOIN resources r ON rr.resource_id = r.resource_id
            JOIN halls h ON r.hall_id = h.hall_id
            WHERE rr.status = 'Pending'
        """)
        requests = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(requests)
    except Exception as e:
        print("❌ Error loading resource requests:", e)
        return jsonify({'error': str(e)}), 500


@app.route('/update_resource_request', methods=['POST'])
def update_resource_request():
    try:
        data = request.get_json()
        request_id = data.get('request_id')
        status = data.get('status')
        allocated_quantity = data.get('allocated_quantity')

        cursor = connection.cursor()

        # Get the resource_id
        cursor.execute("SELECT resource_id FROM resource_requests WHERE request_id = %s", (request_id,))
        result = cursor.fetchone()
        resource_id = result[0] if result else None

        if status == 'Approved':
            # Update available quantity in Resources table
            cursor.execute("""
                UPDATE resources
                SET available_quantity = available_quantity - %s
                WHERE resource_id = %s
            """, (allocated_quantity, resource_id))

        # Update resource request table
        cursor.execute("""
            UPDATE resource_requests 
            SET status = %s, allocated_quantity = %s 
            WHERE request_id = %s
        """, (status, allocated_quantity if status == 'Approved' else None, request_id))

        connection.commit()
        cursor.close()

        return jsonify({'success': True})
    except Exception as e:
        print("❌ Error updating resource request:", e)
        return jsonify({'success': False, 'error': str(e)})

@app.route('/pending_hall_bookings')
def pending_hall_bookings():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT e.event_id, e.event_name, e.date, e.booking_status,
                   h.hall_name, c.club_name
            FROM events e
            JOIN halls h ON e.hall_id = h.hall_id
            JOIN clubs c ON e.club_id = c.club_id
            WHERE e.booking_status = 'Pending'
        """)
        bookings = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(bookings)
    except Exception as e:
        print("❌ Error loading hall bookings:", e)
        return jsonify({'error': str(e)}), 500

@app.route('/update_hall_booking', methods=['POST'])
def update_hall_booking():
    try:
        data = request.get_json()
        event_id = data.get('event_id')
        status = data.get('status')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE events SET booking_status = %s WHERE event_id = %s", (status, event_id))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'success': True})
    except Exception as e:
        print("❌ Error updating hall booking:", e)
        return jsonify({'success': False, 'error': str(e)})
    
# @app.route('/club_reports')
# def club_reports():
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)

#         cursor.execute("""
#             SELECT 
#                 c.club_name,
#                 COUNT(DISTINCT e.event_id) AS total_events,
#                 COUNT(er.registration_id) AS total_participants
#             FROM clubs c
#             LEFT JOIN events e ON c.club_id = e.club_id
#             LEFT JOIN event_registrations er ON e.event_id = er.event_id
#             GROUP BY c.club_id
#             ORDER BY c.club_name
#         """)

#         reports = cursor.fetchall()
#         cursor.close()
#         conn.close()
#         return jsonify(reports)
#     except Exception as e:
#         print("❌ Error loading club reports:", e)
#         return jsonify({'error': str(e)}), 500

# @app.route('/club_reports')
# def club_reports():
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)

#         # Step 1: Get all club IDs
#         cursor.execute("SELECT club_id FROM clubs")
#         clubs = cursor.fetchall()

#         all_reports = []

#         # Step 2: Call stored procedure for each club
#         for club in clubs:
#             club_id = club['club_id']
#             cursor.execute("CALL Club_Event_Stats(club_id)")
#             result = cursor.fetchone()
#             if result:
#                 all_reports.append(result)

#         cursor.close()
#         conn.close()
#         return jsonify(all_reports)

#     except Exception as e:
#         print("❌ Error loading club reports:", e)
#         return jsonify({'error': str(e)}), 500

@app.route('/club_report/<int:club_id>')
def single_club_report(club_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Call the stored procedure for the given club
        cursor.execute("CALL Club_Event_Stats(%s)", (club_id,))
        report = cursor.fetchone()

        cursor.close()
        conn.close()

        if report:
            return jsonify(report)
        else:
            return jsonify({'error': 'No report found'}), 404

    except Exception as e:
        print("❌ Error fetching club report:", e)
        return jsonify({'error': str(e)}), 500
    
@app.route('/club_reports')
def club_reports():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        print("✅ Connected to DB")

        # Get all club IDs
        cursor.execute("SELECT club_id FROM clubs")
        clubs = cursor.fetchall()
        print("📌 Fetched club IDs:", clubs)

        all_reports = []

        for club in clubs:
            club_id = club['club_id']
            print(f"📊 Calling procedure for club_id = {club_id}")
            cursor.execute("CALL Club_Event_Stats(%s)", (club_id,))
            result = cursor.fetchone()
            cursor.nextset()
            print(f"✅ Result for club {club_id}:", result)
            if result:
                all_reports.append(result)

        cursor.close()
        conn.close()

        return jsonify(all_reports)

    except Exception as e:
        print("❌ Error in /club_reports route:", e)
        return jsonify({'error': str(e)}), 500



import smtplib
from email.message import EmailMessage

def send_email_to_all_students(subject, body):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM users WHERE role = 'Student'")
        students = cursor.fetchall()
        cursor.close()
        conn.close()

        emails = [row[0] for row in students]

        # Setup email content
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = 'aarohan.arnav1@gmail.com'
        msg['To'] = 'nvinayake@gmail.com'
        #', '.join(emails)
        msg.set_content(body)

        # Setup SMTP (using Gmail)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login('aarohan.arnav1@gmail.com', 'mrsp xrhl nche utza')
            smtp.send_message(msg)

        print("✅ Emails sent successfully.")
    except Exception as e:
        print("❌ Email error:", e)

@app.route('/update_event_status', methods=['POST'])
def update_event_status():
    try:
        data = request.get_json()
        event_id = data.get('event_id')
        status = data.get('status')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Update event status
        cursor.execute("UPDATE events SET status = %s WHERE event_id = %s", (status, event_id))
        conn.commit()

        # Fetch event details
        cursor.execute("SELECT event_name, date FROM events WHERE event_id = %s", (event_id,))
        event = cursor.fetchone()

        cursor.close()
        conn.close()

        # Send email if approved
        if status == 'Approved' and event:
            # subject = f"New Upcoming Event Approved – {event['event_name']}"
            # body = f"Hello!\n\nThe event '{event['event_name']}' has been approved and is scheduled on {event['date']}.\n\nVisit your student dashboard to register now!"
            subject = f"🚀 You're Invited: {event['event_name']} is Coming up at MIT-WPU!"
            body = f"""
🎉 Hello there!

Great news! 🎊 The event **{event['event_name']}** is happening on 📅 {event['date']}.

Don’t miss your chance to be part of something exciting! 💡
Spots fill up fast, so head over to your Student Dashboard now and register 📝 before it's too late.

👉 Let’s make it an unforgettable experience!

Cheers,"""
            send_email_to_all_students(subject, body)

        return jsonify({'success': True})
    except Exception as e:
        print("❌ Error updating event status:", e)
        return jsonify({'success': False, 'error': str(e)})


@app.route('/student_stats/<int:user_id>')
def student_stats(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Total approved events
        cursor.execute("SELECT COUNT(*) AS total_events FROM Events WHERE status = 'Approved'")
        total_events = cursor.fetchone()['total_events']

        # Events the student has registered for
        cursor.execute("SELECT COUNT(*) AS registered_events FROM event_registrations WHERE user_id = %s", (user_id,))
        registered_events = cursor.fetchone()['registered_events']

        # Total clubs
        cursor.execute("SELECT COUNT(*) AS total_clubs FROM Clubs")
        total_clubs = cursor.fetchone()['total_clubs']

        cursor.close()
        conn.close()

        return jsonify({
            'total_events': total_events,
            'registered_events': registered_events,
            'total_clubs': total_clubs
        })

    except Exception as e:
        print("❌ Error fetching student stats:", e)
        return jsonify({'error': str(e)}), 500

@app.route('/club_members/<int:club_id>')
def get_club_members(club_id):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT u.user_id, u.name, u.email, m.role_in_club 
        FROM Memberships m
        JOIN Users u ON m.user_id = u.user_id
        WHERE m.club_id = %s
    """, (club_id,))
    members = cursor.fetchall()
    cursor.close()
    return jsonify(members)
@app.route('/add_club_member', methods=['POST'])
def add_club_member():
    data = request.get_json()
    email = data.get('email')
    club_id = data.get('club_id')
    role = data.get('role', 'Member')

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT user_id FROM Users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    user_id = user['user_id']

    # Check if already a member
    cursor.execute("SELECT * FROM Memberships WHERE club_id = %s AND user_id = %s", (club_id, user_id))
    if cursor.fetchone():
        return jsonify({'success': False, 'message': 'User already a member'}), 409

    cursor.execute("""
        INSERT INTO Memberships (user_id, club_id, role_in_club, joined_on)
        VALUES (%s, %s, %s, CURDATE())
    """, (user_id, club_id, role))
    connection.commit()
    cursor.close()
    return jsonify({'success': True})

@app.route('/update_club_member_role', methods=['POST'])
def update_club_member_role():
    try:
        data = request.get_json()
        user_id = data['user_id']
        club_id = data['club_id']
        role = data['role']

        cursor = connection.cursor()
        print(f"Updating club {club_id}, user {user_id} to role {role}")
        cursor.execute("""
            UPDATE Memberships
            SET role_in_club = %s
            WHERE user_id = %s AND club_id = %s
        """, (role, user_id, club_id))
        connection.commit()
        cursor.close()
        return jsonify({'success': True})
    except Exception as e:
        print("❌ Error in /update_club_member_role:", e)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/remove_club_member', methods=['POST'])
def remove_club_member():
    data = request.get_json()
    user_id = data['user_id']
    club_id = data['club_id']

    cursor = connection.cursor()
    cursor.execute("DELETE FROM Memberships WHERE user_id = %s AND club_id = %s", (user_id, club_id))
    connection.commit()
    cursor.close()
    return jsonify({'success': True})

@app.route('/president_dashboard2/<int:club_id>')
def president_dashboard2(club_id):
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM events WHERE club_id = %s AND date >= CURDATE() AND status = 'Approved' ORDER BY date ASC LIMIT 3", (club_id,))
        events = cursor.fetchall()
        cursor.close()

        return render_template("president.html", club_id=club_id, events=events)
    except Exception as e:
        return f"Error loading dashboard: {str(e)}"


# Logout route
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import Database, User, Movie, Show, Booking
import json
from datetime import datetime

# Create blueprints
auth_bp = Blueprint('auth', __name__)
main_bp = Blueprint('main', __name__)
movie_bp = Blueprint('movie', __name__)
booking_bp = Blueprint('booking', __name__)

# Authentication Routes
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': 'Invalid data received'}), 400
            
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        if password != confirm_password:
            return jsonify({'success': False, 'message': 'Passwords do not match'}), 400
        
        hashed_password = generate_password_hash(password)
        print(f"📝 Attempting to register user: {username}") # Debug print
        user = User.create_user(username, email, hashed_password)
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            print("✅ Registration successful")
            return jsonify({'success': True, 'message': 'Registration successful!'})
        else:
            return jsonify({'success': False, 'message': 'Username or email already exists'}), 400
    
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': 'Invalid data received'}), 400
            
        username = data.get('username')
        password = data.get('password')
        
        user = User.get_user_by_username(username)
        
        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            print(f"✅ User {username} logged in")
            return jsonify({'success': True, 'message': 'Login successful!'})
        else:
            return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))

# Main Routes
@main_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    movies = Movie.get_all_movies()
    return render_template('index.html', movies=movies, is_logged_in=True, username=session.get('username'))

@main_bp.route('/about')
def about():
    return render_template('about.html', is_logged_in='user_id' in session, username=session.get('username'))

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        data = request.get_json()
        # Here you can save contact messages to database or send email
        return jsonify({'success': True, 'message': 'Thank you for contacting us!'})
    return render_template('contact.html', is_logged_in='user_id' in session, username=session.get('username'))

# Movie Routes
@movie_bp.route('/movies')
def movies():
    all_movies = Movie.get_all_movies()
    return render_template('movies.html', movies=all_movies, is_logged_in='user_id' in session, username=session.get('username'))

@movie_bp.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    movie = Movie.get_movie_by_id(movie_id)
    shows = Show.get_shows_by_movie(movie_id)
    
    if not movie:
        return "Movie not found", 404
    
    # Group shows by date
    shows_by_date = {}
    for show in shows:
        try:
            dt = datetime.fromisoformat(show[3])
            date_key = dt.strftime('%Y-%m-%d')
            if date_key not in shows_by_date:
                shows_by_date[date_key] = []
            shows_by_date[date_key].append({
                'id': show[0],
                'theater': show[2],
                'time': dt.strftime('%I:%M %p'),
                'price': show[4],
                'available_seats': show[6]
            })
        except ValueError:
            continue
    
    # Sort dates and format for display
    formatted_shows = []
    for date_key in sorted(shows_by_date.keys()):
        dt = datetime.strptime(date_key, '%Y-%m-%d')
        formatted_shows.append({
            'date_display': dt.strftime('%A, %d %b'),
            'shows': shows_by_date[date_key]
        })
    
    return render_template('movie_detail.html', movie=movie, formatted_shows=formatted_shows, 
                         is_logged_in='user_id' in session, username=session.get('username'))

# Booking Routes
@booking_bp.route('/book/<int:show_id>')
def book_seats(show_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    show = Show.get_show_by_id(show_id)
    movie = Movie.get_movie_by_id(show[1])
    seats = Show.get_all_seats(show_id)
    
    # Format date and time for display
    show_dt = datetime.fromisoformat(show[3])
    show_date = show_dt.strftime('%a, %d %b %Y')
    show_time = show_dt.strftime('%I:%M %p')
    
    # Determine Shift (Morning, Afternoon, Evening, Night)
    hour = show_dt.hour
    if hour < 12:
        shift = "Morning"
    elif 12 <= hour < 17:
        shift = "Afternoon"
    elif 17 <= hour < 21:
        shift = "Evening"
    else:
        shift = "Night"
    
    seats_list = []
    for seat in seats:
        seats_list.append({
            'id': seat[0],
            'seat_number': seat[2],
            'is_booked': bool(seat[3])
        })
    
    return render_template('book_seats.html', show_id=show_id, movie=movie, 
                         show=show, seats=seats_list, show_date=show_date, show_time=show_time, shift=shift,
                         is_logged_in=True, username=session.get('username'))

@booking_bp.route('/api/book', methods=['POST'])
def confirm_booking():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'You are not logged in. Please log in to book tickets.'}), 401

    # Verify that the user in the session still exists in the database
    user = User.get_user_by_id(session['user_id'])
    if not user:
        session.clear() # Clear the invalid/stale session
        return jsonify({'success': False, 'message': 'Your session is invalid. Please log in again.'}), 401

    data = request.get_json()
    show_id = data.get('show_id')
    selected_seats = data.get('seats')

    if not show_id or not selected_seats or len(selected_seats) == 0:
        return jsonify({'success': False, 'message': 'Show or seat information is missing.'}), 400

    show = Show.get_show_by_id(show_id)
    if not show:
        return jsonify({'success': False, 'message': 'The selected show does not exist.'}), 404

    total_price = len(selected_seats) * show[4]

    booking_id = Booking.create_booking(session['user_id'], show_id, selected_seats, total_price)

    if booking_id:
        return jsonify({'success': True, 'message': 'Booking confirmed!', 'booking_id': booking_id})
    else:
        # This message is more specific about a potential race condition
        return jsonify({'success': False, 'message': 'Booking failed. One or more selected seats may have just been booked by someone else. Please refresh and try again.'}), 400

@booking_bp.route('/bookings')
def my_bookings():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    bookings = Booking.get_user_bookings(session['user_id'])
    
    bookings_list = []
    for booking in bookings:
        bookings_list.append({
            'id': booking[0],
            'user_id': booking[1],
            'show_id': booking[2],
            'seats': booking[3],
            'total_price': booking[4],
            'booking_date': booking[5],
            'status': booking[6],
            'movie_title': booking[7],
            'movie_poster': booking[8],
            'theater': booking[9],
            'show_time': booking[10]
        })
    
    return render_template('my_bookings.html', bookings=bookings_list,
                         is_logged_in=True, username=session.get('username'))

@booking_bp.route('/ticket/<int:booking_id>')
def ticket_view(booking_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        booking = Booking.get_booking_by_id(booking_id)
        
        if not booking:
            return "Booking not found", 404
        
        # Check if the booking belongs to the logged-in user
        # user_id is at index 12
        if booking[12] != session['user_id']:
            return "You are not authorized to view this ticket.", 403
        
        # Calculate Shift for Ticket
        show_dt = datetime.fromisoformat(booking[6])
        show_time_formatted = show_dt.strftime('%I:%M %p')
        show_date_formatted = show_dt.strftime('%A, %d %b %Y')
        hour = show_dt.hour
        if hour < 12:
            shift = "Morning"
        elif 12 <= hour < 17:
            shift = "Afternoon"
        elif 17 <= hour < 21:
            shift = "Evening"
        else:
            shift = "Night"

        # Convert tuple to a more usable dict for the template
        booking_dict = {
            'id': booking[0], 
            'seats': booking[1],          # Seat Numbers
            'total_price': booking[2],    # Payment Amount
            'booking_date': booking[3], 
            'status': booking[4], 
            'theater_name': booking[5],
            'show_time': show_time_formatted,
            'show_date': show_date_formatted,
            'title': booking[7],          # Movie Name
            'poster_url': booking[8],
            'duration': booking[9], 
            'language': booking[10], 
            'username': booking[11],
            'shift': shift
        }
        
        return render_template('ticket.html', booking=booking_dict, 
                               is_logged_in=True, username=session.get('username'))
                               
    except Exception as e:
        print(f"Error fetching ticket: {e}")
        return "Error loading ticket. Please refresh the page.", 500

@booking_bp.route('/api/cancel-booking/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    booking_id, message = Booking.cancel_booking(booking_id, session['user_id'])
    
    if booking_id:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'message': message}), 400

@booking_bp.route('/api/seats/<int:show_id>')
def get_seats(show_id):
    seats = Show.get_available_seats(show_id)
    all_seats = []
    
    for seat in seats:
        all_seats.append({
            'seat_number': seat[2],
            'is_booked': bool(seat[3])
        })
    
    return jsonify(all_seats)

# Admin Routes
admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
def admin_dashboard():
    # Simple admin check (in production, use proper authentication)
    admin_password = session.get('admin_logged_in')
    if not admin_password:
        return redirect(url_for('admin.admin_login'))
    
    movies = Movie.get_all_movies()
    movies_list = []
    for movie in movies:
        movies_list.append({
            'id': movie[0],
            'title': movie[1],
            'genre': movie[3],
            'rating': movie[4],
            'duration': movie[5],
            'language': movie[6],
            'poster': movie[7]
        })
    
    total_bookings = Booking.get_total_bookings_count()
    theater_bookings = Booking.get_bookings_by_theater()
    
    return render_template('admin_dashboard.html', movies=movies_list, total_bookings=total_bookings, theater_bookings=theater_bookings)

@admin_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        data = request.get_json()
        password = data.get('password')
        
        # Simple admin password (change this!)
        if password == 'admin123':
            session['admin_logged_in'] = True
            return jsonify({'success': True, 'message': 'Admin logged in!'})
        else:
            return jsonify({'success': False, 'message': 'Invalid password'}), 401
    
    return render_template('admin_login.html')

@admin_bp.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin.admin_login'))

@admin_bp.route('/api/admin/movies')
def get_admin_movies():
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Not authorized'}), 401
    
    movies = Movie.get_all_movies()
    movies_list = []
    for movie in movies:
        movies_list.append({
            'id': movie[0],
            'title': movie[1],
            'genre': movie[3],
            'rating': movie[4],
            'duration': movie[5],
            'language': movie[6],
            'poster': movie[7]
        })
    
    return jsonify(movies_list)

@admin_bp.route('/api/admin/add-movie', methods=['POST'])
def add_movie():
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Not authorized'}), 401
    
    data = request.get_json()
    
    # Validate and convert numeric fields safely
    try:
        rating = float(data.get('rating')) if data.get('rating') else 0.0
        duration = int(data.get('duration')) if data.get('duration') else 0
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid rating or duration'}), 400

    movie_id = Movie.add_movie(
        data.get('title'),
        data.get('description'),
        data.get('genre'),
        rating,
        duration,
        data.get('language'),
        data.get('poster')
    )
    
    if movie_id:
        return jsonify({'success': True, 'message': 'Movie added!', 'movie_id': movie_id})
    else:
        return jsonify({'success': False, 'message': 'Failed to add movie'}), 400

@admin_bp.route('/api/admin/delete-movie/<int:movie_id>', methods=['POST'])
def delete_movie(movie_id):
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Not authorized'}), 401
    
    if Movie.delete_movie(movie_id):
        return jsonify({'success': True, 'message': 'Movie deleted!'})
    else:
        return jsonify({'success': False, 'message': 'Failed to delete movie or movie not found.'}), 400

@admin_bp.route('/api/admin/add-show', methods=['POST'])
def add_show():
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Not authorized'}), 401
    
    data = request.get_json()
    try:
        movie_id = int(data.get('movie_id'))
        price = float(data.get('price'))
        show_time = data.get('show_time')
        theater = data.get('theater')

        if not all([movie_id, price, show_time, theater]):
             return jsonify({'success': False, 'message': 'Missing required fields.'}), 400

    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Invalid data format for movie_id or price.'}), 400

    show_id = Show.add_show(movie_id, theater, show_time, price)
    
    if show_id:
        return jsonify({'success': True, 'message': 'Show added!', 'show_id': show_id})
    else:
        return jsonify({'success': False, 'message': 'Failed to add show'}), 400

@admin_bp.route('/api/admin/movie-shows/<int:movie_id>')
def get_movie_shows(movie_id):
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Not authorized'}), 401
    
    shows = Show.get_shows_by_movie(movie_id)
    shows_list = []
    for show in shows:
        shows_list.append({
            'id': show[0],
            'theater': show[2],
            'show_time': show[3],
            'price': show[4],
            'available_seats': show[6]
        })
    
    return jsonify(shows_list)

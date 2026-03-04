from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, current_app
from app.models import Movie, Show, Booking
from collections import OrderedDict
import os
from werkzeug.utils import secure_filename

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
    
    # Group bookings by date and then by theater
    daily_theaters_raw = Booking.get_bookings_by_date_and_theater()
    daily_movies_raw = Booking.get_bookings_by_date_and_movie()
    daily_totals_raw = Booking.get_bookings_by_date()
    
    daily_stats = OrderedDict() # Use OrderedDict to keep dates sorted
    
    # Initialize with total counts for each day
    for date, total_count in daily_totals_raw:
        if date not in daily_stats:
            daily_stats[date] = {'total': total_count, 'theaters': [], 'movies': []}
        
    # Add theater breakdown
    for date, theater, count in daily_theaters_raw:
        if date in daily_stats:
            daily_stats[date]['theaters'].append({'name': theater, 'count': count})
    # Add movie breakdown
    for date, movie, count in daily_movies_raw:
        if date in daily_stats:
            daily_stats[date]['movies'].append({'title': movie, 'count': count})
    
    movie_wise_bookings = Booking.get_bookings_by_movie()
    
    # Group bookings by Theater then Movie
    theater_movie_raw = Booking.get_bookings_by_theater_and_movie()
    theater_movie_stats = {}
    for theater, movie, date, count in theater_movie_raw:
        if theater not in theater_movie_stats:
            theater_movie_stats[theater] = {}
        if movie not in theater_movie_stats[theater]:
            theater_movie_stats[theater][movie] = {'total': 0, 'dates': []}
        
        theater_movie_stats[theater][movie]['dates'].append({'date': date, 'count': count})
        theater_movie_stats[theater][movie]['total'] += count
    
    return render_template('admin_dashboard.html', movies=movies_list, total_bookings=total_bookings, theater_bookings=theater_bookings, daily_stats=daily_stats, movie_wise_bookings=movie_wise_bookings, theater_movie_stats=theater_movie_stats)

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
    
    # Use request.form for text data and request.files for images
    title = request.form.get('title')
    description = request.form.get('description')
    genre = request.form.get('genre')
    language = request.form.get('language')
    poster_url = request.form.get('poster_url') # Fallback URL
    
    # Validate and convert numeric fields safely
    try:
        rating = float(request.form.get('rating')) if request.form.get('rating') else 0.0
        duration = int(request.form.get('duration')) if request.form.get('duration') else 0
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid rating or duration'}), 400

    # Handle File Upload
    poster_path = poster_url
    if 'poster_file' in request.files:
        file = request.files['poster_file']
        if file.filename != '':
            filename = secure_filename(file.filename)
            upload_folder = os.path.join(current_app.root_path, '..', 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            file.save(os.path.join(upload_folder, filename))
            poster_path = f'/static/uploads/{filename}'

    movie_id = Movie.add_movie(
        title, description, genre,
        rating,
        duration,
        language,
        poster_path
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
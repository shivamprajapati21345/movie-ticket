from datetime import datetime
import sqlite3
import json
import os

DATABASE = 'movie_booking.db'

class Database:
    @staticmethod
    def init_db():
        """Initialize database with tables"""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Movies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                genre TEXT,
                rating REAL,
                duration INTEGER,
                language TEXT,
                poster_url TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Shows table (movie + time + theater)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                movie_id INTEGER NOT NULL,
                theater_name TEXT NOT NULL,
                show_time TIMESTAMP NOT NULL,
                price REAL NOT NULL,
                total_seats INTEGER DEFAULT 100,
                available_seats INTEGER DEFAULT 100,
                FOREIGN KEY(movie_id) REFERENCES movies(id)
            )
        ''')
        
        # Bookings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                show_id INTEGER NOT NULL,
                seats TEXT NOT NULL,
                total_price REAL NOT NULL,
                booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'confirmed',
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(show_id) REFERENCES shows(id)
            )
        ''')
        
        # Seats table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS seats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                show_id INTEGER NOT NULL,
                seat_number TEXT NOT NULL,
                is_booked INTEGER DEFAULT 0,
                booked_by INTEGER,
                UNIQUE(show_id, seat_number),
                FOREIGN KEY(show_id) REFERENCES shows(id),
                FOREIGN KEY(booked_by) REFERENCES users(id)
            )
        ''')
        
        conn.commit()
        conn.close()

class User:
    @staticmethod
    def create_user(username, email, password):
        """Create new user"""
        try:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (username, email, password)
                VALUES (?, ?, ?)
            ''', (username, email, password))
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            return {'id': user_id, 'username': username, 'email': email}
        except sqlite3.IntegrityError:
            return None

    @staticmethod
    def get_user_by_username(username):
        """Get user by username"""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        return user

    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        return user

class Movie:
    @staticmethod
    def add_movie(title, description, genre, rating, duration, language, poster_url):
        """Add new movie"""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO movies (title, description, genre, rating, duration, language, poster_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (title, description, genre, rating, duration, language, poster_url))
        conn.commit()
        movie_id = cursor.lastrowid
        conn.close()
        return movie_id

    @staticmethod
    def get_all_movies():
        """Get all active movies"""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM movies WHERE status = "active"')
        movies = cursor.fetchall()
        conn.close()
        return movies

    @staticmethod
    def get_movie_by_id(movie_id):
        """Get movie by ID"""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM movies WHERE id = ?', (movie_id,))
        movie = cursor.fetchone()
        conn.close()
        return movie

class Show:
    @staticmethod
    def add_show(movie_id, theater_name, show_time, price):
        """Add new show"""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO shows (movie_id, theater_name, show_time, price)
            VALUES (?, ?, ?, ?)
        ''', (movie_id, theater_name, show_time, price))
        conn.commit()
        show_id = cursor.lastrowid
        
        # Create seats for this show
        for row in range(1, 11):  # 10 rows
            for col in range(1, 11):  # 10 columns
                seat_number = f"{chr(64+row)}{col}"
                cursor.execute('''
                    INSERT INTO seats (show_id, seat_number)
                    VALUES (?, ?)
                ''', (show_id, seat_number))
        
        conn.commit()
        conn.close()
        return show_id

    @staticmethod
    def get_shows_by_movie(movie_id):
        """Get all shows for a movie"""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM shows WHERE movie_id = ?', (movie_id,))
        shows = cursor.fetchall()
        conn.close()
        return shows

    @staticmethod
    def get_show_by_id(show_id):
        """Get show by ID"""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM shows WHERE id = ?', (show_id,))
        show = cursor.fetchone()
        conn.close()
        return show

    @staticmethod
    def get_available_seats(show_id):
        """Get available seats for a show"""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM seats WHERE show_id = ? AND is_booked = 0', (show_id,))
        seats = cursor.fetchall()
        conn.close()
        return seats

class Booking:
    @staticmethod
    def create_booking(user_id, show_id, seats, total_price):
        """Create new booking"""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        try:
            # Insert booking
            cursor.execute('''
                INSERT INTO bookings (user_id, show_id, seats, total_price)
                VALUES (?, ?, ?, ?)
            ''', (user_id, show_id, ','.join(seats), total_price))
            
            booking_id = cursor.lastrowid
            
            # Mark seats as booked
            for seat in seats:
                cursor.execute('''
                    UPDATE seats SET is_booked = 1, booked_by = ?
                    WHERE show_id = ? AND seat_number = ?
                ''', (user_id, show_id, seat))
            
            # Update available seats in show
            cursor.execute('''
                UPDATE shows SET available_seats = available_seats - ?
                WHERE id = ?
            ''', (len(seats), show_id))
            
            conn.commit()
            conn.close()
            return booking_id
        except Exception as e:
            conn.close()
            return None

    @staticmethod
    def get_user_bookings(user_id):
        """Get all bookings for a user"""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT b.*, m.title, m.poster_url, sh.theater_name, sh.show_time
            FROM bookings b
            JOIN shows sh ON b.show_id = sh.id
            JOIN movies m ON sh.movie_id = m.id
            WHERE b.user_id = ?
            ORDER BY b.booking_date DESC
        ''', (user_id,))
        bookings = cursor.fetchall()
        conn.close()
        return bookings

    @staticmethod
    def get_booking_by_id(booking_id):
        """Get booking details"""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM bookings WHERE id = ?', (booking_id,))
        booking = cursor.fetchone()
        conn.close()
        return booking

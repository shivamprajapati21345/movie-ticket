from datetime import datetime
import sqlite3
import json
import os

DATABASE = 'movie_booking.db'

class Database:
    @staticmethod
    def init_db():
        """Initialize database with tables"""
        conn = sqlite3.connect(DATABASE, timeout=30)
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
        conn = sqlite3.connect(DATABASE, timeout=30)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO users (username, email, password)
                VALUES (?, ?, ?)
            ''', (username, email, password))
            conn.commit()
            user_id = cursor.lastrowid
            return {'id': user_id, 'username': username, 'email': email}
        except sqlite3.IntegrityError:
            return None
        except Exception as e:
            print(f"❌ Error creating user: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_user_by_username(username):
        """Get user by username"""
        conn = sqlite3.connect(DATABASE, timeout=30)
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            return user
        finally:
            conn.close()

    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        conn = sqlite3.connect(DATABASE, timeout=30)
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()
            return user
        finally:
            conn.close()

class Movie:
    @staticmethod
    def add_movie(title, description, genre, rating, duration, language, poster_url):
        """Add new movie"""
        conn = sqlite3.connect(DATABASE, timeout=30)
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO movies (title, description, genre, rating, duration, language, poster_url)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (title, description, genre, rating, duration, language, poster_url))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"❌ Error adding movie: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_all_movies():
        """Get all active movies"""
        conn = sqlite3.connect(DATABASE, timeout=30)
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM movies WHERE status = "active"')
            return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def get_movie_by_id(movie_id):
        """Get movie by ID"""
        conn = sqlite3.connect(DATABASE, timeout=30)
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM movies WHERE id = ?', (movie_id,))
            return cursor.fetchone()
        finally:
            conn.close()

    @staticmethod
    def delete_movie(movie_id):
        """Soft delete a movie by setting its status to 'inactive'."""
        conn = sqlite3.connect(DATABASE, timeout=30)
        try:
            cursor = conn.cursor()
            cursor.execute('UPDATE movies SET status = "inactive" WHERE id = ?', (movie_id,))
            conn.commit()
            return cursor.rowcount > 0 # Return True if a row was updated
        except Exception as e:
            print(f"❌ Error deleting movie: {e}")
            return False
        finally:
            conn.close()

class Show:
    @staticmethod
    def add_show(movie_id, theater_name, show_time, price):
        """Add new show and its seats atomically to prevent data inconsistency."""
        conn = sqlite3.connect(DATABASE, timeout=30)
        conn.isolation_level = None  # Disable automatic transactions
        cursor = conn.cursor()
        try:
            cursor.execute('BEGIN IMMEDIATE') # Start transaction and lock DB

            # Insert the show
            cursor.execute('''
                INSERT INTO shows (movie_id, theater_name, show_time, price)
                VALUES (?, ?, ?, ?)
            ''', (movie_id, theater_name, show_time, price))
            show_id = cursor.lastrowid
            
            # Create seats for this show using executemany for efficiency
            seats_to_insert = []
            for row in range(1, 11):  # 10 rows (A-J)
                for col in range(1, 11):  # 10 columns (1-10)
                    seat_number = f"{chr(64+row)}{col}"
                    seats_to_insert.append((show_id, seat_number))
            
            cursor.executemany('INSERT INTO seats (show_id, seat_number) VALUES (?, ?)', seats_to_insert)
            
            conn.commit()
            return show_id
        except Exception as e:
            conn.rollback() # Rollback on error
            print(f"❌ Error adding show/seats: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_shows_by_movie(movie_id):
        """Get all shows for a movie"""
        conn = sqlite3.connect(DATABASE, timeout=30)
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM shows WHERE movie_id = ? AND show_time > ?', (movie_id, datetime.now()))
            return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def get_show_by_id(show_id):
        """Get show by ID"""
        conn = sqlite3.connect(DATABASE, timeout=30)
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM shows WHERE id = ?', (show_id,))
            return cursor.fetchone()
        finally:
            conn.close()

    @staticmethod
    def get_available_seats(show_id):
        """Get available seats for a show"""
        conn = sqlite3.connect(DATABASE, timeout=30)
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM seats WHERE show_id = ? AND is_booked = 0', (show_id,))
            return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def get_all_seats(show_id):
        """Get all seats for a show (booked and available)"""
        conn = sqlite3.connect(DATABASE, timeout=30)
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM seats WHERE show_id = ?', (show_id,))
            return cursor.fetchall()
        finally:
            conn.close()

class Booking:
    @staticmethod
    def create_booking(user_id, show_id, seats, total_price):
        """Create new booking atomically and safely to prevent race conditions."""
        conn = sqlite3.connect(DATABASE, timeout=30)
        conn.isolation_level = None  # Disable automatic transactions
        cursor = conn.cursor()
        
        try:
            cursor.execute('BEGIN IMMEDIATE') # Start transaction and lock DB

            # Double-check if any of the selected seats are already booked
            for seat in seats:
                cursor.execute('SELECT is_booked FROM seats WHERE show_id = ? AND seat_number = ?', (show_id, seat))
                result = cursor.fetchone()
                if result is None or result[0] == 1:
                    conn.rollback()
                    print(f"❌ Booking Error: Seat {seat} for show {show_id} is already booked or invalid.")
                    return None

            # Insert booking record
            cursor.execute('''
                INSERT INTO bookings (user_id, show_id, seats, total_price)
                VALUES (?, ?, ?, ?)
            ''', (user_id, show_id, ','.join(seats), total_price))
            
            booking_id = cursor.lastrowid
            
            # Mark seats as booked in the seats table
            for seat in seats:
                cursor.execute('''
                    UPDATE seats SET is_booked = 1, booked_by = ?
                    WHERE show_id = ? AND seat_number = ?
                ''', (user_id, show_id, seat))
            
            # Update available seats count in the shows table
            cursor.execute('''
                UPDATE shows SET available_seats = available_seats - ?
                WHERE id = ?
            ''', (len(seats), show_id))
            
            conn.commit()
            return booking_id
        except Exception as e:
            conn.rollback()
            print(f"❌ Booking Error during transaction: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def cancel_booking(booking_id, user_id):
        """Cancel a booking, update seat status, and show availability."""
        conn = sqlite3.connect(DATABASE, timeout=30)
        conn.isolation_level = None  # Disable automatic transactions
        cursor = conn.cursor()
        
        try:
            cursor.execute('BEGIN IMMEDIATE') # Start transaction
            
            # 1. Get booking details and check ownership
            cursor.execute('SELECT show_id, seats, status FROM bookings WHERE id = ? AND user_id = ?', (booking_id, user_id))
            booking = cursor.fetchone()
            
            if not booking:
                # Booking not found or doesn't belong to the user
                return None, "Booking not found or you are not authorized to cancel it."
            
            if booking[2] == 'cancelled':
                return None, "Booking has already been cancelled."

            show_id, seats_str, status = booking
            seats_list = seats_str.split(',')
            
            # 2. Update booking status
            cursor.execute('UPDATE bookings SET status = "cancelled" WHERE id = ?', (booking_id,))
            
            # 3. Mark seats as available again
            for seat in seats_list:
                cursor.execute('''
                    UPDATE seats SET is_booked = 0, booked_by = NULL
                    WHERE show_id = ? AND seat_number = ?
                ''', (show_id, seat))
            
            # 4. Update available seats in shows table
            cursor.execute('''
                UPDATE shows SET available_seats = available_seats + ?
                WHERE id = ?
            ''', (len(seats_list), show_id))
            
            conn.commit()
            return booking_id, "Booking cancelled successfully."
        except Exception as e:
            conn.rollback()
            return None, f"An error occurred: {e}"
        finally:
            conn.close()

    @staticmethod
    def get_user_bookings(user_id):
        """Get all bookings for a user"""
        conn = sqlite3.connect(DATABASE, timeout=30)
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT b.*, m.title, m.poster_url, sh.theater_name, sh.show_time
                FROM bookings b
                JOIN shows sh ON b.show_id = sh.id
                JOIN movies m ON sh.movie_id = m.id
                WHERE b.user_id = ?
                ORDER BY b.booking_date DESC
            ''', (user_id,))
            return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def get_booking_by_id(booking_id):
        """Get booking details"""
        conn = sqlite3.connect(DATABASE, timeout=30)
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    b.id, b.seats, b.total_price, b.booking_date, b.status,
                    sh.theater_name, sh.show_time,
                    m.title, m.poster_url, m.duration, m.language,
                    u.username, b.user_id
                FROM bookings b
                JOIN shows sh ON b.show_id = sh.id
                JOIN movies m ON sh.movie_id = m.id
                JOIN users u ON b.user_id = u.id
                WHERE b.id = ?
            ''', (booking_id,))
            return cursor.fetchone()
        except Exception as e:
            print(f"❌ Error getting booking: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_total_bookings_count():
        """Get total number of confirmed bookings"""
        conn = sqlite3.connect(DATABASE, timeout=30)
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM bookings WHERE status = "confirmed"')
            return cursor.fetchone()[0]
        except Exception as e:
            print(f"❌ Error counting bookings: {e}")
            return 0
        finally:
            conn.close()

    @staticmethod
    def get_bookings_by_theater():
        """Get total bookings count per theater"""
        conn = sqlite3.connect(DATABASE, timeout=30)
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT s.theater_name, COUNT(b.id)
                FROM bookings b
                JOIN shows s ON b.show_id = s.id
                WHERE b.status = 'confirmed'
                GROUP BY s.theater_name
            ''')
            return cursor.fetchall()
        except Exception as e:
            print(f"❌ Error counting theater bookings: {e}")
            return []
        finally:
            conn.close()

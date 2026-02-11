# Shivam Booking - Movie Online Ticket Booking Website

A complete online movie ticket booking system built with Python Flask, SQLite, HTML5, CSS3, and JavaScript.

## Features

✨ **User Authentication**

- User registration and login
- Session management
- Secure password handling

🎬 **Movie Management**

- Browse all available movies
- View movie details (genre, duration, rating, language)
- Filter movies by various criteria

🎪 **Theater & Shows**

- Multiple theaters and show timings
- Real-time seat availability
- Dynamic pricing

🎫 **Booking System**

- Interactive seat selection
- Visual seat map (available, booked, selected)
- Instant booking confirmation
- View booking history

💳 **Payment Integration Ready**

- Price calculation
- Multiple payment options support

📱 **Responsive Design**

- Mobile-friendly interface
- Works on all devices
- Modern UI/UX

## Database Schema

### Users Table

├── app/
│ ├── **init**.py # Flask app initialization
│ ├── models.py # Database models
│ └── routes.py # API routes
├── templates/ # HTML templates
│ ├── base.html # Base template
│ ├── index.html # Home page
│ ├── login.html # Login page
│ ├── register.html # Registration page
│ ├── movies.html # Movies listing
│ ├── movie_detail.html # Movie details
│ ├── book_seats.html # Seat selection
│ ├── my_bookings.html # Booking history
│ ├── about.html # About page
│ └── contact.html # Contact page
├── static/
│ ├── css/
│ │ └── style.css # Main stylesheet
│ ├── js/
│ │ └── main.js # JavaScript utilities
│ └── images/ # Image assets
├── run.py # Application entry point
├── requirements.txt # Python dependencies
└── movie_booking.db # SQLite database

````

## Requirements

- Python 3.7+
- Flask 2.3.0
- Flask-Login 0.6.2
- Werkzeug 2.3.0

## Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
````

### 2. Run the Application

```bash
python run.py
```

The application will start on `http://localhost:5000`

## Usage

### For Users

1. **Register/Login** - Create an account or login
2. **Browse Movies** - View all available movies
3. **Select Show** - Choose a movie and select show timing
4. **Book Seats** - Select your preferred seats
5. **Confirm Booking** - Complete the booking process
6. **View Bookings** - Check your booking history

### For Developers

**Database Initialization**
The database is automatically initialized on first run with sample movies and shows.

**Adding More Content**
Edit the `run.py` file to add more movies and shows.

**Customization**

- Colors and theme: Edit `static/css/style.css`
- JavaScript functionality: Edit `static/js/main.js`
- Backend logic: Edit `app/routes.py`

## Database Schema

### Users Table

- id (Primary Key)
- username (Unique)
- email (Unique)
- password (Hashed)
- created_at

### Movies Table

- id (Primary Key)
- title
- description
- genre
- rating
- duration
- language
- poster_url
- status

### Shows Table

- id (Primary Key)
- movie_id (Foreign Key)
- theater_name
- show_time
- price
- total_seats
- available_seats

### Bookings Table

- id (Primary Key)
- user_id (Foreign Key)
- show_id (Foreign Key)
- seats
- total_price
- booking_date
- status

### Seats Table

- id (Primary Key)
- show_id (Foreign Key)
- seat_number
- is_booked
- booked_by (Foreign Key)

## API Endpoints

### Authentication

- `GET/POST /register` - User registration
- `GET/POST /login` - User login
- `GET /logout` - User logout

### Movies

- `GET /` - Home page
- `GET /movies` - List all movies
- `GET /movie/<id>` - Movie details

### Shows

- `GET /movie/<id>` - Get shows for a movie
- `GET /api/seats/<show_id>` - Get available seats

### Bookings

- `GET /book/<show_id>` - Booking page
- `POST /api/book` - Confirm booking
- `GET /bookings` - User's bookings

### Other

- `GET /about` - About page
- `GET /contact` - Contact page

## Features to Add

Future enhancements:

- Payment gateway integration (Razorpay, Stripe)
- Email confirmations
- Admin panel for movie/show management
- QR code generation for tickets
- Refund management
- Review and rating system
- Notification system
- Mobile app
- Advanced search and filtering

## Security Notes

⚠️ **Important**: Before deploying to production:

1. Change the `SECRET_KEY` in `app/__init__.py`
2. Configure proper error handling
3. Add input validation
4. Enable CSRF protection
5. Use environment variables for sensitive data
6. Set up proper logging
7. Configure HTTPS
8. Use a production WSGI server (Gunicorn, etc.)

## Default Sample Data

The application comes with sample data:

- **Movies**: Avengers, Inception, Dangal, The Dark Knight, Interstellar, Baahubali
- **Theaters**: PVR Cinemas, INOX, Cinepolis, Carnival
- **Shows**: 7 days of shows for each movie in each theater
- **Pricing**: ₹150 onwards

## Troubleshooting

**Database Locked Error**

- Ensure the database file is not locked by another process
- Delete `movie_booking.db` to start fresh

**Port Already in Use**

- Change the port in `run.py` from 5000 to another available port
- Or kill the process using port 5000

**Module Not Found**

- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version compatibility

## License

This project is open source and available for educational purposes.

## Support

For issues or suggestions, please contact us at: support@shivambooking.com

---

**Happy Booking! 🎬🎫**

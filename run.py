from app import create_app
from app.models import Database, Movie, Show
from datetime import datetime, timedelta

app = create_app()

# Initialize database with sample data
def init_database():
    """Initialize database with sample movies and shows"""
    Database.init_db()
    
    # Check if movies already exist
    existing_movies = Movie.get_all_movies()
    if not existing_movies:
        # Add sample movies
        movies_data = [
            {
                'title': 'Avengers: Endgame',
                'description': 'After the devastating events of Infinity War, the Avengers assemble once more to reverse Thanos actions and restore balance to the universe.',
                'genre': 'Action, Adventure, Sci-Fi',
                'rating': 8.4,
                'duration': 181,
                'language': 'English',
                'poster': 'https://upload.wikimedia.org/wikipedia/en/0/0d/Avengers_Endgame_poster.jpg'
            },
            {
                'title': 'Inception',
                'description': 'A skilled thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea.',
                'genre': 'Action, Sci-Fi, Thriller',
                'rating': 8.8,
                'duration': 148,
                'language': 'English',
                'poster': 'https://upload.wikimedia.org/wikipedia/en/2/2e/Inception_%282010%29_theatrical_poster.jpg'
            },
            {
                'title': 'Dangal',
                'description': 'A former wrestler and his two young daughters struggle to be heard in India.',
                'genre': 'Drama, Sport',
                'rating': 8.4,
                'duration': 161,
                'language': 'Hindi',
                'poster': 'https://upload.wikimedia.org/wikipedia/en/9/99/Dangal_Poster.jpg'
            },
            {
                'title': 'The Dark Knight',
                'description': 'When the menace known as the Joker wreaks havoc on Gotham, Batman must accept one of the greatest tests of his ability.',
                'genre': 'Action, Crime, Drama',
                'rating': 9.0,
                'duration': 152,
                'language': 'English',
                'poster': 'https://upload.wikimedia.org/wikipedia/en/1/1c/The_Dark_Knight_%282008_film%29.jpg'
            },
            {
                'title': 'Interstellar',
                'description': 'A team of explorers travel through a wormhole in space in an attempt to ensure humanity survival.',
                'genre': 'Adventure, Drama, Sci-Fi',
                'rating': 8.6,
                'duration': 169,
                'language': 'English',
                'poster': 'https://upload.wikimedia.org/wikipedia/en/b/bc/Interstellar_film_poster.jpg'
            },
            {
                'title': 'Baahubali',
                'description': 'An obscure warrior gets his chance to reign over the kingdom of Mahishmati.',
                'genre': 'Action, Adventure, Drama',
                'rating': 8.0,
                'duration': 159,
                'language': 'Telugu',
                'poster': 'https://upload.wikimedia.org/wikipedia/en/5/59/Baahubali_The_Beginning_poster.jpg'
            },
            {
                'title': 'The Raja Saab',
                'description': 'A romantic horror entertainer starring Prabhas, directed by Maruthi. A fun-filled ride with supernatural elements.',
                'genre': 'Horror, Comedy, Romance',
                'rating': 9.2,
                'duration': 150,
                'language': 'Telugu',
                'poster': 'https://assets-in.bmscdn.com/iedb/movies/images/mobile/thumbnail/xlarge/the-raja-saab-et00383559-1705306079.jpg'
            },
            {
                'title': 'Pushpa 2: The Rule',
                'description': 'The clash continues as Pushpa Raj asserts his dominance against Shekhawat in this high-octane action sequel.',
                'genre': 'Action, Crime, Thriller',
                'rating': 9.5,
                'duration': 180,
                'language': 'Telugu',
                'poster': 'https://upload.wikimedia.org/wikipedia/en/1/11/Pushpa_The_Rule_poster.jpg'
            },
            {
                'title': 'Kalki 2898 AD',
                'description': 'In a post-apocalyptic world, a modern avatar of Vishnu descends to protect humanity from darkness.',
                'genre': 'Sci-Fi, Action, Mythological',
                'rating': 9.0,
                'duration': 175,
                'language': 'Telugu',
                'poster': 'https://upload.wikimedia.org/wikipedia/en/4/4c/Kalki_2898_AD.jpg'
            }
        ]
        
        # Add movies
        for movie_data in movies_data:
            movie_id = Movie.add_movie(
                movie_data['title'],
                movie_data['description'],
                movie_data['genre'],
                movie_data['rating'],
                movie_data['duration'],
                movie_data['language'],
                movie_data['poster']
            )
            
            # Add shows for each movie
            theaters = ['PVR Cinemas', 'INOX', 'Cinepolis', 'Carnival']
            for theater in theaters:
                # Create shows for next 7 days
                for i in range(7):
                    # Define shifts: Morning, Afternoon, Evening, Night
                    shifts = [
                        {'hour': 10, 'minute': 0, 'price_mod': -10},    # 10:00 AM (Morning)
                        {'hour': 14, 'minute': 30, 'price_mod': 10},    # 02:30 PM (Afternoon)
                        {'hour': 19, 'minute': 0, 'price_mod': 30},     # 07:00 PM (Evening)
                        {'hour': 22, 'minute': 0, 'price_mod': 40}      # 10:00 PM (Night)
                    ]

                    for shift in shifts:
                        # Set the date and time for the show
                        show_time = (datetime.now() + timedelta(days=i)).replace(hour=shift['hour'], minute=shift['minute'], second=0, microsecond=0)
                        
                        price = 180 + shift['price_mod']
                        Show.add_show(movie_id, theater, show_time.isoformat(), price)
        print("✅ Database initialized with movies and posters successfully!")

if __name__ == '__main__':
    init_database()
    print("=" * 50)
    print("🎬 Shivam Booking - Movie Ticket Booking System")
    print("=" * 50)
    print("Starting Flask application...")
    print("Open your browser and go to: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)

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
                'poster': 'https://via.placeholder.com/250x350?text=Avengers+Endgame'
            },
            {
                'title': 'Inception',
                'description': 'A skilled thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea.',
                'genre': 'Action, Sci-Fi, Thriller',
                'rating': 8.8,
                'duration': 148,
                'language': 'English',
                'poster': 'https://via.placeholder.com/250x350?text=Inception'
            },
            {
                'title': 'Dangal',
                'description': 'A former wrestler and his two young daughters struggle to be heard in India.',
                'genre': 'Drama, Sport',
                'rating': 8.4,
                'duration': 161,
                'language': 'Hindi',
                'poster': 'https://via.placeholder.com/250x350?text=Dangal'
            },
            {
                'title': 'The Dark Knight',
                'description': 'When the menace known as the Joker wreaks havoc on Gotham, Batman must accept one of the greatest tests of his ability.',
                'genre': 'Action, Crime, Drama',
                'rating': 9.0,
                'duration': 152,
                'language': 'English',
                'poster': 'https://via.placeholder.com/250x350?text=The+Dark+Knight'
            },
            {
                'title': 'Interstellar',
                'description': 'A team of explorers travel through a wormhole in space in an attempt to ensure humanity survival.',
                'genre': 'Adventure, Drama, Sci-Fi',
                'rating': 8.6,
                'duration': 169,
                'language': 'English',
                'poster': 'https://via.placeholder.com/250x350?text=Interstellar'
            },
            {
                'title': 'Baahubali',
                'description': 'An obscure warrior gets his chance to reign over the kingdom of Mahishmati.',
                'genre': 'Action, Adventure, Drama',
                'rating': 8.0,
                'duration': 159,
                'language': 'Telugu',
                'poster': 'https://via.placeholder.com/250x350?text=Baahubali'
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
                    show_time = datetime.now() + timedelta(days=i, hours=18)
                    price = 150 + (i * 10)
                    Show.add_show(movie_id, theater, show_time.isoformat(), price)

if __name__ == '__main__':
    init_database()
    print("=" * 50)
    print("🎬 Shivam Booking - Movie Ticket Booking System")
    print("=" * 50)
    print("Starting Flask application...")
    print("Open your browser and go to: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)

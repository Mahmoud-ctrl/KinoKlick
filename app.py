
from datetime import date, datetime
from flask import Flask, jsonify, redirect, render_template, request, url_for
import sqlite3
import math
import random

app = Flask(__name__)

def get_movies(page, per_page):
    offset = (page - 1) * per_page
    today = datetime.today().strftime('%Y-%m-%d')
    
    try:
        conn = sqlite3.connect('movies.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, genres, release_date, rating, duration, overview, poster_path 
            FROM movies 
            WHERE release_date <= ? AND is_available = 1
            ORDER BY release_date DESC 
            LIMIT ? OFFSET ?
        """, (today, per_page, offset))
        movies = cursor.fetchall()
        
        cursor.execute("SELECT COUNT(*) FROM movies WHERE release_date <= ? AND is_available = 1", (today,))
        total = cursor.fetchone()[0]
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        movies, total = [], 0
    finally:
        conn.close()
    
    return movies, total

def get_movie(movie_id):
    today = datetime.today().strftime('%Y-%m-%d')
    
    try:
        conn = sqlite3.connect('movies.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, genres, release_date, rating, duration, overview, poster_path, top_billed_cast, cast_images, top_billed_cast_names, trailer_link 
            FROM movies 
            WHERE id = ? AND release_date <= ? AND is_available = 1
        """, (movie_id, today))
        movie = cursor.fetchone()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        movie = None
    finally:
        conn.close()
    
    return movie

def search_movies(query, limit=10, offset=0):
    today = datetime.today().strftime('%Y-%m-%d')
    
    try:
        conn = sqlite3.connect('movies.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, genres, release_date, rating, duration, overview, poster_path
            FROM movies
            WHERE title LIKE ? AND release_date <= ? AND is_available = 1
            ORDER BY release_date DESC
            LIMIT ? OFFSET ?
        """, ('%' + query + '%', today, limit, offset))
        movies = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        movies = []
    finally:
        conn.close()
    return movies


def get_latest_movies(limit=8):
    today = datetime.today().strftime('%Y-%m-%d')
    
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, background_image, genres, rating, duration, overview, trailer_link 
        FROM movies 
        WHERE release_date <= ? AND is_available = 1
        ORDER BY release_date DESC 
        LIMIT ?
    """, (today, limit))
    movies = cursor.fetchall()
    conn.close()
    return movies

def search_tv_shows(query, limit=10, offset=0):
    try:
        conn = sqlite3.connect('movies.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, genres, release_date, rating, poster_path
            FROM series
            WHERE title LIKE ?
            ORDER BY release_date DESC
            LIMIT ? OFFSET ?
        """, ('%' + query + '%', limit, offset))
        tv_shows = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        tv_shows = []
    finally:
        conn.close()
    return tv_shows


def execute_query(query, params):
    try:
        conn = sqlite3.connect('movies.db')
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        results = []
    finally:
        conn.close()
    return results

def get_recommendations(movie_id, limit=6):
    today = datetime.today().strftime('%Y-%m-%d')
    
    try:
        conn = sqlite3.connect('movies.db')
        cursor = conn.cursor()
        
        # Get the genres of the current movie
        cursor.execute("SELECT genres FROM movies WHERE id = ?", (movie_id,))
        genres = cursor.fetchone()[0]
        
        # Split genres into a list
        genre_list = genres.split(', ')
        
        # Create a SQL query that checks for any overlap in genres
        query = f"""
            SELECT id, poster_path, title 
            FROM movies 
            WHERE id != ? AND release_date <= ? AND (
        """
        query += " OR ".join(["genres LIKE ?"] * len(genre_list)) + ")"
        
        # Add wildcards to genre_list for partial matching
        genre_patterns = [f"%{genre}%" for genre in genre_list]
        
        # Execute the query with the movie_id, today's date, and genre patterns
        cursor.execute(query, (movie_id, today, *genre_patterns))
        recommendations = cursor.fetchall()
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        recommendations = []
    finally:
        conn.close()
    
    # Return a random sample of the recommendations
    return random.sample(recommendations, min(len(recommendations), limit))

def get_tv_shows(page, per_page, genre=None, year=None, rating=None):
    query = "SELECT id, title, genres, release_date, rating, poster_path FROM series WHERE 1=1"
    params = []

    if genre:
        query += " AND genres LIKE ?"
        params.append('%' + genre + '%')
    if year:
        query += " AND strftime('%Y', release_date) = ?"
        params.append(year)
    if rating:
        query += " AND rating >= ?"
        params.append(float(rating))

    # Order by release_date descending
    query += " ORDER BY release_date DESC"

    # Add LIMIT and OFFSET for pagination
    offset = (page - 1) * per_page
    query += " LIMIT ? OFFSET ?"
    params.extend([per_page, offset])

    tv_shows = execute_query(query, params)

    # Retrieve the total count for pagination
    count_query = "SELECT COUNT(*) FROM series WHERE 1=1"
    count_params = []

    if genre:
        count_query += " AND genres LIKE ?"
        count_params.append('%' + genre + '%')
    if year:
        count_query += " AND strftime('%Y', release_date) = ?"
        count_params.append(year)
    if rating:
        count_query += " AND rating >= ?"
        count_params.append(float(rating))

    total_count = execute_query(count_query, count_params)[0][0]

    return tv_shows, total_count



def get_series(series_id):
    try:
        conn = sqlite3.connect('movies.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, overview, genres, release_date, rating, poster_path, top_billed_cast, cast_images, top_billed_cast_names, trailer_link FROM series WHERE id = ?", (series_id,))
        series = cursor.fetchone()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        series = None
    finally:
        conn.close()
    return series

def get_seasons(series_id):
    try:
        conn = sqlite3.connect('movies.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, season_number FROM seasons WHERE series_id = ?", (series_id,))
        seasons = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        seasons = []
    finally:
        conn.close()
    return seasons

def get_episodes(series_id, season_number):
    try:
        conn = sqlite3.connect('movies.db')
        cursor = conn.cursor()

        # Get the episodes for the given season_number and series_id
        cursor.execute("""
            SELECT id, episode_number, title, overview, release_date, rating, poster_path 
            FROM episodes 
            WHERE series_id = ? AND season_id = ?
        """, (series_id, season_number))

        episodes = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        episodes = []
    finally:
        conn.close()

    return episodes

def get_series_recommendations(series_id, limit=6):
    try:
        conn = sqlite3.connect('movies.db')
        cursor = conn.cursor()
        
        # Get the genres of the current series
        cursor.execute("SELECT genres FROM series WHERE id = ?", (series_id,))
        genres = cursor.fetchone()[0]
        
        # Split genres into a list
        genre_list = genres.split(', ')
        
        # Create a SQL query that checks for any overlap in genres
        query = f"""
            SELECT id, poster_path, title 
            FROM series 
            WHERE id != ? AND (
        """
        query += " OR ".join(["genres LIKE ?"] * len(genre_list)) + ")"
        
        # Add wildcards to genre_list for partial matching
        genre_patterns = [f"%{genre}%" for genre in genre_list]
        
        # Execute the query with the series_id and genre patterns
        cursor.execute(query, (series_id, *genre_patterns))
        recommendations = cursor.fetchall()
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        recommendations = []
    finally:
        conn.close()
    
    # Return a random sample of the recommendations
    return random.sample(recommendations, min(len(recommendations), limit))

def get_movies_by_category(category):
    today = datetime.today().strftime('%Y-%m-%d')
    
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()
    # Use '%' wildcards to allow for partial matches before and after the category string
    query = f"%{category}%"
    cursor.execute("""
        SELECT id, poster_path, title, rating 
        FROM movies 
        WHERE genres LIKE ? AND release_date <= ? 
        ORDER BY release_date DESC 
        LIMIT 100
    """, (query, today))
    movies = cursor.fetchall()
    conn.close()
    return movies


def get_random_recommendations(table, min_rating=8.5, limit=6):
    today = datetime.today().strftime('%Y-%m-%d')
    
    try:
        conn = sqlite3.connect('movies.db')
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT id, poster_path, title, release_date, rating 
            FROM {table} 
            WHERE rating >= ? AND release_date <= ?
        """, (min_rating, today))
        items = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        items = []
    finally:
        conn.close()
    
    return random.sample(items, min(len(items), limit))

def get_movie_recommendations():
    return get_random_recommendations('movies')

def get_tv_show_recommendations():
    return get_random_recommendations('series')

def dateformat(value):
    if value.strip() == "":
        return "N/A"  # or return any default value like "N/A"
    try:
        date = datetime.strptime(value, '%Y-%m-%d')
        return date.strftime('%d/%m/%Y')
    except ValueError:
        return "Invalid date"  # or handle the error in another way

app.jinja_env.filters['dateformat'] = dateformat

def format_date(date_str):
    if date_str.strip() == "":
        return "N/A"  # or return any default value like "N/A"
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%b %d, %Y')
    except ValueError:
        return "Invalid date"  # or handle the error in another way
app.jinja_env.filters['formatDate'] = format_date


# Custom adapter and converter for date objects
def adapt_date(iso_date):
    return iso_date.strftime("%Y-%m-%d")

def convert_date(bytestring):
    return datetime.strptime(bytestring.decode("utf-8"), "%Y-%m-%d").date()

# Register the adapter and converter with sqlite3
sqlite3.register_adapter(date, adapt_date)
sqlite3.register_converter("date", convert_date)

def get_upcoming_movies(limit=9):
    current_date = datetime.now().date()
    try:
        conn = sqlite3.connect('movies.db', detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = conn.cursor()
        
        # Step 1: Retrieve upcoming movies
        cursor.execute("""
            SELECT id, title, genres, release_date, rating, duration, overview, poster_path
            FROM movies
            WHERE release_date > ?
            ORDER BY release_date ASC
            LIMIT ?
        """, (current_date, limit))
        upcoming_movies = cursor.fetchall()
        
        # Step 2: Update 'is_available' to 0 for movies with today's release date
        cursor.execute("""
            UPDATE movies
            SET is_available = 0
            WHERE release_date = ?
        """, (current_date,))
        conn.commit()
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        upcoming_movies = []
    finally:
        conn.close()
        
    return upcoming_movies


@app.route('/')
def index():
    action_adventure = get_movies_by_category('Action, Adventure')
    animation = get_movies_by_category('animation')
    comedy = get_movies_by_category('comedy')
    horror = get_movies_by_category('horror')
    scifi = get_movies_by_category('Science Fiction')
    romance = get_movies_by_category('Romance')
    crime = get_movies_by_category('Crime')
    latest_movies = get_latest_movies()  
    upcoming_movies = get_upcoming_movies()
    
    return render_template('index.html', 
                           action_adventure=action_adventure,
                           horror=horror,
                           comedy=comedy,
                           romance=romance,
                           scifi=scifi,
                           crime=crime,
                           animation=animation,
                           latest_movies=latest_movies,
                           upcoming_movies=upcoming_movies
                          )

@app.route('/movies')
def movies():
    page = request.args.get('page', 1, type=int)
    max_pages_to_show = request.args.get('max_pages_to_show', 7, type=int)  # Default to 7 if not provided
    per_page = 54  # Number of movies per page
    movies, total = get_movies(page, per_page)
    total_pages = math.ceil(total / per_page)
    
    # Define the range of pages to display
    start_page = max(1, page - max_pages_to_show // 2)
    end_page = min(total_pages, start_page + max_pages_to_show - 1)
    
    # Adjust start_page if there aren't enough pages at the end
    if end_page - start_page < max_pages_to_show:
        start_page = max(1, end_page - max_pages_to_show + 1)
    
    return render_template('movies.html', movies=movies, page=page, total_pages=total_pages, start_page=start_page, end_page=end_page)

@app.route('/movie/<int:movie_id>-<string:title>')
def movie(movie_id, title):
    movie = get_movie(movie_id)
    if not movie:
        return "Movie not found", 404
    
    # Validate the title
    db_title = movie[1].replace(' ', '-').lower()
    if title != db_title:
        return redirect(url_for('movie', movie_id=movie_id, title=db_title))

    recommendations = get_recommendations(movie_id)  # Function to fetch recommendations

    # List of server embed URLs
    embed_urls = {
        "Server 1": f"https://vidsrc.in/embed/movie/{movie[0]}",
        "Server 2": f"https://www.2embed.cc/embed/{movie[0]}",
        "Server 3": f"https://vidsrc.cc/v2/embed/movie/{movie[0]}",
        "Server 4": f"https://vidsrc.pro/embed/movie/{movie[0]}"
    }

    return render_template('movie.html', movie=movie, recommendations=recommendations, embed_urls=embed_urls, zip=zip)


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    movie_results = search_movies(query)
    tv_show_results = search_tv_shows(query)
    return render_template('search_results.html', query=query, movie_results=movie_results, tv_show_results=tv_show_results)

@app.route('/load-more-movies', methods=['GET'])
def load_more_movies():
    query = request.args.get('query', '')
    offset = request.args.get('offset', 0, type=int)
    movie_results = search_movies(query, offset=offset)
    
    if not movie_results:
        return jsonify({'movie_results': [], 'no_more_results': True})
    
    return jsonify({
        'movie_results': [{
            'id': movie[0],
            'title': movie[1],
            'poster': movie[7],
            'rating': movie[4],
            'release_date': movie[3]
        } for movie in movie_results],
        'no_more_results': False
    })

@app.route('/load-more-tv-shows', methods=['GET'])
def load_more_tv_shows():
    query = request.args.get('query', '')
    offset = request.args.get('offset', 0, type=int)
    tv_show_results = search_tv_shows(query, offset=offset)
    return jsonify(tv_show_results=[{
        'id': show[0],
        'title': show[1],
        'poster': show[5],
        'rating': show[4],
        'release_date': show[3]
    } for show in tv_show_results])


@app.route('/search-suggestions', methods=['GET'])
def search_suggestions():
    query = request.args.get('query', '')
    movie_results = search_movies(query)
    tv_show_results = search_tv_shows(query)
    suggestions = [
        {'id': movie[0], 'title': movie[1], 'poster': movie[7], 'rating': "%.1f" % movie[4], 'type': 'movie'} 
        for movie in movie_results
    ] + [
        {'id': show[0], 'title': show[1], 'poster': show[5], 'rating': "%.1f" % show[4], 'type': 'tv_show'} 
        for show in tv_show_results
    ]
    return jsonify(suggestions=suggestions)

@app.route('/filter-movies', methods=['GET'])
def filter_movies():
    genre = request.args.get('genre')
    year = request.args.get('year')
    rating = request.args.get('rating')
    page = request.args.get('page', 1, type=int)
    per_page = 54  # Number of movies per page
    today = datetime.today().strftime('%Y-%m-%d')

    query = """
        SELECT id, title, genres, release_date, rating, duration, overview, poster_path 
        FROM movies 
        WHERE release_date <= ? AND is_available = 1
    """
    count_query = """
        SELECT COUNT(*) 
        FROM movies 
        WHERE release_date <= ? AND is_available = 1
    """
    params = [today]

    if genre and genre != "":  # Check if genre is provided and not empty
        query += " AND genres LIKE ?"
        count_query += " AND genres LIKE ?"
        params.append('%' + genre + '%')

    if year and year != "":  # Check if year is provided and not empty
        query += " AND strftime('%Y', release_date) = ?"
        count_query += " AND strftime('%Y', release_date) = ?"
        params.append(year)

    if rating and rating != "":  # Check if rating is provided and not empty
        query += " AND rating >= ?"
        count_query += " AND rating >= ?"
        params.append(float(rating))

    # Order by release_date descending
    query += " ORDER BY release_date DESC"
    query += " LIMIT ? OFFSET ?"
    
    offset = (page - 1) * per_page
    params.extend([per_page, offset])

    try:
        conn = sqlite3.connect('movies.db')
        cursor = conn.cursor()
        cursor.execute(query, params)
        movies = cursor.fetchall()

        cursor.execute(count_query, params[:-2])
        total = cursor.fetchone()[0]
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        movies, total = [], 0
    finally:
        conn.close()

    total_pages = math.ceil(total / per_page)
    
    return jsonify(movies=[{
        'id': movie[0],
        'title': movie[1],
        'poster': movie[7],
        'rating': movie[4],
        'releaseDate': format_date(movie[3])
    } for movie in movies], total_pages=total_pages, current_page=page)


@app.route('/filter-tv-shows', methods=['GET'])
def filter_tv_shows():
    genre = request.args.get('genre')
    year = request.args.get('year')
    rating = request.args.get('rating')
    
    query = "SELECT id, title, genres, release_date, rating, poster_path FROM series WHERE 1=1"
    params = []
    
    if genre:
        query += " AND genres LIKE ?"
        params.append('%' + genre + '%')
    if year:
        query += " AND strftime('%Y', release_date) = ?"
        params.append(year)
    if rating:
        query += " AND rating >= ?"
        params.append(float(rating))

    query += " ORDER BY release_date DESC"
    
    shows = execute_query(query, params)
    
    return jsonify(shows=[{
        'id': show[0],
        'title': show[1],
        'poster': show[5],
        'rating': show[4],
        'releaseDate': format_date(show[3])
    } for show in shows])

@app.route('/tv-shows')
def tv_shows():
    page = request.args.get('page', 1, type=int)
    genre = request.args.get('genre')
    year = request.args.get('year')
    rating = request.args.get('rating')
    max_pages_to_show = request.args.get('max_pages_to_show', 7, type=int)  # Default to 7 if not provided
    per_page = 54  # Number of TV shows per page

    tv_shows, total = get_tv_shows(page, per_page, genre, year, rating)
    total_pages = math.ceil(total / per_page)
    
    # Define the range of pages to display
    start_page = max(1, page - max_pages_to_show // 2)
    end_page = min(total_pages, start_page + max_pages_to_show - 1)
    
    # Adjust start_page if there aren't enough pages at the end
    if end_page - start_page < max_pages_to_show:
        start_page = max(1, end_page - max_pages_to_show + 1)
    
    return render_template('tv_shows.html', tv_shows=tv_shows, page=page, total_pages=total_pages, start_page=start_page, end_page=end_page)

@app.route('/tv-show/<int:series_id>-<string:title>')
def tv_show(series_id, title):
    series = get_series(series_id)
    if not series:
        return "TV Show not found", 404
    
    # Validate the title
    db_title = series[1].replace(' ', '-').lower()
    if title != db_title:
        return redirect(url_for('tv_show', series_id=series_id, title=db_title))
    
    seasons = get_seasons(series_id)
    season_number = request.args.get('season', 1, type=int)
    episodes = get_episodes(series_id, season_number)
    episode_number = request.args.get('episode', episodes[0][1] if episodes else 1, type=int)
    
    # List of server embed URLs
    embed_urls = {
        "Server 1": f"https://vidsrc.pm/embed/tv?tmdb={series_id}&season={season_number}&episode={episode_number}",
        "Server 2": f"https://www.2embed.cc/embedtv/{series_id}&s={season_number}&e={episode_number}",
        "Server 3": f"https://vidsrc.cc/v2/embed/tv/{series_id}/{season_number}/{episode_number}",
        "Server 4": f"https://vidsrc.pro/embed/tv/{series_id}/{season_number}/{episode_number}"
    }
    
    recommendations = get_series_recommendations(series_id)
    
    return render_template('tv_show.html', series=series, seasons=seasons, episodes=episodes, embed_urls=embed_urls, selected_season=season_number, selected_episode=episode_number, recommendations=recommendations, zip=zip)

@app.route('/must_watch')
def must_watch():
    movie_recommendations = get_movie_recommendations()
    series_recommendations = get_tv_show_recommendations()
    
    return render_template('must_watch.html', 
                           movie_recommendations=movie_recommendations, 
                           series_recommendations=series_recommendations)


if __name__ == '__main__':
    app.run(debug=True, host='192.168.42.130')
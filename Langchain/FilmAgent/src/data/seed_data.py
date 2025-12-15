"""Seed the films database with sample data."""

from .films_db import FilmsDatabase


def seed_films_database():
    """Populate the database with sample films."""
    db = FilmsDatabase()
    
    films_data = [
        # Sci-Fi
        {
            "title": "Inception",
            "year": 2010,
            "rating": 8.8,
            "description": "A thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea.",
            "genres": ["Sci-Fi", "Thriller", "Action"],
            "actors": ["Leonardo DiCaprio", "Joseph Gordon-Levitt", "Ellen Page", "Tom Hardy"]
        },
        {
            "title": "The Matrix",
            "year": 1999,
            "rating": 8.7,
            "description": "A computer hacker learns about the true nature of reality and his role in the war against its controllers.",
            "genres": ["Sci-Fi", "Action"],
            "actors": ["Keanu Reeves", "Laurence Fishburne", "Carrie-Anne Moss"]
        },
        {
            "title": "Interstellar",
            "year": 2014,
            "rating": 8.6,
            "description": "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.",
            "genres": ["Sci-Fi", "Drama", "Adventure"],
            "actors": ["Matthew McConaughey", "Anne Hathaway", "Jessica Chastain"]
        },
        {
            "title": "Blade Runner 2049",
            "year": 2017,
            "rating": 8.0,
            "description": "A young blade runner's discovery of a long-buried secret leads him to track down former blade runner Rick Deckard.",
            "genres": ["Sci-Fi", "Thriller"],
            "actors": ["Ryan Gosling", "Harrison Ford", "Ana de Armas"]
        },
        {
            "title": "The Terminator",
            "year": 1984,
            "rating": 8.0,
            "description": "A cyborg assassin is sent back in time to kill Sarah Connor, whose unborn son is destined to lead humanity in a war against machines.",
            "genres": ["Sci-Fi", "Action", "Thriller"],
            "actors": ["Arnold Schwarzenegger", "Linda Hamilton", "Michael Biehn"]
        },
        
        # Action
        {
            "title": "The Dark Knight",
            "year": 2008,
            "rating": 9.0,
            "description": "When the menace known as the Joker wreaks havoc on Gotham, Batman must accept one of the greatest psychological tests.",
            "genres": ["Action", "Crime", "Drama"],
            "actors": ["Christian Bale", "Heath Ledger", "Aaron Eckhart", "Michael Caine"]
        },
        {
            "title": "Mad Max: Fury Road",
            "year": 2015,
            "rating": 8.1,
            "description": "In a post-apocalyptic wasteland, a woman rebels against a tyrannical ruler in search for her homeland.",
            "genres": ["Action", "Adventure", "Sci-Fi"],
            "actors": ["Tom Hardy", "Charlize Theron", "Nicholas Hoult"]
        },
        {
            "title": "John Wick",
            "year": 2014,
            "rating": 7.4,
            "description": "An ex-hitman comes out of retirement to track down the gangsters that killed his dog.",
            "genres": ["Action", "Thriller"],
            "actors": ["Keanu Reeves", "Michael Nyqvist", "Alfie Allen"]
        },
        {
            "title": "Die Hard",
            "year": 1988,
            "rating": 8.2,
            "description": "An NYPD officer tries to save his wife and others taken hostage by German terrorists during a Christmas party.",
            "genres": ["Action", "Thriller"],
            "actors": ["Bruce Willis", "Alan Rickman", "Bonnie Bedelia"]
        },
        
        # Drama
        {
            "title": "The Shawshank Redemption",
            "year": 1994,
            "rating": 9.3,
            "description": "Two imprisoned men bond over years, finding solace and eventual redemption through acts of common decency.",
            "genres": ["Drama"],
            "actors": ["Tim Robbins", "Morgan Freeman", "Bob Gunton"]
        },
        {
            "title": "Forrest Gump",
            "year": 1994,
            "rating": 8.8,
            "description": "The presidencies of Kennedy and Johnson unfold through the perspective of an Alabama man with an IQ of 75.",
            "genres": ["Drama", "Romance"],
            "actors": ["Tom Hanks", "Robin Wright", "Gary Sinise"]
        },
        {
            "title": "The Green Mile",
            "year": 1999,
            "rating": 8.6,
            "description": "The lives of guards on Death Row are affected by one of their charges: a black man accused of child murder.",
            "genres": ["Drama", "Fantasy"],
            "actors": ["Tom Hanks", "Michael Clarke Duncan", "David Morse"]
        },
        {
            "title": "Schindler's List",
            "year": 1993,
            "rating": 9.0,
            "description": "In German-occupied Poland, industrialist Oskar Schindler gradually becomes concerned for his Jewish workforce.",
            "genres": ["Drama", "History"],
            "actors": ["Liam Neeson", "Ralph Fiennes", "Ben Kingsley"]
        },
        
        # Thriller
        {
            "title": "The Silence of the Lambs",
            "year": 1991,
            "rating": 8.6,
            "description": "A young FBI cadet must receive the help of an incarcerated cannibal killer to catch another serial killer.",
            "genres": ["Thriller", "Crime", "Drama"],
            "actors": ["Jodie Foster", "Anthony Hopkins", "Lawrence A. Bonney"]
        },
        {
            "title": "Se7en",
            "year": 1995,
            "rating": 8.6,
            "description": "Two detectives hunt a serial killer who uses the seven deadly sins as his motives.",
            "genres": ["Thriller", "Crime", "Drama"],
            "actors": ["Brad Pitt", "Morgan Freeman", "Kevin Spacey"]
        },
        {
            "title": "Shutter Island",
            "year": 2010,
            "rating": 8.2,
            "description": "A U.S. Marshal investigates the disappearance of a murderer who escaped from a hospital for the criminally insane.",
            "genres": ["Thriller", "Mystery"],
            "actors": ["Leonardo DiCaprio", "Mark Ruffalo", "Ben Kingsley"]
        },
        
        # Comedy
        {
            "title": "The Grand Budapest Hotel",
            "year": 2014,
            "rating": 8.1,
            "description": "A writer encounters the owner of an aging high-class hotel, who tells him of his early years.",
            "genres": ["Comedy", "Adventure", "Drama"],
            "actors": ["Ralph Fiennes", "F. Murray Abraham", "Mathieu Amalric"]
        },
        {
            "title": "Pulp Fiction",
            "year": 1994,
            "rating": 8.9,
            "description": "The lives of two mob hitmen, a boxer, and a pair of diner bandits intertwine in four tales of violence.",
            "genres": ["Crime", "Drama"],
            "actors": ["John Travolta", "Uma Thurman", "Samuel L. Jackson"]
        },
        {
            "title": "The Big Lebowski",
            "year": 1998,
            "rating": 8.1,
            "description": "Jeff 'The Dude' Lebowski is mistaken for a millionaire and seeks restitution for a ruined rug.",
            "genres": ["Comedy", "Crime"],
            "actors": ["Jeff Bridges", "John Goodman", "Julianne Moore"]
        },
        
        # Horror
        {
            "title": "The Shining",
            "year": 1980,
            "rating": 8.4,
            "description": "A family heads to an isolated hotel for the winter where a sinister presence influences the father.",
            "genres": ["Horror", "Drama"],
            "actors": ["Jack Nicholson", "Shelley Duvall", "Danny Lloyd"]
        },
        {
            "title": "Get Out",
            "year": 2017,
            "rating": 7.7,
            "description": "A young African-American visits his white girlfriend's parents for the weekend.",
            "genres": ["Horror", "Mystery", "Thriller"],
            "actors": ["Daniel Kaluuya", "Allison Williams", "Bradley Whitford"]
        },
        
        # Romance
        {
            "title": "Titanic",
            "year": 1997,
            "rating": 7.9,
            "description": "A seventeen-year-old aristocrat falls in love with a kind but poor artist aboard the luxurious, ill-fated R.M.S. Titanic.",
            "genres": ["Romance", "Drama"],
            "actors": ["Leonardo DiCaprio", "Kate Winslet", "Billy Zane"]
        },
        {
            "title": "The Notebook",
            "year": 2004,
            "rating": 7.8,
            "description": "A poor yet passionate young man falls in love with a rich young woman.",
            "genres": ["Romance", "Drama"],
            "actors": ["Ryan Gosling", "Rachel McAdams", "James Garner"]
        },
        
        # Animation
        {
            "title": "Spirited Away",
            "year": 2001,
            "rating": 8.6,
            "description": "During her family's move to the suburbs, a sullen 10-year-old girl wanders into a world ruled by gods.",
            "genres": ["Animation", "Adventure", "Fantasy"],
            "actors": ["Daveigh Chase", "Suzanne Pleshette", "Miyu Irino"]
        },
        {
            "title": "WALL-E",
            "year": 2008,
            "rating": 8.4,
            "description": "In the distant future, a small waste-collecting robot inadvertently embarks on a space journey.",
            "genres": ["Animation", "Adventure", "Sci-Fi"],
            "actors": ["Ben Burtt", "Elissa Knight", "Jeff Garlin"]
        },
        {
            "title": "Toy Story",
            "year": 1995,
            "rating": 8.3,
            "description": "A cowboy doll is profoundly threatened when a new spaceman figure supplants him as top toy.",
            "genres": ["Animation", "Adventure", "Comedy"],
            "actors": ["Tom Hanks", "Tim Allen", "Don Rickles"]
        },
        
        # More classics
        {
            "title": "The Godfather",
            "year": 1972,
            "rating": 9.2,
            "description": "The aging patriarch of an organized crime dynasty transfers control to his reluctant son.",
            "genres": ["Crime", "Drama"],
            "actors": ["Marlon Brando", "Al Pacino", "James Caan"]
        },
        {
            "title": "Goodfellas",
            "year": 1990,
            "rating": 8.7,
            "description": "The story of Henry Hill and his life in the mob, covering his relationship with his wife and his partners.",
            "genres": ["Crime", "Drama"],
            "actors": ["Robert De Niro", "Ray Liotta", "Joe Pesci"]
        },
        {
            "title": "Fight Club",
            "year": 1999,
            "rating": 8.8,
            "description": "An insomniac office worker and a devil-may-care soapmaker form an underground fight club.",
            "genres": ["Drama"],
            "actors": ["Brad Pitt", "Edward Norton", "Helena Bonham Carter"]
        },
        {
            "title": "Gladiator",
            "year": 2000,
            "rating": 8.5,
            "description": "A former Roman General sets out to exact vengeance against the corrupt emperor who murdered his family.",
            "genres": ["Action", "Adventure", "Drama"],
            "actors": ["Russell Crowe", "Joaquin Phoenix", "Connie Nielsen"]
        },
        {
            "title": "Saving Private Ryan",
            "year": 1998,
            "rating": 8.6,
            "description": "Following the Normandy Landings, a group of U.S. soldiers go behind enemy lines to retrieve a paratrooper.",
            "genres": ["Drama", "War"],
            "actors": ["Tom Hanks", "Matt Damon", "Tom Sizemore"]
        },
        {
            "title": "Catch Me If You Can",
            "year": 2002,
            "rating": 8.1,
            "description": "A seasoned FBI agent pursues Frank Abagnale Jr., who successfully performed cons worth millions.",
            "genres": ["Biography", "Crime", "Drama"],
            "actors": ["Leonardo DiCaprio", "Tom Hanks", "Christopher Walken"]
        },
        {
            "title": "The Departed",
            "year": 2006,
            "rating": 8.5,
            "description": "An undercover cop and a mole in the police attempt to identify each other while infiltrating an Irish gang.",
            "genres": ["Crime", "Drama", "Thriller"],
            "actors": ["Leonardo DiCaprio", "Matt Damon", "Jack Nicholson"]
        },
    ]
    
    print("Seeding films database...")
    for film in films_data:
        try:
            db.add_film(
                title=film["title"],
                year=film["year"],
                rating=film["rating"],
                description=film["description"],
                genres=film["genres"],
                actors=film["actors"]
            )
            print(f"  ✓ Added: {film['title']} ({film['year']})")
        except Exception as e:
            print(f"  ✗ Error adding {film['title']}: {e}")
    
    print(f"\nDatabase seeded successfully!")
    print(f"Total genres: {len(db.get_all_genres())}")
    print(f"Available genres: {', '.join(db.get_all_genres())}")


if __name__ == "__main__":
    seed_films_database()

import sqlite3


def initialize_database(db_path):
    # Connect to the database (or create it if it doesn't exist)
    conn = sqlite3.connect(db_path)

    # Create a cursor object
    cursor = conn.cursor()

    try:
        # Create the users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            hash TEXT NOT NULL
        )
        ''')

        # Create the images table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            filename TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS loves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            image_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (image_id) REFERENCES images (id)
        );
        ''')

        # # Insert dummy data into the users table
        # cursor.execute('''
        # INSERT INTO users (username, hash) VALUES
        # ('user1', 'hash1'),
        # ('user2', 'hash2'),
        # ('user3', 'hash3')
        # ''')

        # # Insert dummy data into the images table
        # cursor.execute('''
        # INSERT INTO images (name, description, filename, user_id) VALUES
        # ('Image1', 'Description1', 'image1.jpg', 1),
        # ('Image2', 'Description2', 'image2.jpg', 2),
        # ('Image3', 'Description3', 'image3.jpg', 3)
        # ''')
        # Commit the transaction
        conn.commit()

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the connection
        conn.close()


def clear_database(db_path):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Retrieve the list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        # Delete all records from each table
        for table in tables:
            table_name = table[0]
            cursor.execute(f"DELETE FROM {table_name};")
            print(f"Cleared all records from table {table_name}")

        # Commit the changes
        conn.commit()

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the connection
        conn.close()


db_path = 'gallery.db'
initialize_database(db_path)
# clear_database(db_path)

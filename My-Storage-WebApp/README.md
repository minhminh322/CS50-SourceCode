# Gallery App

This is a web application that allows users to upload and display images in a gallery. It is built using Flask and SQLite.

## Features

- User registration and login
- Upload images with metadata (name and description)
- Display a gallery of uploaded images for each user

## Installation

1. **Clone the repository**

2. **Set up a virtual environment:**

   ```sh
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**

   ```sh
   pip install -r requirements.txt
   ```

4. **Configure the CS50 Library:**

   Make sure you have the CS50 library installed. If not, install it using:

   ```sh
   pip install cs50
   ```

## Database Setup

1. **Setup database:**
   Run this command to create the database and tables:
   ```sh
   python3 setup_db.py
   ```

## Configuration

1. **Ensure the upload folder exists:**

   ```sh
   mkdir -p static/uploads
   ```

2. **Run the application:**

   ```sh
   flask run
   ```

   The application will be available at `http://127.0.0.1:5000`.

## Usage

1. **Register a new user:**

   Visit `http://127.0.0.1:5000/register` and fill in the registration form.

2. **Login:**

   Visit `http://127.0.0.1:5000/login` and log in with your credentials.

3. **Upload an image:**

   After logging in, you can upload an image with a name and description from the home page.

4. **View gallery:**

   After uploading images, they will be displayed on the home page.

## Helpers

- `apology`: Function to render apology messages
- `login_required`: Decorator to ensure routes are accessed by logged-in users only

## Database Design

- **users**: Stores user information.

  - `id`: Primary key.
  - `username`: Username of the user.
  - `hash`: Password hash.

- **images**: Stores information about uploaded images.
  - `id`: Primary key.
  - `name`: Name of the image.
  - `description`: Description of the image.
  - `filename`: Filename of the uploaded image.
  - `created_at`: Timestamp when the image was uploaded.
  - `user_id`: Foreign key referencing the `users` table.

## Security

- Passwords are hashed using Werkzeug's security module.
- Session management with Flask's built-in session handling.

## API Integration (OPTIONAL for Auto-Generated Image Descriptions)

### Obtaining the OPENAI_KEY

To use the OpenAI API, you need to obtain an API key. Follow these steps to get your `OPENAI_KEY`:

1. Go to the [OpenAI website](https://www.openai.com/).
2. Sign up for an account if you don't already have one.
3. Once logged in, navigate to the API section.
4. Create a new API key.
5. Copy the generated API key.

### Setting Up Environment Variables

After obtaining your `OPENAI_KEY`, you need to set it as an environment variable. You can do this by adding the following line to your `.env` file:

```sh
OPENAI_KEY=your_openai_key_here
```

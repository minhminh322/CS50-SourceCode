import os
from datetime import datetime, timezone
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from cs50 import SQL
from helpers import resize_image, apology, login_required
import base64
import requests
import os

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///gallery.db")

# Ensure the upload folder exists
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Configure upload folder and allowed extensions
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
# Set a secret key for session management
app.config['SECRET_KEY'] = 'supersecretkey'


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower(
           ) in app.config['ALLOWED_EXTENSIONS']


# def analyze_image(image_path):
    # return 'This image depicts a colorful variation of the Ethereum logo. The Ethereum logo is generally characterized by a diamond shape or an "eth" symbol, which is a geometric shape consisting of an upright diamond with a line cutting through its middle. In this image, the logo is divided into six segments, each with a different color: yellow, orange, green, purple, blue, and cyan.'
def analyze_image(image_path):
    """Analyze the image using OpenAI API to generate a description."""
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "API key not found. Set the OPENAI_API_KEY environment variable.")

    # Encode image to base64
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4o",
        "messages": [{
            "role": "system",
            "content": "You are ChatGPT, an advanced AI assistant specializing in image recognition. Your role is to provide helpful, accurate, and insightful responses to users’ queries. You aim to be both informative and engaging, ensuring users have a positive experience. You excel at detecting and identifying individuals or locations in images."
        },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Write a brief description of this image. Tell the person name or exact location if possible."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
        }
        ],
        "max_tokens": 300
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    if response.status_code == 200:
        response_data = response.json()
        return response_data['choices'][0]['message']['content']
    else:
        raise Exception(
            f"OpenAI API request failed with status code {response.status_code}: {response.text}")


@app.route("/auto-generate-description", methods=["POST"])
@login_required
def auto_generate_description():
    # Handle image upload for auto-generating description
    if 'image' not in request.files:
        return jsonify({"success": False, "error": "No file part"})
    file = request.files['image']
    if file.filename == '':
        return jsonify({"success": False, "error": "No selected file"})
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Generate description using OpenAI
        try:
            description = analyze_image(filepath)
            return jsonify({"success": True, "description": description})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})
    return jsonify({"success": False, "error": "Invalid file type"})


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET"])
@login_required
def index():
    user_id = session.get("user_id")
    # Display the images in the gallery
    images = db.execute(
        """
        SELECT images.id AS id, images.*, 
            CASE WHEN loves.user_id IS NOT NULL THEN 1 ELSE 0 END AS loved
        FROM images
        LEFT JOIN loves ON images.id = loves.image_id
        WHERE images.user_id = ?
        ORDER BY images.created_at DESC
        """, user_id)

    # Calculate the time difference for each image
    for image in images:
        # Convert to same timezone
        created_at = datetime.strptime(
            image['created_at'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        time_diff = now - created_at
        if time_diff.days > 0:
            image['time_ago'] = f"{time_diff.days} days ago"
        elif time_diff.seconds // 3600 > 0:
            image['time_ago'] = f"{time_diff.seconds // 3600} hours ago"
        elif time_diff.seconds // 60 > 0:
            image['time_ago'] = f"{time_diff.seconds // 60} minutes ago"
        else:
            image['time_ago'] = "just now"

    return render_template("index.html", images=images)


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    user_id = session.get("user_id")

    if request.method == "GET":
        return render_template("upload.html")

    if request.method == "POST":
        # Handle image upload
        if 'image' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['image']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            resize_image(file)

            # Save image metadata to the database
            name = request.form.get('name')
            description = request.form.get('description', '')

            db.execute("INSERT INTO images (name, description, filename, user_id) VALUES (?, ?, ?, ?)",
                       name, description, filename, user_id)
            return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":
        # Get form data
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Validate form data
        if not username:
            return apology("User cant be blanked")

        if not password or not confirmation:
            return apology("Password/confirmation can't be blanked")

        if password != confirmation:
            return apology("Passwords don't match")

        # Check if username already exists
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if rows:
            flash('Username already exists')
            return redirect('/register')

        # Hash password and insert new user into database
        hash = generate_password_hash(password)
        db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)

        # Redirect to login page
        return redirect('/login')


@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user_id
    session.clear()
    if request.method == "GET":
        return render_template('login.html')
    if request.method == "POST":
        # Get form data
        username = request.form.get("username")
        password = request.form.get("password")

        # Validate form data
        if not username:
            return apology("must provide username", 403)

        if not password:
            flash('Must provide password')
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]['hash'], password):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect to home page
        return redirect("/")


@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()

    # Redirect to login form
    return redirect("/login")


@app.route('/love', methods=['POST'])
def love():
    if not session.get('user_id'):
        return jsonify({'success': False, 'error': 'User not logged in'})

    user_id = session['user_id']
    data = request.get_json()
    image_id = int(data.get('image_id'))

    # Check if the user already loved the image
    love = db.execute(
        'SELECT * FROM loves WHERE user_id = ? AND image_id = ?', user_id, image_id)

    if len(love) > 0:
        # Unlove the image
        db.execute(
            'DELETE FROM loves WHERE user_id = ? AND image_id = ?', user_id, image_id)
        loved = False
    else:
        # Love the image
        db.execute(
            'INSERT INTO loves (user_id, image_id) VALUES (?, ?)', user_id, image_id)
        loved = True

    return jsonify({'success': True, 'loved': loved})

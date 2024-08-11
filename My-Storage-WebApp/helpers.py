from flask import redirect, render_template, session
from functools import wraps
from PIL import Image
import os


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def resize_image(file, output_size=(1920, 1080)):
    """
    Resize the given image to the specified output size.

    :param file: The image file to resize.
    :param output_size: A tuple specifying the desired output size (width, height).
    :return: The resized image file path.
    """
    filename = file.filename
    filepath = os.path.join('static/uploads', filename)

    image = Image.open(file)
    image = image.resize(output_size)
    image.save(filepath)

    return filepath

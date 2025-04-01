from flask import Flask
from config import Config
from models import init_db

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
init_db(app)

# Import routes after app creation to avoid circular imports
from routes import *

if __name__ == '__main__':
    app.run(debug=True)
"""creating sql alchemy extension that can be imported all over our app as needed
    initialize sqlalchemy so it can setup everything
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
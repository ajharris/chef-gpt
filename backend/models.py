from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

from datetime import datetime, timedelta

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    inventory = db.relationship('Inventory', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    fiber_content = db.Column(db.Float, nullable=True)  # in grams
    sugar_content = db.Column(db.Float, nullable=True)  # in grams
    nutrition_score = db.Column(db.Float, nullable=True)  # overall nutrition score
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    user = db.relationship('User', backref=db.backref('recipes', lazy=True))
    ratings = db.relationship('Rating', backref='recipe', lazy=True)

    def __repr__(self):
        return f'<Recipe {self.title}>'

    def average_rating(self):
        if not self.ratings:
            return None
        return sum(rating.score for rating in self.ratings) / len(self.ratings)

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)

    def __repr__(self):
        return f'<Rating {self.score} for Recipe ID {self.recipe_id}>'

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ingredient = db.Column(db.String(128), nullable=False)
    quantity = db.Column(db.Float, nullable=True)  # This can be extended to handle inventory management
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Inventory {self.ingredient}>'
    
class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    last_cleaned_stove = db.Column(db.DateTime, default=datetime.utcnow)
    last_cleaned_fridge = db.Column(db.DateTime, default=datetime.utcnow)
    next_reminder_stove = db.Column(db.DateTime)
    next_reminder_fridge = db.Column(db.DateTime)
    user = db.relationship('User', backref=db.backref('reminders', lazy=True))

    def __init__(self, user_id):
        self.user_id = user_id
        self.next_reminder_stove = self.last_cleaned_stove + timedelta(days=30)  # Example: Remind every 30 days
        self.next_reminder_fridge = self.last_cleaned_fridge + timedelta(days=30)

    def update_reminder_stove(self):
        self.last_cleaned_stove = datetime.utcnow()
        self.next_reminder_stove = self.last_cleaned_stove + timedelta(days=30)
        db.session.commit()

    def update_reminder_fridge(self):
        self.last_cleaned_fridge = datetime.utcnow()
        self.next_reminder_fridge = self.last_cleaned_fridge + timedelta(days=30)
        db.session.commit()

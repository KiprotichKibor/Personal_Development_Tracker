from datetime import datetime
from sqlalchemy import Enum
from enum import Enum as pyEnum
from waweza import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    goals = db.relationship('Goal', backref='user', lazy=True)
    habits = db.relationship('Habit', backref='user', lazy=True)
    moods = db.relationship('Mood', backref='user', lazy=True)
    analytics = db.relationship('Analytics', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"
    
class GoalType(pyEnum):
    DAILY = 'daily'
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'

class StatusType(pyEnum):
    NOTSTARTED = 'not started'
    STARTED = 'in progress'
    COMPLETED = 'completed'
    
class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    type = db.Column(Enum(GoalType), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(Enum(StatusType), nullable=False)
    habits = db.relationship('Habit', backref='goal', lazy=True)

    def __repr__(self):
        return f"Goal('{self.title}')"

class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.id'), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Habit('{self.name}')"
    
class MoodType(pyEnum):
    HAPPY = 'happy'
    FRUSTRATED = 'frustrated'
    NEUTRAL = 'neutral'

class Mood(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mood = db.Column(Enum(MoodType), nullable=False)
    logged_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Mood('{self.mood}', '{self.logged_at}')"
    
class Analytics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    week_start_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    week_end_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    goals_progress = db.Column(db.Float, nullable=False)
    habits_completion = db.Column(db.Float, nullable=False)
    mood_distribution = db.Column(db.JSON, nullable=False)

    def __repr__(self):
        return f"Analytics('{self.week_start_date}', '{self.week_end_date}', '{self.goals_progress}', '{self.habits_completion}', '{self.mood_distribution}')"
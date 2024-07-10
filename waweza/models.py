from datetime import datetime, timedelta
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from sqlalchemy import Enum
from enum import Enum as pyEnum
from waweza import db, login_manager, app
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
    verified = db.Column(db.Boolean, default=False)

    def get_verification_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"
    
class GoalType(pyEnum):
    SHORT_TERM = 'short term'
    LONG_TERM = 'long term'

class StatusType(pyEnum):
    NOTSTARTED = 'not started'
    STARTED = 'in progress'
    COMPLETED = 'completed'

    def __str__(self):
        return self.value
    
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
    habits = db.relationship('Habit', backref='goal', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f"Goal('{self.title}')"

class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.id'), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    logs = db.relationship('HabitLog', backref='habit', lazy=True, cascade='all, delete-orphan')

    @property
    def is_completed(self):
        today = datetime.utcnow().date()
        log = HabitLog.query.filter_by(habit_id=self.id, date=today).first()
        return log.completed if log else False

    def __repr__(self):
        return f"Habit('{self.name}')"
    
class HabitLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey('habit.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    notes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"HabitLog('{self.name}', '{self.date}', '{self.completed}')"
    
class MoodType(pyEnum):
    HAPPY = 'happy'
    FRUSTRATED = 'frustrated'
    NEUTRAL = 'neutral'
    SAD = 'sad'
    ANXIOUS = 'anxious'

class Mood(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mood_type = db.Column(Enum(MoodType), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Mood('{self.mood_type.value}', '{self.date}')"
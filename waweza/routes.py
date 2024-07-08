from flask import Blueprint, render_template, abort, url_for, flash, redirect, jsonify, request
from waweza import app, db, bcrypt
from waweza.forms import RegistrationForm, LoginForm, GoalForm, HabitForm, HabitLogForm, MoodForm, HabitStatusForm
from waweza.models import User, GoalType, StatusType, Goal, Habit, HabitLog, MoodType, Mood
from waweza.helpers import get_analytics_data
from flask_login import login_user, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from flask import session, current_app
from datetime import datetime
from collections import Counter


goal_bp = Blueprint('goal', __name__)
habit_bp = Blueprint('habit', __name__)
mood_bp = Blueprint('mood', __name__)
analytics_bp = Blueprint('analytics', __name__)


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are are now able to login', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@goal_bp.route("/goals", methods=['GET', 'POST'])
@login_required
def goals():
    form = GoalForm()
    if form.validate_on_submit():
        print("Form Validated Successfully!")
        new_goal = Goal(
            title = form.title.data,
            description = form.description.data,
            type = GoalType(form.type.data),
            start_date = form.start_date.data,
            end_date = form.end_date.data,
            status = StatusType(form.status.data),
            user_id = current_user.id
        )
        db.session.add(new_goal)
        db.session.commit()
        flash('Goal created successfully!', 'success')
        return redirect(url_for('goal.goals'))
    
    else:
        print("Form validation failed")
        print(form.errors)
    
    goals = Goal.query.all()
    return render_template('goals.html', form=form, goals=goals)
    
@goal_bp.route("/goal/<int:goal_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    if goal.user_id != current_user.id:
        abort(403)
    form = GoalForm(obj=goal)
    if form.validate_on_submit():
        print("Form validation successful!")
        goal.title = form.title.data
        goal.description = form.description.data
        goal.type = GoalType(form.type.data)
        goal.start_date = form.start_date.data
        goal.end_date = form.end_date.data
        goal.status = StatusType(form.status.data)
        db.session.commit()
        flash('Goal updated successfully', 'success')
        return redirect(url_for('goal.goals'))
    
    else:
        print("Form validation failed")
        print(form.errors)

    return render_template('edit_goal.html', form=form, goal=goal)

@goal_bp.route("/goal/<int:goal_id>/delete", methods=['POST'])
@login_required
def delete_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    if goal.user_id != current_user.id:
        abort(403)
    try:
        db.session.delete(goal)
        db.session.commit()
        flash('Goal deleted successfully', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('An error occured while deleting the goal', 'error')
    return redirect(url_for('goal.goals'))

@habit_bp.route("/habits", methods=['GET', 'POST'])
@login_required
def habits():
    form = HabitForm()
    form.goal.choices = [(goal.id, goal.title) for goal in Goal.query.all()]

    if form.validate_on_submit():
        print("Form validation was successful")
        new_habit = Habit(
            name=form.name.data,
            goal_id=form.goal.data,
            user_id=current_user.id)
        db.session.add(new_habit)
        db.session.commit()
        flash('Habit created successfully', 'success')
        return redirect(url_for('habit.habits'))
    
    else:
        print("Form validation failed")
        print(form.errors)
    
    habits = Habit.query.all()
    return render_template('habits.html', form=form, habits=habits)

@habit_bp.route("/habit/<int:habit_id>/log", methods=['GET', 'POST'])
@login_required
def log_habit(habit_id):
    form = HabitLogForm()
    habit = Habit.query.get_or_404(habit_id)
    if habit.user_id != current_user.id:
        abort(403)

    if form.validate_on_submit():
        print("Form validated sucessfully!")
        new_log = HabitLog(
            habit_id=habit_id,
            date=form.date.data,
            completed=form.completed.data,
            notes=form.notes.data)
        try:
            db.session.add(new_log)
            db.session.commit()
            flash('Habit log updated successfully', 'sucess')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occured: {str(e)}', 'error')
            
        return redirect(url_for('habit.habits'))
    
    else:
        print("Form validation failed")
        print(form.errors)
    
    logs = HabitLog.query.filter_by(habit_id=habit_id).order_by(HabitLog.date.desc()).all()
    return render_template('log_habit.html', form=form, habit=habit, logs=logs)

@habit_bp.route("/habit/<int:habit_id>/history")
@login_required
def habits_history(habit_id):
    habit = Habit.query.get_or_404(habit_id)
    if habit.user_id != current_user.id:
        abort(403)
    habit_history = HabitLog.query.filter_by(habit_id=habit_id).order_by(HabitLog.date.desc()).all()
    return render_template('habits_history.html', habit=habit, habit_history=habit_history)

@habit_bp.route("/habit/<int:habit_id>/delete", methods=['POST'])
@login_required
def delete_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)
    if habit.user_id != current_user.id:
        abort(403)
    try:
        db.session.delete(habit)
        db.session.commit()
        flash('Habit deleted successfully', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('An error occured while deleting habit!', 'error')

        current_app.logger.error(f'Error deleting habit: {str(e)}')
    return redirect(url_for('habit.habits'))

@habit_bp.route("/habit/<int:habit_id>/update", methods=['POST'])
@login_required
def update_status(habit_id):
    habit = Habit.query.get_or_404(habit_id)
    if habit.user_id != current_user.id:
        abort(403)
    form = HabitStatusForm()
    if form.validate_on_submit():
        new_log = HabitLog(
            habit_id=habit_id,
            date=datetime.utcnow().date(),
            completed=form.status.data == 'completed',
            notes=form.notes.data
        )
        db.session.add(new_log)
        db.session.commit()
        flash('Habit status updated successfully!', 'success')
    return redirect(url_for('habit.habits'))

@mood_bp.route('/moods', methods=['GET', 'POST'])
@login_required
def moods():
    form = MoodForm()
    if form.validate_on_submit():
        new_mood = Mood(
            date=form.date.data,
            mood_type=MoodType[form.mood_type.data],
            notes=form.notes.data,
            user_id=current_user.id
        )
        try:
            db.session.add(new_mood)
            db.session.commit()
            flash('Mood logged successfully!', 'success')
        except IntegrityError:
            db.session.rollback()
            flash('Error: Mood for this date already exists.', 'error')
        return redirect(url_for('mood.moods'))
    
    moods = Mood.query.order_by(Mood.date.desc()).all()
    
    # Prepare data for the mood chart
    dates = [mood.date.strftime('%Y-%m-%d') for mood in moods]
    mood_values = [list(MoodType).index(mood.mood_type) + 1 for mood in moods]
    
    return render_template('moods.html', form=form, moods=moods, dates=dates, mood_values=mood_values)

@mood_bp.route('/moods/<int:mood_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_mood(mood_id):
    mood = Mood.query.get_or_404(mood_id)
    if mood.user_id != current_user.id:
        abort(403)
    form = MoodForm(obj=mood)
    if form.validate_on_submit():
        mood.date = form.date.data
        mood.mood_type = MoodType[form.mood_type.data]
        mood.notes = form.notes.data
        db.session.commit()
        flash('Mood updated successfully!', 'success')
        return redirect(url_for('mood.moods'))
    return render_template('edit_mood.html', form=form, mood=mood)

@mood_bp.route('/moods/<int:mood_id>/delete', methods=['POST'])
@login_required
def delete_mood(mood_id):
    mood = Mood.query.get_or_404(mood_id)
    if mood.user_id != current_user.id:
        abort(403)
    db.session.delete(mood)
    db.session.commit()
    flash('Mood deleted successfully!', 'success')
    return redirect(url_for('mood.moods'))

@mood_bp.route('/moods/chart')
@login_required
def moods_chart(mood_id):
    moods = Mood.query.order_by(Mood.date()).all()

    dates = [mood.date.strftime('%Y-%m-%d') for mood in moods]
    mood_values = [list(MoodType).index(mood.mood_type) + 1 for mood in moods]

    mood_counts = Counter(mood.mood_type.value for mood in moods)
    mood_types = list(mood_counts.keys())
    mood_counts = list(mood_counts.values())

    return render_template('moods_chart.html',
                           dates=dates,
                           mood_values=mood_values,
                           mood_types=mood_types,
                           mood_counts=mood_counts)

@analytics_bp.route("/analytics", methods=['GET', 'POST'])
@login_required
def analytics():
    data = get_analytics_data()
    return render_template('analytics.html', **data)

@analytics_bp.route("/analytics/data")
@login_required
def analytics_data():
    data = get_analytics_data()
    return jsonify(data)
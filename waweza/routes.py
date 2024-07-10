from flask import Blueprint, render_template, abort, url_for, flash, redirect, jsonify, request
from waweza import app, db, bcrypt, mail
from waweza.forms import RegistrationForm, UpdateAccountForm, LoginForm, GoalForm, HabitForm, HabitLogForm, MoodForm, HabitStatusForm, RequestResetForm, ResetPasswordForm, ResendVerificationForm
from waweza.models import User, GoalType, StatusType, Goal, Habit, HabitLog, MoodType, Mood
from waweza.helpers import get_analytics_data, calculate_habit_streak
from flask_login import login_user, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from flask import session, current_app
from datetime import datetime, timedelta
from collections import Counter
from flask_mail import Message
from waweza.utils import save_picture


goal_bp = Blueprint('goal', __name__)
habit_bp = Blueprint('habit', __name__)
mood_bp = Blueprint('mood', __name__)
analytics_bp = Blueprint('analytics', __name__)


def send_verification_email(user):
    token = user.get_verification_token()
    msg = Message('Verify Your Email',
                  sender='noreply@yourdomain.com',
                  recipients=[user.email])
    msg.body = f'''To verify your email, visit the following link:
{url_for('verify_email', token=token, _external=True)}

If you did not make this request then simply ignore this email.
'''
    mail.send(msg)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@yourdomain.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

@app.route("/")
def landing():
    return render_template('landing.html', title='Welcome to Waweza')


@app.route("/home")
@login_required
def home():
    current_date = datetime.utcnow()
    
    # Fetch data for summaries
    goals_count = Goal.query.filter_by(user_id=current_user.id, status='in_progress').count()
    completed_goals_count = Goal.query.filter_by(user_id=current_user.id, status='completed').count()
    habits_count = Habit.query.filter_by(user_id=current_user.id).count()
    habits_completed_today = HabitLog.query.filter(
        HabitLog.habit.has(user_id=current_user.id),
        HabitLog.date == current_date.date(),
        HabitLog.completed == True
    ).count()
    
    # Fetch mood data for the last 7 days
    seven_days_ago = current_date - timedelta(days=7)
    moods = Mood.query.filter(
        Mood.user_id == current_user.id,
        Mood.date >= seven_days_ago
    ).order_by(Mood.date).all()
    
    mood_to_number = {
    'HAPPY': 0,
    'FRUSTRATED': 1,
    'NEUTRAL': 2,
    'SAD': 3,
    'ANXIOUS': 4 
    }

    mood_dates = [mood.date.strftime('%Y-%m-%d') for mood in moods]
    mood_values = [mood_to_number[mood.mood_type.name] for mood in moods]
    mood_average = sum(mood_values) / len(mood_values) if mood_values else 0
    
    # Calculate goal completion rate and habit streak
    total_goals = Goal.query.filter_by(user_id=current_user.id).count()
    goal_completion_rate = (completed_goals_count / total_goals * 100) if total_goals > 0 else 0
    
    habit_streak = calculate_habit_streak(current_user.id)
    
    return render_template('home.html',
                           current_date=current_date,
                           goals_count=goals_count,
                           completed_goals_count=completed_goals_count,
                           habits_count=habits_count,
                           habits_completed_today=habits_completed_today,
                           mood_dates=mood_dates,
                           mood_values=mood_values,
                           mood_average=round(mood_average, 1),
                           goal_completion_rate=round(goal_completion_rate, 1),
                           habit_streak=habit_streak)

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
        user.verified = False
        db.session.add(user)
        db.session.commit()
        send_verification_email(user)
        flash('Your account has been created! Please check your email to verify your account.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/verify_email/<token>")
def verify_email(token):
    user = User.verify_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('login'))
    user.verified = True
    db.session.commit()
    flash('Your email has been verified! You can now login.', 'success')
    return redirect(url_for('login'))

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            if user.verified:
                login_user(user, remember=form.remember.data)
                return redirect(url_for('home'))
            else:
                flash('Please verify your email before logging in.', 'warning')
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('landing'))

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

@app.route("/resend_verification", methods=['GET', 'POST'])
def resend_verification():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = ResendVerificationForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and not user.verified:
            send_verification_email(user)
            flash('A new verification email has been sent.', 'info')
        else:
            flash('Invalid email or account already verified.', 'warning')
        return redirect(url_for('login'))
    return render_template('resend_verification.html', title='Resend Verification Email', form=form)

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)

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
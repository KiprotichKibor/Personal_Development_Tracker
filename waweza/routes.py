from flask import Blueprint, render_template, url_for, flash, redirect
from waweza import app, db, bcrypt
from waweza.forms import RegistrationForm, LoginForm, GoalForm
from waweza.models import User, GoalType, StatusType, Goal, Habit, MoodType, Mood, Analytics
from flask_login import login_user, current_user, logout_user


goal_bp = Blueprint('goal', __name__)

goalies = [
    {
        'user': 'kibor',
        'title': 'project completion',
        'context': 'portfolio project',
        'date_started': 'June 2, 2024',
        'date_ending': 'June 29, 2024'
    },
    {
        'user': 'kibor',
        'title': 'procastination',
        'context': 'use pomodoro technique',
        'date_started': 'June 2, 2024',
        'date_ending': 'June 29, 2024'
    }
]

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', goalies=goalies)

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
def goals():
    form = GoalForm()
    if form.validate_on_submit():
        new_goal = Goal(
            title = form.title.data,
            description = form.description.data,
            type = GoalType(form.type.data),
            start_date = form.start_date.data,
            end_date = form.end_date.data
        )
        db.session.add(new_goal)
        db.session.commit()
        flash('Goal created successfully!', 'success')
        return redirect(url_for('goal.goals'))
    
    goals = Goal.query.all()
    return render_template('goals.html', form=form, goals=goals)
    
@goal_bp.route("/goal/edit/<int:id>", methods=['GET', 'POST'])
def edit_goal():
    goal = Goal.query.get_or_404(id)
    form = GoalForm(obj=goal)
    if form.validate_on_submit():
        goal.title = form.title.data
        goal.description = form.description.data
        goal.type = GoalType(form.type.data)
        goal.start_date = form.start_date.data
        goal.end_date = form.end_date.data
        db.session.commit()
        flash('Goal updated successfully', 'success')
        return redirect(url_for('goal.goals'))
    return render_template('edit_goal.html', form=form)

@goal_bp.route("/goal/delete/<int:id>", methods=['GET', 'POST'])
def delete_goal():
    goal = Goal.query.get_or_404(id)
    db.session.delete(goal)
    db.session.commit()
    flash('Goal deleted successfully', 'success')
    return redirect(url_for('goal.goals'))
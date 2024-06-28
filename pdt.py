#!/usr/bin/python3

from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm

app = Flask(__name__)

app.config['SECRET_KEY'] = '6f4f3a256f17c57dba634184da6f3181'

goals = [
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
    return render_template('home.html', goals=goals)

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'ktk@trial.com' and form.password.data == 'password':
            flash(f'You have been logged in', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

if __name__ == '__main__':
    app.run(debug=True)
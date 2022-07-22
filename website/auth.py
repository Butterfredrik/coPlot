from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import base64
from covid19dh import covid19
from io import BytesIO
from matplotlib.figure import Figure

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category="success")
                login_user(user, remember=True)
                return redirect(url_for('view.home'))
            else:
                flash('Incorrect password, try again', category="error")
        else:
            flash('Email does not exist', category="error")

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()

        if user:
            flash('Email already exists', category='error')

        elif len(email) < 4:
            flash('Email must be greater than 4 characters', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character', category='error')
        elif password1 != password2:
            flash('Passwords do not match', category='error')
        elif len(password1) < 7:
            flash('Passwords must be greater than 7 characters', category='error')
        else:
            new_user = User(email=email, first_name=first_name,
                            password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(user, remember=True)
            flash('Account created!', category='Success')
            return redirect(url_for('view.home'))

    return render_template("sign_up.html", user=current_user)


@auth.route('/work', methods=['GET', 'POST'])
def plot_work():
    if request.method == 'POST':
        country = request.form.get('country')
        parameter = request.form.get('parameter')
        data, src = covid19(country)

        if data is not None:
            x = data.date

            if parameter == "deaths":
                y = data.deaths
            elif parameter == "confirmed":
                y = data.confirmed
            elif parameter == "people vaccinated":
                y = data.people_vaccinated
            elif parameter == "icu":
                y = data.icu
            else:
                y = data.recovered

            fig = Figure()
            ax = fig.subplots()
            ax.plot(x, y)
            # Save it to a temporary buffer.
            buf = BytesIO()
            fig.savefig(buf, format="png")
            # Embed the result in the html output.
            view = base64.b64encode(buf.getbuffer()).decode("ascii")
            return f"<div><table width='100%' height='100%' align='center' valign='center'><center><img src='data:image/png;base64,{view}' alt = 'foo' /></center></div>"


        else:
            flash("Invalid country id", category="error")
    return render_template("work.html", user=current_user)


@auth.route('who_am_I', methods=['GET', 'POST'])
def who_am_I():
    return render_template('who_am_I.html', user=current_user)

from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user

import base64
from covid19dh import covid19
from matplotlib.figure import Figure
from io import BytesIO


view = Blueprint('view', __name__)


@view.route('/', methods=['GET', 'POST'])
@login_required
def home():
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

            if y.isnull().all():
                flash("Data is not available", category="error")
                return render_template("work.html", user=current_user)
            print(y.isnull().all(), y)

            fig = Figure()
            ax = fig.subplots()
            ax.plot(x, y)

            # Save it to a temporary buffer.
            buf = BytesIO()
            fig.savefig(buf, format="png")
            # Embed the result in the html output.
            figure = base64.b64encode(buf.getbuffer()).decode("ascii")
            return f"<div><table width='100%' height='100%' align='center' valign='center'><center><img src='data:image/png;base64,{figure}' alt = 'foo' /></center></div>"


        else:
            flash("Invalid country id", category="error")
    return render_template("work.html", user=current_user)





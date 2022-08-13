from flask import Blueprint, render_template, request, flash
import base64
from covid19dh import covid19
from io import BytesIO
from matplotlib.figure import Figure

view = Blueprint('view', __name__)


@view.route('/home', methods=['GET', 'POST'])
@view.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        country = request.form.get('country')
        parameter = request.form.get('parameter')
        data, src = covid19(country)
        data2, src = covid19('USA')

        if data is not None:
            x = data.date
            x2 = data2.date

            if parameter == "deaths":
                y = data.deaths
                y2 = data2.deaths

            elif parameter == "confirmed cases":
                y = data.confirmed
                y2 = data2.confirmed
            elif parameter == "people vaccinated":
                y = data.people_vaccinated
                y2 = data2.people_vaccinated
            elif parameter == "icu":
                y = data.icu
                y2 = data2.icu

            else:
                y = data.tests
                y2 = data2.tests

            if y.isnull().all():
                flash("Data is not available", category="error")
                return render_template("work.html")

            fig = Figure(figsize=(19, 9))
            ax1 = fig.subplots()
            ax2 = ax1.twinx()
            ax1.grid(linestyle='-', linewidth=1)

            ax1.plot(x, y, 'r-', label=country)

            ax2.plot(x2, y2, 'b-', label='USA')

            ax1.set_title(parameter.upper() + ' COVID-19', fontsize=30, color='black', fontweight='bold')

            ax1.legend(prop={'size': 20})
            ax2.legend(prop={'size': 20}, loc='lower right')
            # Save it to a temporary buffer.
            buf = BytesIO()
            fig.savefig(buf, format="png")
            # Embed the result in the html output.
            plot = base64.b64encode(buf.getbuffer()).decode("ascii")
            return f"<body style='background-color:white;'><div><table width='100%' height='100%' align='center' valign='center'><center><img src='data:image/png;base64,{plot}' alt = 'foo' /></center></div></body>"

        else:
            flash("Invalid country id", category="error")
    return render_template("work.html")


@view.route('who_am_I', methods=['GET', 'POST'])
def who_am_I():
    return render_template('who_am_I.html')

# import libraries
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
import requests

from forms.input_form import PortfolioAgg
from main import agg_contracts

# create app
app = Flask(__name__)
bootstrap = Bootstrap(app)

app.config['SECRET_KEY'] = 'testkey'

# main page
@app.route('/portfolio', methods=['POST', 'GET'])
def portfolio():

    form = PortfolioAgg()

    contracts = []

    if form.validate_on_submit():

        aggregation_level = request.form.get('aggregation_level')
        reporting_date = request.form.get('reporting_date')

        print(reporting_date)

        output = agg_contracts(reporting_date='28/06/2019', aggregation_level=aggregation_level)

        import pandas as pd
        contracts = pd.DataFrame(output['contracts']).to_html()
        value = pd.DataFrame(output['value']).to_html()

        daily = pd.DataFrame(output['daily']).to_html()
        month = pd.DataFrame(output['month']).to_html()
        year = pd.DataFrame(output['year']).to_html()





    return render_template('portfolio.html', title='Home Page', form=form,
                           contracts=contracts,
                           value=value,
                           daily=daily,
                           month=month,
                           year=year)


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)

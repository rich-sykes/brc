# import libraries
from flask import Flask, render_template, request, redirect
from flask_bootstrap import Bootstrap
import requests
import pandas as pd

from forms.input_form import PortfolioAgg
from main import agg_contracts

# create app
app = Flask(__name__)
bootstrap = Bootstrap(app)

app.config['SECRET_KEY'] = 'testkey'


# main page
@app.route('/', methods=['POST', 'GET'])
def index():

    form = PortfolioAgg()

    contracts_df = pd.DataFrame()
    value_df = pd.DataFrame()
    daily_df = pd.DataFrame()
    month_df = pd.DataFrame()
    year_df = pd.DataFrame()

    if form.validate_on_submit():

        aggregation_level = request.form.get('aggregation_level')
        reporting_date = request.form.get('reporting_date')


        output = agg_contracts(reporting_date=reporting_date, aggregation_level=aggregation_level)

        # comtracts
        contracts_df = pd.DataFrame(
            output['contracts'], columns=["Contracts"]).to_html(table_id="contracts",
                                         classes=["table table-striped table-bordered table-hover"],
                                         index=False)

        value_df = pd.DataFrame(output['value']).reset_index().to_html(table_id="value",
                                         classes=["table table-striped table-bordered table-hover"],
                                         index=False)

        daily_df = pd.DataFrame(output['daily']).reset_index().to_html(table_id="daily",
                                         classes=["table table-striped table-bordered table-hover"],
                                         index=False)

        month_df = pd.DataFrame(output['month']).reset_index().to_html(table_id="month",
                                         classes=["table table-striped table-bordered table-hover"],
                                         index=False)

        year_df = pd.DataFrame(output['year']).reset_index().to_html(table_id="year",
                                         classes=["table table-striped table-bordered table-hover"],
                                         index=False)

    return render_template('portfolio.html', title='Home Page', form=form,
                           contracts_df=contracts_df,
                           value_df=value_df,
                           daily_df=daily_df,
                           month_df=month_df,
                           year_df=year_df)


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)

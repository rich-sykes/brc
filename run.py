# import libraries
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
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

    # init web form
    form = PortfolioAgg()

    # init tables
    contracts_df = pd.DataFrame()
    value_df = pd.DataFrame()
    daily_df = pd.DataFrame()
    month_df = pd.DataFrame()
    year_df = pd.DataFrame()

    reporting_date = ""

    if form.validate_on_submit():

        # get aggregation_level
        aggregation_level = request.form.get('aggregation_level')

        # get reporting_date
        reporting_date = request.form.get('reporting_date')

        # execute aggregation
        output = agg_contracts(reporting_date=reporting_date, aggregation_level=aggregation_level)

        # table formats
        pd.options.display.float_format = '${:,.2f}'.format

        # contracts held
        contracts_df = output['contracts'].to_html(table_id="contracts",
                                         classes=["table table-striped table-bordered table-hover"],
                                         index=False)

        # portfolio value
        value_df = pd.DataFrame(output['value']).reset_index().to_html(table_id="value",
                                         classes=["table table-striped table-bordered table-hover"],
                                         index=False)

        # daily return
        daily_df = output['daily'].to_html(table_id="daily",
                                         classes=["table table-striped table-bordered table-hover"],
                                         index=False)

        # m-t-d return
        month_df = output['month'].to_html(table_id="month",
                                         classes=["table table-striped table-bordered table-hover"],
                                         index=False)

        # y-t-d return
        year_df = output['year'].to_html(table_id="year",
                                         classes=["table table-striped table-bordered table-hover"],
                                         index=False)

    return render_template('portfolio.html',
                           title='Home Page',
                           form=form,
                           reporting_date=reporting_date,
                           contracts_df=contracts_df,
                           value_df=value_df,
                           daily_df=daily_df,
                           month_df=month_df,
                           year_df=year_df)


if __name__ == "__main__":

    # run flask server
    app.run(host='127.0.0.1', port=5000, debug=True)

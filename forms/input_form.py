from wtforms import Form, SelectField, StringField, DateField, validators
from flask_wtf import FlaskForm


class PortfolioAgg(FlaskForm):

    # reporting_date = StringField('Report Date')
    reporting_date = DateField('Report Date DD/MM/YYYY', format='%d/%m/%Y')

    aggregation_level = SelectField('Aggregation Level',
                                    choices=[('Instrument Asset Class', 'Instrument Asset Class'),
                                             ('Instrument Description', 'Instrument Description'),
                                             ('Contract Ticker', 'Contract Ticker')]
                                    )


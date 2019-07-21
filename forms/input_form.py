from wtforms import Form, SelectField, DateField


class PortfolioAgg(Form):

    reporting_date = DateField('Report Date', format='%d/%m/%Y')

    aggregation_level = SelectField('Aggregation Level',
                                    choices=[('Instrument Asset Class' , 'Instrument Description', 'Contract Ticker'),
                                             ('Instrument Asset Class' , 'Instrument Description', 'Contract Ticker')])
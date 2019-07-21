# import libraries
from flask import Flask, render_template
from flask_bootstrap import Bootstrap

# create app
app = Flask(__name__)
bootstrap = Bootstrap(app)


# main page
@app.route('/', methods=['POST', 'GET'])
def index():



    return render_template('index.html', title='Home Page', year=2019,)

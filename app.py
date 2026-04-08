from flask import Flask, render_template, request
from username_scan import check_username

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    results = None

    if request.method == 'POST':
        username = request.form['username']
        results = check_username(username)

    return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
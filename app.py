from flask import Flask, render_template, request
from username_scan import check_username

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    risk_score = 0

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        if username:
            results, risk_score = check_username(username)

    return render_template('index.html', results=results, risk_score=risk_score)

if __name__ == '__main__':
    app.run(debug=False)
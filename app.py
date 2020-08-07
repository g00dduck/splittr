from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
@app.route('/<name>')
def hello_world(name=None):
    return render_template('index.html', name=name)

@app.route('/dashboard')
def get_dash():
    return render_template("dashboard.html")

if __name__ == '__main__':
    app.run(debug=True, port=5000)
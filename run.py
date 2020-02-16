
from flask import Flask, render_template, request, send_file
from main import generate


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/uploader', methods=['POST'])
def upload():
    if request.method == 'POST':
        genre = request.form['genre']
        instrument = request.form['instrument']
        duration = request.form['duration']

        fl = generate(genre, instrument, duration)

        return send_file('./'+fl, attachment_filename= fl)
    return render_template('index.html')



if __name__ == '__main__':
    app.run()
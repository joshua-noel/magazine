import os
from flask import Flask, request, redirect, url_for #URL imports
from flask import send_from_directory
from flask import g #DATABASE imports
import sqlite3
from werkzeug.utils import secure_filename
from datetime import datetime

DATABASE = f"{os.getcwd()}\storage\database.db"
UPLOAD_FOLDER = f"{os.getcwd()}\storage\\"
ALLOWED_EXTENSIONS = {"mp4"}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000 #16MB upload size

"""
URL stuff
"""
#the funny
@app.route("/harharhar")
def freddy():
    return "Fredrick Fazberry"

@app.route("/")
def root():
    return redirect(url_for('upload'))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']

        if file is None: #promopts resubmission if user trys to upload nothing
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            conn = get_db()
            cur = conn.cursor()
            cur.execute("INSERT INTO CLIPS (NAME, PATH, UPLOADTS) VALUES (?,?, ?)", (filename.strip(".mp4"), f"{UPLOAD_FOLDER}\\{filename}", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()

            return redirect(url_for('download_file', name=filename))
        
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

#EARMARKED
@app.route("/dbtest")
def dbtest():
    return_string = ""

    for record in query_db("SELECT * FROM CLIPS WHERE PATH = path/to/clip.mp4"):
        return_string = return_string + record[1] + "<br>"

    return return_string

@app.errorhandler(404)
def not_found(e):
  return "Custom 404 page", 404

@app.errorhandler(500)
def not_found(e):
  return "Custom 500 page", 500

"""
DATABASE stuff
"""
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
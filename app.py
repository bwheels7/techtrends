import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
from datetime import datetime
import logging

connectioncount = 0
# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global connectioncount
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    connectioncount+=1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      #logmessage('Article "{id}" not found'.format(id=post_id))
      app.logger.error('Article does not exist "404"')
      return render_template('404.html'), 404
    else:
      #logmessage('"{title}" found')
      app.logger.info('Article' +' "'+post['title']+'" ' + 'retrieved!')
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    logmessage('About page rendered')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            app.logger.info('A new article' +' "'+ title +'" ' + 'has been created!')
            return redirect(url_for('index'))

    return render_template('create.html')

# Healthz endpoint
@app.route('/healthz')
def healthz():
    try:
        connection = get_db_connection()
        connection.cursor()
        connection.execute('SELECT * FROM posts')
        connection.close()
        return {'result': 'OK - healthy'}
    except Exception:
        return {'result': 'ERROR - unhealthy'}, 500

# Metrics endpoint
@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    post_count = len(posts)
    data = {"db_connection_count": connectioncount, "post_count": post_count}
    return data


#Log messaging
def logmessage(msg):
    app.logger.info('{time} | {message}'.format(
        time=datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), message=msg))

# start the application on port 3111
if __name__ == "__main__":
   #logging.basicConfig(filename='apptt.log',level=logging.DEBUG)
   logging.basicConfig(level=logging.DEBUG)
   app.run(host='0.0.0.0', port='3111')


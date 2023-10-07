from flask import Flask, render_template, request,jsonify
import joblib
import re
import string
import pandas as pd
import mysql.connector

app = Flask(__name__)

# Load the trained model
Model = joblib.load(r'C:\Users\Pavilion\Desktop\Fake news detection project\Fake news detection project\model.pkl')

# Set up MySQL database connection
db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='news_data'
)

cursor = db.cursor()

def create_table():
    cursor.execute("""CREATE TABLE IF NOT EXISTS fake_news_data (id INT AUTO_INCREMENT PRIMARY KEY, input_text TEXT, prediction VARCHAR(255))""")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS form_submissions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            email VARCHAR(255),
            message TEXT
        )
    """)

create_table()

@app.route('/')
def index():
    return render_template("index.html")

def wordpre(text):
    text = text.lower()
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub("\\W"," ",text) # remove special chars
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub('<.*?>+', '', text)
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('\n', '', text)
    text = re.sub(r'\w*\d\w*', '', text)
    return text

@app.route('/',methods=['POST'])
def predict():
    if request.method == 'POST':
        txt = request.form['txt']
        txt = wordpre(txt)
        txt_list = [txt]
        result = Model.predict(txt_list)[0]
        result_text = str(result)
        insert_data(txt, result_text)
        return render_template("index.html", result = result)
    return '' 

@app.route('/submit', methods=['POST'])
def submit_form():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        
        # Insert form data into the database
        insert_data1(name, email, message)
        
        return "Form submitted successfully!"
    return ''

# Function to insert data into the database
def insert_data(input_text, prediction):
    query = "INSERT INTO fake_news_data (input_text, prediction) VALUES (%s, %s)"
    values = (input_text, prediction)
    cursor.execute(query, values)
    db.commit()

def insert_data1(name, email, message):
    query = "INSERT INTO form_submissions (name, email, message) VALUES (%s, %s, %s)"
    values = (name, email, message)
    cursor.execute(query, values)
    db.commit()


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)

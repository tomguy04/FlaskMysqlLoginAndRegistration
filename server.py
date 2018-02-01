from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
from datetime import datetime
import re
app = Flask(__name__)
app.secret_key = "ThisIsSecret!"
mysql = MySQLConnector(app,'dbloginregistration')

# our index route will handle rendering our form

#1
@app.route('/')
def index():
  #session['date'] =  datetime.now().strftime("%m/%d/%Y")
  return render_template("registrationForm.html")

# this route will handle our form submission
# notice how we defined which HTTP methods are allowed by this route
# WE ARE WAITING FOR A POST REQUEST
@app.route('/process', methods=['POST'])
def process():
  #do validation
  #setup the regex to check for just letters in the first and last names.
  ALPHA_REGEX = re.compile(r'^[a-zA-Z]+$')
  EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
  #some test values
  #A23456789
  #23456789A
  #ABCDEFGh9
  #9ABCDEFGh
  PW_U_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]*[A-Z]+[a-zA-Z0-9.+_-]*$')
  PW_NUM_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]*[0-9]+[a-zA-Z0-9.+_-]*$')
  BDAY_VALID_REGEX = re.compile(r'^[0-9]{2}\/{1}[0-9]{2}\/[0-9]{4}$')
  
  confPw = request.form['confpassword']
  query = "INSERT INTO tblusers (first_name, last_name, email, password, created_at, updated_at) VALUES (:fname, :lname, :email, :pw, NOW(), NOW())"
  
  # 1. First Name - letters only, at least 2 characters and that it was submitted
  # 2. Last Name - letters only, at least 2 characters and that it was submitted
  # 3. Email - Valid Email format, and that it was submitted
  # 4. Password - at least 8 characters, and that it was submitted
  # 5. Password Confirmation - matches password

  if not request.form['firstname'] or not request.form['lastname'] or not request.form['email'] or not request.form['password'] :
    flash(u"YOU SUCK!",'flashErrorMessages')
    return redirect('/') 
  else:
    if len(request.form['firstname']) < 2 or len(request.form['lastname']) < 2 or len(request.form['firstname']) < 2:# or len(lname) < 1 or len (session['pw']) < 1 or len(confPw) < 1 :
      flash(u"1. ->First Name - letters only, at least 2 characters",'flashErrorMessages')
      flash(u"2. ->Last Name - letters only, at least 2 characters",'flashErrorMessages')
      flash(u"3. Email - Valid Email format, and that it was submitted",'flashErrorMessages')
      flash(u"4. Password - at least 8 characters, and that it was submitted",'flashErrorMessages')
      flash(u"5. Password Confirmation - matches password",'flashErrorMessages')
      return redirect('/') 
    elif not EMAIL_REGEX.match(request.form['email']):
      flash(u"1. First Name - letters only, at least 2 characters",'flashErrorMessages')
      flash(u"2. Last Name - letters only, at least 2 characters",'flashErrorMessages')
      flash(u"3. -> Email - Valid Email format, and that it was submitted",'flashErrorMessages')
      flash(u"4. Password - at least 8 characters, and that it was submitted",'flashErrorMessages')
      flash(u"5. Password Confirmation - matches password",'flashErrorMessages')
      return redirect('/')
    elif len(request.form['password']) < 8:
      flash(u"1. First Name - letters only, at least 2 characters",'flashErrorMessages')
      flash(u"2. Last Name - letters only, at least 2 characters",'flashErrorMessages')
      flash(u"3. Email - Valid Email format, and that it was submitted",'flashErrorMessages')
      flash(u"4. --> Password - at least 8 characters, and that it was submitted",'flashErrorMessages')
      flash(u"5. Password Confirmation - matches password",'flashErrorMessages')
      return redirect('/')
    elif (request.form['password'] != request.form['confpassword']):
      flash(u"1. First Name - letters only, at least 2 characters",'flashErrorMessages')
      flash(u"2. Last Name - letters only, at least 2 characters",'flashErrorMessages')
      flash(u"3. Email - Valid Email format, and that it was submitted",'flashErrorMessages')
      flash(u"4. Password - at least 8 characters, and that it was submitted",'flashErrorMessages')
      flash(u"5. --> Password Confirmation - matches password",'flashErrorMessages')
      return redirect('/')
    else:

      data = {
                'fname': request.form['firstname'],
                'lname': request.form['lastname'],
                'email': request.form['email'],
                'pw' : request.form['password']
            }

      mysql.query_db(query, data)

      myUsers = mysql.query_db("SELECT * FROM tblusers")
      # return render_template('success.html', all_users=myUsers)
      return redirect('/loginCheck')

@app.route('/login', methods=['GET'])
def login():
  return  render_template('loginForm.html')

@app.route('/loginCheck', methods=['POST'])
def loginCheck():
  myemail = request.form['email']
  mypassword = request.form['password']
  users = mysql.query_db("SELECT * FROM tblusers")
  for row in users:
    if row['email'] == myemail and row['password'] == mypassword:
      return render_template('loginSuccess.html')
    else:
      return redirect('/login')
app.run(debug=True) # run our server


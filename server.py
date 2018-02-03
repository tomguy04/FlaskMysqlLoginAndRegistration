from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
from datetime import datetime
import re
import md5
app = Flask(__name__)
app.secret_key = "ThisIsSecret!"
mysql = MySQLConnector(app,'dbwall')

# our index route will handle rendering our form

#1
@app.route('/')
def index():
  return render_template("registrationForm.html")

@app.route('/insertComment', methods=['POST'])
def insertComment():
  query = "INSERT INTO tblComments (message_id, user_id, comment, created_at, updated_at) VALUES (:message_id, :user_id, :comment, NOW(), NOW())"
  data = {
            'comment': request.form['commentcontent'],
            'message_id': request.form['messageid'],
            "user_id":session["uid"]
        }

  row_id = mysql.query_db(query, data) #when there is an insert, we get back the id of the row inserted to.
  #session['uid']=user #this means we have a logged in user.
  #myUsers = mysql.query_db("SELECT * FROM tblusers")
  return redirect('/wall')

@app.route('/insertMessage', methods=['POST'])
def insertMessage():
  query = "INSERT INTO tblMessages (message, user_id, created_at, updated_at) VALUES (:message, :user_id, NOW(), NOW())"
  data = {
            'message': request.form['messagecontent'],
            "user_id":session["uid"]
        }

  row_id = mysql.query_db(query, data) #when there is an insert, we get back the id of the row inserted to.
  #session['uid']=user #this means we have a logged in user.
  #myUsers = mysql.query_db("SELECT * FROM tblusers")
  return redirect('/wall')


@app.route('/process', methods=['POST'])
def process():
  #do validation
  #setup the regex to check for just letters in the first and last names.
  ALPHA_REGEX = re.compile(r'^[a-zA-Z]+$')
  EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
  
  confPw = request.form['confpassword']
  query = "INSERT INTO tblusers (first_name, last_name, email, password, created_at, updated_at) VALUES (:fname, :lname, :email, :pw, NOW(), NOW())"
  
  if not request.form['firstname'] or not request.form['lastname'] or not request.form['email'] or not request.form['password'] :
    flash(u"You have not entered all the required data",'flashErrorMessages')
    return redirect('/') 
  else:
    if len(request.form['firstname']) < 2 or len(request.form['lastname']) < 2 or len(request.form['firstname']) < 2:# or len(lname) < 1 or len (session['pw']) < 1 or len(confPw) < 1 :
      flash(u"1. ->First Name - letters only, at least 2 characters",'flashErrorMessages')
      flash(u"2. ->Last Name - letters only, at least 2 characters",'flashErrorMessages')
      flash(u"3. Email - Valid Email format, and that it was submitted",'flashErrorMessages')
      flash(u"4. Password - at least 8 characters, and that it was submitted",'flashErrorMessages')
      flash(u"5. Password Confirmation - matches password",'flashErrorMessages')
      return redirect('/') 
    elif not request.form['firstname'].isalpha() or not request.form['lastname'].isalpha() :
      flash(u"first and last name must contain only alpha letters",'flashErrorMessages')
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
                'pw' : md5.new(request.form['password']).hexdigest()
            }
     
      new_user = mysql.query_db(query, data) #when there is an insert, we get back the id of the row inserted to.
      session['uid']=new_user #this means we have a logged in user.
      myUsers = mysql.query_db("SELECT * FROM tblusers")
      return redirect('/wall')

@app.route('/wall') # this is the success of a register!
def dashboard():
    #THIS IS A GIANT BLOB OF MESSAGE DATA AND COMMENT DATA, BUT NO COMMENT USER NAMES.    
    #query= mysql.query_db("select tblusers.first_name, tblmessages.message, tblmessages.user_id, tblmessages.id, tblmessages.created_at, tblmessages.updated_at, tblcomments.message_id, tblcomments.user_id, tblcomments.comment, tblcomments.created_at, tblcomments.updated_at from tblmessages join tblusers on tblmessages.user_id = tblusers.id left join tblcomments on tblmessages.id = tblcomments.message_id;")

    messageQuery= mysql.query_db("select tblusers.first_name, tblmessages.message, tblmessages.created_at, tblmessages.id from tblmessages join tblusers on tblmessages.user_id = tblusers.id")
    commentQuery=mysql.query_db("select tblcomments.comment, tblcomments.created_at, tblusers.first_name, tblcomments.message_id from tblcomments left join tblusers on tblcomments.user_id = tblusers.id")
    query2 = "SELECT * FROM tblusers WHERE id = :user_id" #being able to show this dashboard means there is an active session, someone is logged in.
    data = {
            "user_id":session["uid"]
        }   
    user = mysql.query_db(query2, data) #when there is a select, we get back a list of dictionaries converted from the rows of data selected.
    return render_template("wall.html", user = user[0], messages=messageQuery, comments=commentQuery) 

  #when dashboard.html access user.first_name, it's from user.  
  #USER from mysql.query_db(query, data) IS an list of one dictionary. user[0] is a dictioary.
  #[{u'first_name': u'Tom', u'last_name': u'Jones', u'created_at': datetime.datetime(2018, 2, 1, 17, 48, 40), 
  # u'updated_at': datetime.datetime(2018, 2, 1, 17, 48,40), u'email': u'1@1.com', u'password': u'123456789H', u'id': 31L}]

@app.route("/login", methods=["POST"])
def login():
	query = "SELECT * FROM tblusers WHERE email = :post_email"
	data = {
		"post_email":request.form["email"]
	}
	user = mysql.query_db(query, data) # []
	print user
	

	if len(user) > 0:
		user = user[0]
		if user["password"] ==  md5.new(request.form['password']).hexdigest():
			session["uid"] = user["id"]
			return redirect("/wall")
	flash("Email and password not found")
	return redirect("/")


#fresh login method one
# @app.route('/login', methods=['GET'])
# def login():
#   return  render_template('loginForm.html')

# ANOTHER WAY TO CHECK THE  LOGIN DATA
#  @app.route('/loginCheck', methods=['POST'])
# def loginCheck():
#   myemail = request.form['email']
#   mypassword = request.form['password']
#   users = mysql.query_db("SELECT * FROM tblusers")
#   for row in users:
#     if row['email'] == myemail and row['password'] == mypassword:
#       return render_template('loginSuccess.html')
#     else:
#       return redirect('/login')

@app.route("/logout")
def logout():
  session.clear()
  return redirect("/")
app.run(debug=True) # run our server


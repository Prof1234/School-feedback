from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re


app = Flask(__name__)

app.secret_key = '1a2b3c4d5e'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'college'

# Intialize MySQL
mysql = MySQL(app)


# router for home page
@app.route('/')
def home():
    return render_template("Home.html")

# router to registration page
@app.route('/register')
def registerPage():
    # code for getting all departments in the database
    cursor= mysql.connection.cursor()
    cursor.execute('SELECT dpt_id, department FROM faculty')
    departments = cursor.fetchall()
    return render_template('register.html', departments= departments)
    

# controller triggered when students form is posted
@app.route('/students', methods= ['GET', 'POST'])
def students():
    msg = ''
    if request.method== 'POST' and 'firstName' in request.form and 'lastName' in request.form and 'Email' in request.form and 'phone' in request.form and 'password' in request.form and 'dpt_id' in request.form and 'username' in request.form :
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        email = request.form['Email']
        phone = request.form['phone']
        password = request.form['password']
        username = request.form['username']
        dpt_id = request.form['dpt_id']
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO students(firstName, lastName, Email, phone, dpt_id) VALUES (%s, %s, %s, %s, %s)', (firstName, lastName, email, phone, dpt_id))
        mysql.connection.commit()
        cur.execute('INSERT INTO users(username, Email, user_pwd) VALUES (%s, %s, %s)', (username, email, password))
        mysql.connection.commit()
        cur.close()
        msg= 'success'
        return 'successful'
    elif request.method == 'POST':
        msg= 'please fill the form'
    
    return render_template('register.html', msg = msg)

# controller triggered when staff form is posted

@app.route('/staff', methods=['GET', 'POST'])
def staff():
    msg = ''
    if request.method == 'POST' and 'firstName' in request.form and 'lastName' in request.form and 'Email'in request.form and 'phone' in request.form and 'username' in request.form :
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        username = request.form['username']
        email = request.form['Email']
        phone = request.form['phone']
        dpt_id = request.form['dpt_id']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO staff(firstName, lastName, Email, phone, dpt_id) VALUES( %s, %s, %s, %s, %s)', (firstName, lastName, email, phone, dpt_id))
        mysql.connection.commit()
        cur.execute('INSERT INTO users(username, Email, user_pwd) VALUES (%s, %s, %s)', (username, email, password))
        mysql.connection.commit()
        cur.close()
        msg = 'success'
        return msg
    else:
        msg = 'Please enter the details needed'
        return msg
        
    return render_template('register.html', msg= msg)

# controller to carter for admin login

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method== 'POST' and 'adminEmail' in request.form and 'adminPassword' in request.form :
        email= request.form['adminEmail']
        password = request.form['adminPassword']
        #check if account exist
        cursor= mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM admin WHERE Email= %s AND admin_password= %s', (email, password) )
        account = cursor.fetchone()
        # if account exist in db
        if account:
            session['loggedin'] = True
            session['username'] = account['Email']
            return redirect(url_for('adminDashboard'))
        else:
            return 'incorrect details'

    else:
        return 'failed'

 # controller to carter for admin dashboard

# controller for adminDashboard
@app.route('/adminDashboard')
def adminDashboard():
    if 'loggedin' in session and session['username']=='admin@admin.com':   
        cursor= mysql.connection.cursor()
        cursor.execute('SELECT * FROM feedback ORDER BY avg_rating ASC')
        data = cursor.fetchall()
        cursor.execute('SELECT * FROM staff_feedback')
        staff_data= cursor.fetchall()
        return render_template('adminDashboard.html',data=data, username= session['username'] , staff_data = staff_data )
    else:
        x = 'admin not logged in you can not access account'
        return render_template('Home.html')
    


# controller to carter for students login
@app.route('/studentsLogin', methods=['GET', 'POST'])
def studentLogin():
    if request.method== 'POST' and 'studentsEmail' in request.form and 'studentsPassword' in request.form :
        email= request.form['studentsEmail']
        password = request.form['studentsPassword']
        #check if account exist
        cursor= mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE Email= %s AND user_pwd= %s', (email, password) )
        account = cursor.fetchone()
        # if account exist in db
        if account:
            session['loggedin'] = True
            session['username'] = account['username']
            return redirect(url_for('studentsDashboard'))  
        else:
            msg = 'Incorrect details'
            return msg
    else:
        return 'failed'

 # controller to carter for admin students dashboard


@app.route('/studentsDashboard')
def studentsDashboard():
    #check if student is loggedin
    if 'loggedin' in session:
        return render_template('studentsDashboard.html', username= session['username'])
    return redirect(url_for('home'))


# controller to carter for staff login
@app.route('/staffLogin', methods=['GET', 'POST'])
def staffLogin():
    if request.method== 'POST' and 'staffEmail' in request.form and 'staffPassword' in request.form :
        email= request.form['staffEmail']
        password = request.form['staffPassword']
        #check if account exist
        cursor= mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE Email= %s AND user_pwd= %s', (email, password) )
        account = cursor.fetchone()
        # if account exist in db
        if account:
            session['loggedin'] = True
            session['username'] = account['Email']
            return redirect(url_for('staffDashboard'))  
        else:
            msg = 'Incorrect details'
            return msg
    else:
        return 'failed'

 # controller to carter for admin students dashboard


#controller for staff dashboard
@app.route('/staffDashboard')
def staffDashboard():
    #check if student is loggedin
    if 'loggedin' in session:
        return render_template('staffDashboard.html')
    return redirect(url_for('home'))



@app.route('/studentsSubmit', methods=['GET', 'POST'])
def studentsSubmit():
    if request.method == 'POST' and 'loggedin' in session:
        course= (int)(request.form['ratingCourse'])
        canteen =(int)( request.form['ratingCanteen'])
        attendance=(int)( request.form['ratingAttendance'])
        teaching =(int)( request.form['ratingTeaching'])
        test =(int)( request.form['ratingTest'])
        department=(int)(request.form['ratingDepartment'])
        syllabus=(int)(request.form['ratingSyllabus'])
        studStaff =(int) (request.form['ratingStudStaff'])
        classrooms =(int) (request.form['ratingClass'])
        libs =(int) (request.form['ratingLibs'])
        labs =(int) (request.form['ratingLabs'])
        hostels =(int) (request.form['ratingHostels'])
        sendBy = session['username']
        fullName = request.form['fullname']

        staffComment = request.form['staff_comment']
        college =request.form['college_comment']
        avg = department + canteen + syllabus + labs + studStaff + libs + classrooms + hostels
        avg_rating = avg /8
        avg2 = course + attendance + teaching+ test 
        avg_rating2 = avg2 / 4

        cursor= mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM feedback WHERE SendBy = %s', [sendBy] )
        formIn = cursor.fetchone()
        if formIn:
            return 'You already submitted the form'

        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO feedback(avg_rating, comments, sendBy, department,canteen, syllabus, lab, studStaff, libs, classrooms, hostels) VALUES (%s, %s, %s, %s, %s, %s, %s, %s , %s ,%s, %s)', (avg_rating ,college, sendBy, department, canteen, syllabus, labs, studStaff, libs, classrooms, hostels))
        mysql.connection.commit()
        cur.execute('INSERT INTO staff_feedback(sendBy, fullname, avg_rating, comments, course_material, test, class_attendance, teaching) VALUES(%s, %s, %s ,%s, %s, %s ,%s ,%s)',(sendBy, fullName, avg_rating2, staffComment, course, test, attendance, teaching))
        mysql.connection.commit()
        cur.close()
        return "Successfully send the form"
    else:
        return 'error encountered on submittion'

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))   

@app.route('/addDepartment', methods= ['GET', 'POST'])
def addDpt():
    if request.method == 'POST' and 'department' in request.form:
        department = request.form['department']
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO faculty(department) VALUES (%s)', [department])
        mysql.connection.commit()
        return 'Department added successfully'
    else:
        return 'failed'
   
       





if __name__ =='__main__':
	app.run(debug=True)
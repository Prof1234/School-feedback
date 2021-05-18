from flask import Flask, render_template, request, redirect, url_for, session, flash, json, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import datetime

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

    return render_template('register.html')
    

# controller triggered when students form is posted
@app.route('/students', methods= ['GET', 'POST'])
def students():
    msg = ''
    if request.method== 'POST' and 'firstName' in request.form and 'lastName' in request.form and 'Email' in request.form and 'phone' in request.form and 'password' in request.form :
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        email = request.form['Email']
        phone = request.form['phone']
        password = request.form['password']
        username = request.form['username']
        
        isStudent = True
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO students(firstName, lastName, Email, phone) VALUES ( %s, %s, %s, %s)', (firstName, lastName, email, phone))
        mysql.connection.commit()
        cur.execute('INSERT INTO users(username, Email, user_pwd, isStudent) VALUES (%s, %s,%s, %s)', (username, email, password, isStudent))
        mysql.connection.commit()
        cur.close()
        flash("succefully registered the student")
        return redirect(url_for('home'))
    elif request.method == 'POST':
        msg= 'please fill the form'
    
    return render_template('register.html', msg = msg)

# controller triggered when staff form is posted

@app.route('/staff', methods=['GET', 'POST'])
def staff():
    msg = ''
    if request.method == 'POST' and 'first_name' in request.form and 'last_name' in request.form and 'email'in request.form and 'phone' in request.form and 'username' in request.form :
        firstName = request.form['first_name']
        lastName = request.form['last_name']
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        dpt_id = request.form['dpt_id']
        password = firstName[0].lower() + lastName.lower()
        isStudent = False
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO staff(firstName, lastName, Email, phone, dpt_id) VALUES( %s, %s, %s, %s, %s)', (firstName, lastName, email, phone, dpt_id))
        mysql.connection.commit()
        cur.execute('INSERT INTO users(username, Email, user_pwd, isStudent) VALUES (%s, %s, %s, %s)', (username, email, password, isStudent))
        mysql.connection.commit()
        cur.close()
        flash("successfully registered the new staff member")
        return redirect(url_for('adminDashboard'))
    else:
        msg = 'Please enter the details needed'
        return msg
        
    return render_template('register.html', msg= msg)

# controller to carter for admin login

@app.route('/login', methods=['GET', 'POST'])
def admin():
    if request.method== 'POST' and 'Email' in request.form and 'Password' in request.form :
        email= request.form['Email']
        password = request.form['Password']
        #check if account exist
        cursor= mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE Email= %s AND user_pwd= %s', (email, password) )
        account = cursor.fetchone()
        # if account exist in db
        if account:
            session['loggedin'] = True
            session['username'] = account['Email']
            if account['isStudent'] == None:
                return redirect('/adminDashboard')
            elif account['isStudent'] == True:
                return redirect('/studentsDashboard')
            else:
                return redirect('/staffDashboard')
  
        else:
            flash("Incorrect email or password")
            return render_template('home.html')

    else:
        return redirect(url_for('/'))

 # controller to carter for admin dashboard

# controller for adminDashboard
@app.route('/adminDashboard', methods= ["GET", "POST"])
def adminDashboard():
    if 'loggedin' in session and session['username']=='admin@admin.com':   
        cursor= mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM modules INNER JOIN faculty ON modules.dpt_id = faculty.dpt_id ORDER BY avg_rating ASC')
        data = cursor.fetchall()
        cursor.execute('SELECT *, staff.firstName, staff.lastName FROM staff_feedback INNER JOIN staff ON staff_feedback.Email = staff.Email ORDER BY avg_rating ASC')
        staff_data= cursor.fetchall()
        cursor.execute('SELECT *, staff.firstName, staff.lastName, FLOOR(AVG(staff_feedback.avg_rating)) AS avg_raing2, FLOOR(AVG(staff_feedback.explanation)), FLOOR(AVG(staff_feedback.opinions)), FLOOR(AVG(staff_feedback.labs)), FLOOR(AVG(staff_feedback.presentation)), FLOOR(AVG(staff_feedback.friendly)), FLOOR(AVG(staff_feedback.management)) FROM staff_feedback INNER JOIN staff ON staff_feedback.Email = staff.Email GROUP BY staff_feedback.dateSend, staff_feedback.Email')
        avaraged= cursor.fetchall()
        cursor.execute('SELECT *, FLOOR(AVG(modules.avg_rating)),FLOOR(AVG(modules.tutorials)), FLOOR(AVG(modules.links)), FLOOR(AVG(modules.skills)), FLOOR(AVG(modules.consult)), FLOOR(AVG(modules.content)), FLOOR(AVG(modules.materials)), FLOOR(AVG(modules.outlines)) FROM modules INNER JOIN faculty ON modules.dpt_id = faculty.dpt_id GROUP BY modules.dateSend, faculty.course')
        avaragedCourses= cursor.fetchall()
        

        # codes for loading courses
        cursor= mysql.connection.cursor()
        cursor.execute('SELECT dpt_id, course FROM faculty WHERE dpt_id NOT IN( SELECT dpt_id FROM staff) ')
        departments = cursor.fetchall()
        return render_template('adminDashboard.html',data=data, username= session['username'] , staff_data = staff_data, departments= departments, avaraged= avaraged, avaragedCourses= avaragedCourses)
    else:
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


@app.route('/studentsDashboard', methods= ['GET', 'POST'])
def studentsDashboard():
    #check if student is loggedin
    if 'loggedin' in session:
        cursor= mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT staff.Email, staff.firstName, staff.lastName, staff.dpt_id , faculty.course FROM staff INNER JOIN faculty ON staff.dpt_id = faculty.dpt_id')
        courses = cursor.fetchall()
        
        if request.method== 'POST':
            newPassword= request.form['newPassword']
            userEmail = session['username']
            cur = mysql.connection.cursor()
            cur.execute('UPDATE users SET user_pwd= %s WHERE Email = %s  ', (newPassword, userEmail))
            mysql.connection.commit()
            flash('Successfully updated the password')

        
        if 'messages' in session:
            messages = session['messages']
            flash(messages)
            return render_template('studentsDashboard.html', messages= messages,  username= session['username'], courses = courses)
        return render_template('studentsDashboard.html', username= session['username'], courses = courses)

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
@app.route('/staffDashboard', methods=['GET', 'POST'])
def staffDashboard():
    #check if student is loggedin
    if 'loggedin' in session:
        email = session['username']
        cursor= mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM staff_feedback WHERE Email = %s ORDER BY avg_rating ASC', [email])
        data = cursor.fetchall()

        cursor= mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM modules WHERE dpt_id IN (SELECT dpt_id FROM staff WHERE Email = %s)', [email])
        course_data = cursor.fetchall()
        cursor= mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT faculty.course FROM staff INNER JOIN faculty ON staff.dpt_id = faculty.dpt_id WHERE staff.Email = %s', [email])
        courseName = cursor.fetchall()
        cursor= mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor= mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT *, FLOOR(AVG(staff_feedback.avg_rating)) AS avg_raing2, FLOOR(AVG(staff_feedback.explanation)), FLOOR(AVG(staff_feedback.opinions)), FLOOR(AVG(staff_feedback.labs)), FLOOR(AVG(staff_feedback.presentation)), FLOOR(AVG(staff_feedback.friendly)), FLOOR(AVG(staff_feedback.management)) FROM staff_feedback WHERE staff_feedback.Email= %s GROUP BY staff_feedback.dateSend', [email])
        avaraged = cursor.fetchall()
        cursor= mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT *,FLOOR(AVG(modules.tutorials)), FLOOR(AVG(modules.links)), FLOOR(AVG(modules.skills)), FLOOR(AVG(modules.consult)), FLOOR(AVG(modules.content)), FLOOR(AVG(modules.materials)), FLOOR(AVG(modules.outlines))  FROM modules WHERE dpt_id IN (SELECT dpt_id FROM staff WHERE Email = %s) GROUP BY modules.dateSend', [email])
        avaragedCourses = cursor.fetchall()

        if request.method== 'POST':
            newPassword= request.form['newPassword']
            userEmail = session['username']
            cur = mysql.connection.cursor()
            cur.execute('UPDATE users SET user_pwd= %s WHERE Email = %s  ', (newPassword, userEmail))
            mysql.connection.commit()
            flash('Successfully updated the password')

        return render_template('staffDashboard.html', data = data , username = session['username'], course_data= course_data, avaraged= avaraged, avaragedCourses= avaragedCourses)
    else:
        return redirect(url_for('home'))
   



@app.route('/studentsSubmit', methods=['GET', 'POST'])
def studentsSubmit():
    if request.method == 'POST' and 'loggedin' in session:
        presentation= (int)(request.form['ratingPresent'])
        friendly =(int)( request.form['ratingFriendly'])
        management=(int)( request.form['ratingManange'])
        explanation =(int)( request.form['ratingExplain'])
        opinions =(int)( request.form['ratingOpinions'])
        labs=(int)(request.form['ratingLabs'])
        # feedback on modules
        tutorials =(int) (request.form['ratingTutorials'])
        links =(int) (request.form['ratingLinks'])
        skills =(int) (request.form['ratingSkills'])
        consult =(int) (request.form['ratingConsult'])
        content =(int) (request.form['ratingContent'])
        materials =(int) (request.form['ratingMaterials'])
        outlines =(int) (request.form['ratingOutlines'])
        sendBy = session['username']
        fullName = request.form['fullname']
        dateSend = str(datetime.date.today()) 
        dpt = (int)(request.form['dpt'])

        sum1 = presentation+ friendly + management + explanation + opinions + labs
        avg1= sum1/ 6

        sum2= tutorials+ links + skills + consult + content + materials + outlines 
        avg2 = sum2/ 7

        staffComment = request.form['staff_comment']
        college = request.form['college_comment']

        cursor= mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT id, Email FROM staff_feedback WHERE Email= %s AND sendBY= %s AND dateSend = %s', (fullName, sendBy, dateSend))
        formIn = cursor.fetchone()
        if formIn:
            session['messages'] = "You already submitted that form today"
            return redirect(url_for('studentsDashboard'))
  
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO staff_feedback(Email, SendBY, presentation, friendly, management, explanation, opinions, labs, comments, avg_rating, dateSend) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )', (fullName, sendBy, presentation, friendly, management, explanation, opinions, labs, staffComment, avg1, dateSend))
        mysql.connection.commit()
        cur.execute('INSERT INTO modules(dpt_id, sendBy, tutorials, links, skills, consult, content, materials, outlines, comments, avg_rating, dateSend) VALUES(%s ,%s, %s, %s ,%s ,%s, %s, %s, %s, %s, %s, %s )',(dpt, sendBy, tutorials, links, skills, consult, content, materials,outlines, college, avg2, dateSend))
        mysql.connection.commit()
        cur.close()
        flash("Successfully send the form")
        return redirect(url_for('studentsDashboard'))
    else:
        return 'error encountered on submittion'

  

@app.route('/addDepartment', methods= ['GET', 'POST'])
def addDpt():
    if request.method == 'POST' and 'department' in request.form:
        department = request.form['department']
        try:
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO faculty(course) VALUES (%s)', [department])
            mysql.connection.commit()
            flash("successfully added a new course")
            return redirect(url_for('adminDashboard'))
        except MySQLdb.Error as e:
            flash("You already added that course")
            return redirect(url_for('adminDashboard'))
    else:
        return 'failed'
   


@app.route('/user/change_password', methods=['GET', 'POST'])
def changePassword():
    if request.method == "POST" and 'category' in request.form:
        category = request.form['category']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        userEmail= request.form['Email']
        newPassword = request.form['new_password']
        if category == 'staff':
            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM staff WHERE firstName = %s AND lastName = %s', (firstName, lastName))
            mysql.connection.commit()
        else:
            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM students WHERE firstName = %s AND lastName = %s', (firstName, lastName))
            mysql.connection.commit()
        
        if cur:
            cur = mysql.connection.cursor()
            cur.execute('UPDATE users SET user_pwd= %s WHERE Email = %s  ', (newPassword, userEmail))
            mysql.connection.commit()
            flash('Successfully updated the password')
            return redirect(url_for('home'))
        else:
            return 'Details submitted did not match'
    else:
        return render_template('reset_password.html')




        

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home')) 



if __name__ =='__main__':
	app.run(debug=True)
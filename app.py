from flask import Flask, flash, render_template, request
from flask_sqlalchemy import SQLAlchemy
import logging
from CourseLogics import add_course, drop_course

app = Flask(__name__)
# Set up logging
logging.basicConfig(level=logging.INFO)
# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://ph:test123@localhost/course_selection'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Initialize SQLAlchemy
db = SQLAlchemy(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add', methods=['GET','POST'])
def add_form():
    if request.method == 'POST':
        student_id = request.form['inputStudentID']
        course_id = request.form['inputCourseID']
        logging.info(f'Student ID: {student_id}')
        logging.info(f'Course ID: {course_id}')       
        # Call add_course function to attempt adding the course
        result = add_course(db, student_id, course_id) 
        # Return result to the user
        return result
    else:
        # Handle GET request
        return render_template('add.html')



@app.route('/drop', methods=['GET', 'POST'])
def drop():
    if request.method == 'POST':
        # Retrieve form data
        student_id = request.form['inputStudentID']
        course_id = request.form['inputCourseID'] 
        logging.info(f'Student ID: {student_id}')
        logging.info(f'Course ID: {course_id}')
        # Call add_course function to attempt adding the course
        result = drop_course(db, student_id, course_id) 
        # Return result to the user
        return result
    else:
        # Handle GET request
        return render_template('drop.html')



@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        department = request.form['inputDepartment']
        year = request.form['inputYear']
        logging.info(type(department))
        logging.info(type(year))
        try:
            db.session.begin_nested()
            # Create a new student, need to be careful with strings
            db.engine.execute("INSERT INTO Students (department, year) VALUES (%s, %s)", (department, year))
            # get the lastest student's id
            student_id = db.engine.execute("""SELECT student_id
                                        FROM Students
                                        ORDER BY student_id DESC
                                        LIMIT 1""").fetchone()[0]
            
            # get all the course_id with same department, same year, and is_mandatory is True
            course_ids = db.engine.execute("""SELECT course_id
                                        FROM Courses
                                        WHERE department = %s 
                                        AND year = %s
                                        AND is_mandatory = True""", (department, year)).fetchall()
            course_ids = [row[0] for row in course_ids]
            for course_id in course_ids:
                db.engine.execute(f"INSERT INTO Enrollments(student_id, course_id) VALUES ({student_id}, {course_id})")
            logging.info(course_ids)
            # To-do: update student total credits
            db.session.commit()
            return "success"
        except Exception as e:
                # Rollback the transaction if an error occurs
                db.session.rollback()
                return str(e)
    else:
        return render_template('create.html')

@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    if request.method == 'POST':
        # Retrieve data
        student_id = request.form['inputStudentID']
        try:
            db.session.begin_nested()
            # Query the database to retrieve the courses for the given student_id
            courses_data = db.engine.execute(f"""SELECT course_name, period
                                        FROM Enrollments 
                                        Left JOIN Courses
                                        ON Courses.course_id = Enrollments.course_id
                                        WHERE student_id={student_id}""").fetchall()
            courses = [(row[0], row[1]) for row in courses_data]
            formatted_courses = '<br>'.join([f"{course[0]}: {course[1]}" for course in courses])
            # Pass the courses data to the template
            logging.info(courses)
            flash('Course successfully added!')
            db.session.commit()
            return formatted_courses
        except Exception as e:
            # Rollback the transaction if an error occurs
            db.session.rollback()
            return str(e)
    else:
        # Handle GET request (render the schedule template)
        return render_template('schedule.html')

if __name__ == '__main__':
    app.run(debug=True)

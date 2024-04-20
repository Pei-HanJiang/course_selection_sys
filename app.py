from flask import Flask, flash, render_template, request
from flask_sqlalchemy import SQLAlchemy
import logging
from CourseLogics import add_course, drop_course, create_student

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
        logging.info(department)
        logging.info(year)

        student_id = create_student(db, department, year)
        
        # get all the course_id with same department, same year, and is_mandatory is True
        course_ids = db.engine.execute("""SELECT course_id
                                    FROM Courses
                                    WHERE department = %s 
                                    AND year = %s
                                    AND is_mandatory = True""", (department, year)).fetchall()
        course_ids = [str(row[0]) for row in course_ids]
        logging.info(course_ids)
        logging.info(student_id)
        for course_id in course_ids:
            logging.info(type(course_id))
            result = add_course(db, str(student_id), course_id)
            logging.info(result)

        return "student created successfully"

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
            query = """SELECT course_name, period
                        FROM Enrollments 
                        Left JOIN Courses
                        ON Courses.course_id = Enrollments.course_id
                        WHERE student_id=%s"""
            courses_data = db.engine.execute(query, (student_id)).fetchall()
            courses = [(row[0], row[1]) for row in courses_data]
            formatted_courses = '<br>'.join([f"{course[0]}: {course[1]}" for course in courses])
            # Pass the courses data to the template
            logging.info(courses)
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

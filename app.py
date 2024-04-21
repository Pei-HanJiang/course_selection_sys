from flask import Flask, flash, render_template, request
from flask_sqlalchemy import SQLAlchemy
import logging
import json
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
        # Query the database to retrieve the courses for the given student_id
        query = """SELECT Courses.course_id, course_name, department, year, is_mandatory, max_capacity, current_capacity, credit, period
                    FROM Enrollments 
                    Left JOIN Courses
                    ON Courses.course_id = Enrollments.course_id
                    WHERE student_id=%s"""
        courses_data = db.engine.execute(query, (student_id)).fetchall()
        courses_data = [(*row,) for row in courses_data]
        logging.info(courses_data)

        headers = ['CourseId', 'CourseName', 'Department', 'Year', 'Mandatory', 'MaxCapacity', 'CurrentCap', 'Credit', 'Period']
        html_table = '<table style="width:100%; text-align:center;"><tr>' + ''.join(f"<th>{header}</th>" for header in headers) + '</tr>'
        for course in courses_data:
            html_table += '<tr>' + ''.join(f"<td>{str(value)}</td>" for value in course) + '</tr>'

        html_table += '</table>'
        formatted_courses = html_table
        return formatted_courses
    else:
        # Handle GET request
        return render_template('schedule.html')

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

import logging
app = Flask(__name__)
# Set up logging
logging.basicConfig(level=logging.INFO)

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://ph:test123@localhost/course_selection'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)
def has_overlap(str1, str2):
    slots1 = set(str1.split(','))
    slots2 = set(str2.split(','))
    overlap = slots1.intersection(slots2)
    return bool(overlap)


@app.route('/')
def index():
    return render_template('index.html')

# no need to query in every condition
@app.route('/add', methods=['GET','POST'])
def add():
    if request.method == 'POST':
        # Retrieve form data
        student_id = request.form['inputStudentID']
        course_id = request.form['inputCourseID']
        # double-check 
        # logging.info(f'Student ID: {student_id}')
        # logging.info(f'Course ID: {course_id}')
        # dummy-proof
        # 4. if course period overlaps
        periods = db.engine.execute(f"""SELECT period
                                    FROM Enrollments
                                    LEFT JOIN Courses
                                    ON Courses.course_id = Enrollments.course_id
                                    WHERE student_id = {student_id}
                                    """).fetchall()
        periods = [row[0] for row in periods]
        logging.info(periods)

        course_periods = db.engine.execute(f"""SELECT period
                                           FROM Courses
                                           WHERE course_id = {course_id}""")
        course_periods = [row[0] for row in course_periods]
        logging.info(course_periods)
        if has_overlap(course_periods[0], periods[0]):
            return "fail, Course period overlaps"
        
        # 1. if chosen already => test pass
        chosen_ids = db.engine.execute(f"""SELECT course_id
                                       FROM Enrollments 
                                       WHERE student_id={student_id}""").fetchall()
        chosen_ids = [str(row[0]) for row in chosen_ids]
        if course_id in chosen_ids:
            return "fail, course chosen already"
        
        # 2. if student belongs to the department => test pass
        s_department = db.engine.execute(f"""SELECT department 
                                       FROM Students 
                                       WHERE student_id={student_id}
                                       """).fetchone()
        # logging.info(s_department)
        c_department = db.engine.execute(f"""SELECT department 
                                       FROM Courses 
                                       WHERE course_id={course_id}
                                       """).fetchone()
        # logging.info(c_department)
        if s_department != c_department:
            return "fail, the student does not belong to the department"

        # 3. if course reaches max capacity => test pass
        max_capacity, current_capacity = db.engine.execute(f"""SELECT max_capacity, current_capacity
                                                           FROM Courses 
                                                           WHERE course_id={course_id}
                                                           """).fetchone()
        if current_capacity >= max_capacity:
            return "fail, the course is too full"
        
        # 5. if the name of course is already chosen => test pass
        course_name = db.engine.execute(f"""SELECT course_name
                                        FROM Courses
                                        WHERE course_id={course_id}
                                        """).fetchone()
        course_name = course_name[0]
        # logging.info(course_name)
        chosen_course_name = db.engine.execute(f"""SELECT course_name
                                          FROM Enrollments
                                          Left JOIN Courses
                                          ON Courses.course_id = Enrollments.course_id
                                          WHERE student_id={student_id}""").fetchall()
        chosen_course_name = [row[0] for row in chosen_course_name]
        # logging.info(chosen_course_name)
        if course_name in chosen_course_name:
            return "fail, the course name is already chosen"
        # 6. student credits > 30 => test pass
        current_credit = db.engine.execute(f"""SELECT total_credit
                                           FROM Students
                                           WHERE student_id={student_id}""").fetchone()
        current_credit = current_credit[0]
        course_credit = db.engine.execute(f"""SELECT credit
                                          FROM Courses
                                          WHERE course_id={course_id}""").fetchone()
        course_credit = course_credit[0]
        if current_credit + course_credit > 30:
            return "fail, exceed credit limit"

        
        
        # Add student_id and course_id to Enrollments table
        db.engine.execute(f"INSERT INTO Enrollments(student_id, course_id) VALUES ({student_id}, {course_id})")
        # 1. Add credit to student's total credit
        db.engine.execute(f"""UPDATE Students
                            SET total_credit = total_credit + {course_credit}
                            WHERE student_id={student_id}
                            """)
        # 2. +1 to current capacity
        db.engine.execute(f"""UPDATE Courses
                            SET current_capacity = current_capacity + 1 
                            WHERE course_id={course_id}
                            """)

        # give a notice wether it's done or not, then return empty template

        return render_template('add.html')
    else:
        # Handle GET request (e.g., render the form)
        return render_template('add.html')



@app.route('/drop', methods=['GET', 'POST'])
def drop():
    if request.method == 'POST':
        # Retrieve form data
        student_id = request.form['inputStudentID']
        course_id = request.form['inputCourseID']
        # dummy-proof
        
        
        # double-check 
        # logging.info(f'Student ID: {student_id}')
        # logging.info(f'Course ID: {course_id}')
        # Delete from enrollments where student_id and course_id equals given data
        db.engine.execute(f"DELETE FROM Enrollments WHERE student_id={student_id} AND course_id={course_id}")
        # give a notice wether it's done or not, then return empty template
        return render_template('drop.html')
    else:
        # Handle GET request (e.g., render the form)
        return render_template('drop.html')



@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    if request.method == 'POST':
        # Retrieve data
        student_id = request.form['inputStudentID']
        # Query the database to retrieve the courses for the given student_id
        courses_data = db.engine.execute(f"""SELECT course_name, periods
                                       FROM Enrollments 
                                       Left JOIN Courses
                                       ON Courses.course_id = Enrollments.course_id
                                       WHERE student_id={student_id}""").fetchall()
        courses = [(row[0], row[1]) for row in courses_data]
        # Pass the courses data to the template
        return render_template('schedule.html', courses=courses)
    else:
        # Handle GET request (render the schedule template)
        return render_template('schedule.html')

if __name__ == '__main__':
    app.run(debug=True)

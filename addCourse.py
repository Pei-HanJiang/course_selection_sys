from flask import Flask, flash, render_template, request
from flask_sqlalchemy import SQLAlchemy
def has_overlap(list1, str2):
    slots1 = set(list1.split(','))
    print(f"slots1:{slots1}")
    slots2 = set(str2.split(','))
    print(f"slots2:{slots2}")
    overlap = slots1.intersection(slots2)
    print(f"overlap:{overlap}")
    return bool(overlap)

# add a course logics
def course_exist(db, course_id):
    query = "SELECT course_id FROM Courses"
    course_ids = db.engine.execute(query).fetchall()
    course_ids = [str(row[0]) for row in course_ids]
    return course_id in course_ids

def student_exist(db, student_id):
    query = "SELECT student_id FROM Students"
    student_ids = db.engine.execute(query).fetchall()
    student_ids = [str(row[0]) for row in student_ids]
    return student_id in student_ids

def is_course_chosen(db, student_id, course_id):
    query = "SELECT course_id FROM Enrollments WHERE student_id=%s"
    chosen_ids = db.engine.execute(query, (student_id)).fetchall()
    chosen_ids = [str(row[0]) for row in chosen_ids]
    return course_id in chosen_ids

def is_course_name_chosen(db, student_id, course_id):
    query = "SELECT course_name FROM Courses WHERE course_id=%s"
    course_name = db.engine.execute(query, (course_id)).fetchone()[0]
    query = """SELECT course_name FROM Enrollments
               LEFT JOIN Courses ON Courses.course_id = Enrollments.course_id
               WHERE student_id=%s"""
    chosen_course_name = db.engine.execute(query, (student_id)).fetchall()
    chosen_course_name = [row[0] for row in chosen_course_name]
    return course_name in chosen_course_name

def is_student_in_department(db, student_id, course_id):
    query = "SELECT department FROM Students WHERE student_id=%s"
    s_department = db.engine.execute(query, (student_id)).fetchone()
    query = "SELECT department FROM Courses WHERE course_id=%s"
    c_department = db.engine.execute(query,(course_id)).fetchone()
    return s_department == c_department

def is_course_full(db, course_id):
    query = "SELECT max_capacity, current_capacity FROM Courses WHERE course_id=%s"
    max_capacity, current_capacity = db.engine.execute(query,(course_id)).fetchone()
    return current_capacity >= max_capacity

def is_period_overlapping(db, student_id, course_id):
    query = """SELECT period FROM Enrollments
               LEFT JOIN Courses ON Courses.course_id = Enrollments.course_id
               WHERE student_id = %s"""
    periods = db.engine.execute(query, (student_id)).fetchall()
    periods = [row[0] for row in periods]
    periods_combined = ','.join(periods)
    query = "SELECT period FROM Courses WHERE course_id=%s"
    course_periods = db.engine.execute(query, (course_id)).fetchall()
    course_periods = [row[0] for row in course_periods]
    course_slots = ','.join(course_periods)
    return has_overlap(periods_combined, course_slots)

def is_credit_limit_exceeded(db, student_id, course_id):
    query = "SELECT total_credit FROM Students WHERE student_id=%s"
    current_credit = db.engine.execute(query, (student_id)).fetchone()[0]
    query = "SELECT credit FROM Courses WHERE course_id=%s"
    course_credit = db.engine.execute(query, (course_id)).fetchone()[0]
    return current_credit + course_credit > 30
# end of add course logics

def add_course(db, student_id, course_id):
    try:
        if not course_exist(db, course_id):
            return "fail, course not found"
        if not student_exist(db, student_id):
            return "fail, student not found"
        if is_course_chosen(db, student_id, course_id):
            return "fail, course chosen already"
        if is_course_name_chosen(db, student_id, course_id):
            return "fail, the course name is already chosen"
        if not is_student_in_department(db, student_id, course_id):
            return "fail, the student does not belong to the department"
        if is_course_full(db, course_id):
            return "fail, the course is too full"
        if is_credit_limit_exceeded(db, student_id, course_id):
            return "fail, exceed credit limit"
        if is_period_overlapping(db, student_id, course_id):
            return "fail, Course period overlaps"
        
        # Start a nested transaction
        db.session.begin_nested()

        # Add student_id and course_id to Enrollments table
        query = "INSERT INTO Enrollments(student_id, course_id) VALUES (%s, %s)"
        db.engine.execute(query, (student_id, course_id))

        # Update student's total credit
        query = """UPDATE Students SET total_credit = total_credit +
                   (SELECT credit FROM Courses WHERE course_id = %s)
                   WHERE student_id = %s"""
        db.engine.execute(query, (course_id, student_id))

        # Update current capacity of the course
        query = "UPDATE Courses SET current_capacity = current_capacity + 1 WHERE course_id = %s"
        db.engine.execute(query, (course_id,))

        # Commit the nested transaction
        db.session.commit()

        return "add course successfully"

    except Exception as e:
        # Rollback the nested transaction if an error occurs
        db.session.rollback()
        return str(e)

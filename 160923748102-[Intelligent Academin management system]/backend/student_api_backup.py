import pandas as pd
import numpy as np


def make_json_safe(value):

    if isinstance(value, np.integer):
        return int(value)

    if isinstance(value, np.floating):
        return float(value)

    if isinstance(value, np.ndarray):
        return value.tolist()

    if pd.isna(value):
        return None

    if isinstance(value, dict):
        return {
            key: make_json_safe(val)
            for key, val in value.items()
        }

    if isinstance(value, list):
        return [
            make_json_safe(item)
            for item in value
        ]

    return value


def get_student_view(student_id):

    # --------------------------------------------------
    # Load student information
    # --------------------------------------------------

    students = pd.read_csv(
        "data/students.csv"
    )

    registrations = pd.read_csv(
        "data/registrations.csv"
    )

    timetable = pd.read_csv(
        "outputs/exam_timetable.csv"
    )

    rooms = pd.read_csv(
        "outputs/hybrid_room_allocation.csv"
    )

    # --------------------------------------------------
    # Find student
    # --------------------------------------------------

    student = students[
        students["student_id"].astype(str) == str(student_id)
    ]

    if student.empty:

        return {
            "success": False,
            "error": "Student ID not found."
        }

    # --------------------------------------------------
    # Get student's registered subjects
    # --------------------------------------------------

    registered = registrations[
        registrations["student_id"].astype(str) == str(student_id)
    ]

    # --------------------------------------------------
    # Connect registrations with timetable
    # --------------------------------------------------

    exams = registered.merge(
        timetable,
        on="subject_id",
        how="left"
    )

    # --------------------------------------------------
    # Get student's room and seat
    # --------------------------------------------------

    student_rooms = rooms[
        rooms["student_id"].astype(str) == str(student_id)
    ]

    exams = exams.merge(
        student_rooms[
            [
                "subject_id",
                "slot_id",
                "room_id",
                "seat_number"
            ]
        ],
        on=[
            "subject_id",
            "slot_id"
        ],
        how="left"
    )

    # --------------------------------------------------
    # Student information
    # --------------------------------------------------

    student_info = student.iloc[0].to_dict()

    # --------------------------------------------------
    # Select exam information
    # --------------------------------------------------

    exam_columns = [
        "exam_id",
        "subject_id",
        "exam_date",
        "slot_name",
        "start_time",
        "end_time",
        "duration_minutes",
        "room_id",
        "seat_number"
    ]

    exams = exams[exam_columns]

    exams = exams.sort_values(
        [
            "exam_date",
            "start_time"
        ]
    )

    # --------------------------------------------------
    # Convert Pandas / NumPy values to JSON-safe values
    # --------------------------------------------------

    student_info = make_json_safe(student_info)

    exam_data = exams.to_dict(
        orient="records"
    )

    exam_data = make_json_safe(exam_data)

    # --------------------------------------------------
    # Return student dashboard data
    # --------------------------------------------------

    return {

        "success": True,

        "student": student_info,

        "exams": exam_data

    }


if __name__ == "__main__":

    result = get_student_view(
        "CSE6A001"
    )

    print(result)
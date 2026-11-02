import pandas as pd
import numpy as np


def make_json_safe(value):

    if isinstance(value, np.integer):
        return int(value)

    if isinstance(value, np.floating):
        return float(value)

    if isinstance(value, np.ndarray):
        return [
            make_json_safe(item)
            for item in value.tolist()
        ]

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

    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    return value


def get_student_view(student_id):

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

    student = students[
        students["student_id"].astype(str) == str(student_id)
    ]

    if student.empty:

        return {
            "success": False,
            "error": "Student ID not found."
        }

    registered = registrations[
        registrations["student_id"].astype(str) == str(student_id)
    ]

    exams = registered.merge(
        timetable,
        on="subject_id",
        how="left"
    )

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

    student_info = student.iloc[0].to_dict()

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

    student_info = make_json_safe(student_info)

    exam_data = exams.to_dict(
        orient="records"
    )

    exam_data = make_json_safe(exam_data)

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

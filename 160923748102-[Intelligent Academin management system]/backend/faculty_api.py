import os
import pandas as pd


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


def get_faculty_view(faculty_id):

    faculty_file = os.path.join(
        BASE_DIR,
        "data",
        "faculty.csv"
    )

    duties_file = os.path.join(
        BASE_DIR,
        "outputs",
        "hybrid_invigilator_duties.csv"
    )

    timetable_file = os.path.join(
        BASE_DIR,
        "outputs",
        "exam_timetable.csv"
    )

    if not os.path.exists(faculty_file):
        raise Exception("Faculty data file not found.")

    if not os.path.exists(duties_file):
        raise Exception("Invigilator duties file not found.")

    if not os.path.exists(timetable_file):
        raise Exception("Exam timetable file not found.")

    faculty_df = pd.read_csv(faculty_file)

    duties_df = pd.read_csv(duties_file)

    timetable_df = pd.read_csv(timetable_file)

    faculty_id = str(faculty_id).strip()

    faculty = faculty_df[
        faculty_df["faculty_id"].astype(str) == faculty_id
    ]

    if faculty.empty:
        return {
            "success": False,
            "error": "Faculty not found."
        }

    faculty_info = faculty.iloc[0].to_dict()

    faculty_duties = duties_df[
        duties_df["faculty_id"].astype(str) == faculty_id
    ].copy()

    # Add timetable information to each invigilation duty
    timetable_columns = [
        "subject_id",
        "slot_id",
        "exam_date",
        "slot_name",
        "start_time",
        "end_time"
    ]

    available_columns = [
        column
        for column in timetable_columns
        if column in timetable_df.columns
    ]

    timetable_info = timetable_df[
        available_columns
    ].copy()

    # Match duties with timetable using subject and slot
    merge_columns = [
        column
        for column in ["subject_id", "slot_id"]
        if column in faculty_duties.columns
        and column in timetable_info.columns
    ]

    if merge_columns:
        faculty_duties = faculty_duties.merge(
            timetable_info,
            on=merge_columns,
            how="left"
        )

    duties = faculty_duties.to_dict(
        orient="records"
    )

    return {
        "success": True,
        "faculty": faculty_info,
        "duties": duties
    }

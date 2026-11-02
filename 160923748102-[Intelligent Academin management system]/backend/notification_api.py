import pandas as pd


def generate_notifications():

    notifications = []

    # --------------------------------------------------------
    # Exam timetable notification
    # --------------------------------------------------------

    timetable_file = "outputs/exam_timetable.csv"

    try:

        timetable = pd.read_csv(timetable_file)

        for _, exam in timetable.iterrows():

            notifications.append({

                "type": "exam",

                "title": "Exam Timetable Published",

                "message": (
                    f"{exam['subject_id']} exam is scheduled on "
                    f"{exam['exam_date']} from "
                    f"{exam['start_time']} to "
                    f"{exam['end_time']}."
                ),

                "subject_id": exam["subject_id"],

                "exam_date": exam["exam_date"],

                "slot_id": exam["slot_id"]

            })

    except FileNotFoundError:

        pass


    # --------------------------------------------------------
    # Invigilator notification
    # --------------------------------------------------------

    invigilator_file = (
        "outputs/hybrid_invigilator_duties.csv"
    )

    try:

        duties = pd.read_csv(
            invigilator_file
        )

        for _, duty in duties.iterrows():

            notifications.append({

                "type": "invigilator",

                "title": "Invigilation Duty Assigned",

                "message": (
                    f"Faculty {duty['faculty_id']} is assigned "
                    f"to {duty['subject_id']} in "
                    f"room {duty['room_id']} "
                    f"during {duty['slot_id']}."
                ),

                "faculty_id": duty["faculty_id"],

                "subject_id": duty["subject_id"],

                "room_id": duty["room_id"],

                "slot_id": duty["slot_id"]

            })

    except FileNotFoundError:

        pass


    return notifications
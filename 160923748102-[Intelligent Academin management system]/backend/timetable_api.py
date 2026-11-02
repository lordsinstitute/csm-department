import pandas as pd
import os


def generate_timetable():

    schedule = pd.read_csv("outputs/hybrid_final_schedule.csv")
    slots = pd.read_csv("data/exam_slots.csv")
    exams = pd.read_csv("data/exams.csv")

    timetable = schedule.merge(
        exams[
            [
                "subject_id",
                "exam_id",
                "duration_minutes"
            ]
        ],
        on="subject_id",
        how="left"
    )

    timetable = timetable.merge(
        slots,
        on="slot_id",
        how="left"
    )

    timetable = timetable[
        [
            "exam_id",
            "subject_id",
            "slot_id",
            "exam_date",
            "slot_name",
            "start_time",
            "end_time",
            "duration_minutes"
        ]
    ]

    timetable = timetable.sort_values(
        [
            "exam_date",
            "start_time"
        ]
    )

    os.makedirs("outputs", exist_ok=True)

    output_file = "outputs/exam_timetable.csv"

    timetable.to_csv(
        output_file,
        index=False
    )

    return timetable


if __name__ == "__main__":

    print("\n")
    print("=" * 60)
    print("SMART EXAM - TIMETABLE")
    print("=" * 60)

    timetable = generate_timetable()

    print("\nEXAM TIMETABLE")
    print("-" * 60)

    print(
        timetable.to_string(
            index=False
        )
    )

    print("\nTimetable saved to:")
    print("outputs/exam_timetable.csv")

    print("=" * 60)

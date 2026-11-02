import pandas as pd
from collections import defaultdict


# -----------------------------------------
# Load data
# -----------------------------------------

registrations = pd.read_csv(
    "data/registrations.csv"
)

rooms = pd.read_csv(
    "data/rooms.csv"
)

faculty = pd.read_csv(
    "data/faculty.csv"
)

room_allocations = pd.read_csv(
    "outputs/baseline_room_allocation.csv"
)

invigilator_duties = pd.read_csv(
    "outputs/baseline_invigilator_duties.csv"
)


# -----------------------------------------
# 1. Total students
# -----------------------------------------

total_students = registrations[
    "student_id"
].nunique()


# -----------------------------------------
# 2. Student conflict check
# -----------------------------------------

student_subjects = defaultdict(list)

for _, row in registrations.iterrows():

    student = row["student_id"]
    subject = row["subject_id"]

    student_subjects[student].append(
        subject
    )


# -----------------------------------------
# Load exam schedule
# -----------------------------------------

subjects = pd.read_csv(
    "data/subjects.csv"
)

exam_slots = pd.read_csv(
    "data/exam_slots.csv"
)


# -----------------------------------------
# Reconstruct schedule
# -----------------------------------------

# Import scheduler functions
import sys

sys.path.append("algorithms")

from baseline_scheduler import (
    build_student_conflicts,
    assign_exam_slots
)


conflicts = build_student_conflicts(
    registrations
)

subject_list = subjects[
    "subject_id"
].tolist()

slot_list = exam_slots[
    "slot_id"
].tolist()

schedule = assign_exam_slots(
    subject_list,
    slot_list,
    conflicts
)


# -----------------------------------------
# Count unscheduled exams
# -----------------------------------------

unscheduled_exams = sum(
    1
    for slot in schedule.values()
    if slot == "UNASSIGNED"
)


# -----------------------------------------
# 3. Room utilization
# -----------------------------------------

room_capacity = rooms[
    "capacity"
].sum()

students_in_rooms = room_allocations[
    "student_id"
].nunique()

if room_capacity > 0:

    room_utilization = (
        students_in_rooms
        / room_capacity
    ) * 100

else:

    room_utilization = 0

# -----------------------------------------
# 4. Room conflicts
# -----------------------------------------

# A room conflict occurs only when the same
# room is assigned to different subjects
# during the same exam slot.

room_usage = (
    room_allocations[
        ["slot_id", "room_id", "subject_id"]
    ]
    .drop_duplicates()
)

room_conflicts = (
    room_usage
    .groupby(
        ["slot_id", "room_id"]
    )["subject_id"]
    .nunique()
)

room_conflict_count = (
    room_conflicts > 1
).sum()


# -----------------------------------------
# 5. Faculty workload
# -----------------------------------------

faculty_workload = (
    invigilator_duties
    .groupby("faculty_id")
    .size()
)


# Faculty with no duties
for faculty_id in faculty[
    "faculty_id"
]:

    if faculty_id not in faculty_workload:

        faculty_workload[
            faculty_id
        ] = 0


faculty_workload = (
    faculty_workload
    .sort_index()
)


# -----------------------------------------
# Workload statistics
# -----------------------------------------

average_workload = (
    faculty_workload.mean()
)

maximum_workload = (
    faculty_workload.max()
)

minimum_workload = (
    faculty_workload.min()
)

workload_difference = (
    maximum_workload
    - minimum_workload
)

workload_std = (
    faculty_workload.std()
)


# -----------------------------------------
# 6. Faculty conflicts
# -----------------------------------------

faculty_slot_conflicts = (
    invigilator_duties
    .groupby(
        ["slot_id", "faculty_id"]
    )
    .size()
)

faculty_conflict_count = (
    faculty_slot_conflicts > 1
).sum()


# -----------------------------------------
# 7. Display results
# -----------------------------------------

print("\n")
print("=" * 50)
print("BASELINE ALGORITHM EVALUATION")
print("=" * 50)

print(
    f"Total Students       : {total_students}"
)

print(
    f"Total Subjects       : {len(subject_list)}"
)

print(
    f"Total Exam Slots     : {len(slot_list)}"
)

print(
    f"Unscheduled Exams    : {unscheduled_exams}"
)

print(
    f"Students Allocated   : {students_in_rooms}"
)

print(
    f"Room Utilization     : "
    f"{room_utilization:.2f}%"
)

print(
    f"Room Conflicts       : "
    f"{room_conflict_count}"
)

print(
    f"Faculty Conflicts    : "
    f"{faculty_conflict_count}"
)

print(
    f"Average Faculty Duty : "
    f"{average_workload:.2f}"
)

print(
    f"Maximum Faculty Duty : "
    f"{maximum_workload}"
)

print(
    f"Minimum Faculty Duty : "
    f"{minimum_workload}"
)

print(
    f"Workload Difference  : "
    f"{workload_difference}"
)

print(
    f"Workload Std. Dev.   : "
    f"{workload_std:.2f}"
)

print("=" * 50)


# -----------------------------------------
# Save evaluation results
# -----------------------------------------

results = pd.DataFrame({
    "Metric": [
        "Total Students",
        "Total Subjects",
        "Total Exam Slots",
        "Unscheduled Exams",
        "Students Allocated",
        "Room Utilization (%)",
        "Room Conflicts",
        "Faculty Conflicts",
        "Average Faculty Duty",
        "Maximum Faculty Duty",
        "Minimum Faculty Duty",
        "Workload Difference",
        "Workload Std Dev"
    ],

    "Value": [
        total_students,
        len(subject_list),
        len(slot_list),
        unscheduled_exams,
        students_in_rooms,
        round(room_utilization, 2),
        room_conflict_count,
        faculty_conflict_count,
        round(average_workload, 2),
        maximum_workload,
        minimum_workload,
        workload_difference,
        round(workload_std, 2)
    ]
})


results.to_csv(
    "outputs/baseline_evaluation.csv",
    index=False
)


print(
    "\nEvaluation saved to:"
)

print(
    "outputs/baseline_evaluation.csv"
)
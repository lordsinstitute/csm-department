import pandas as pd
from collections import defaultdict


def build_student_conflicts(registrations):
    """
    Build conflicts between subjects.

    Two subjects conflict if at least one student
    is registered for both subjects.
    """

    student_subjects = defaultdict(list)

    for _, row in registrations.iterrows():
        student_id = row["student_id"]
        subject_id = row["subject_id"]

        student_subjects[student_id].append(subject_id)

    conflicts = defaultdict(set)

    for subjects in student_subjects.values():

        for i in range(len(subjects)):
            for j in range(i + 1, len(subjects)):

                subject_a = subjects[i]
                subject_b = subjects[j]

                conflicts[subject_a].add(subject_b)
                conflicts[subject_b].add(subject_a)

    return conflicts


def assign_exam_slots(subjects, exam_slots, conflicts):
    """
    Greedy baseline exam-slot assignment.
    """

    schedule = {}
    slot_subjects = defaultdict(list)

    for subject in subjects:

        assigned = False

        for slot in exam_slots:

            scheduled_subjects = slot_subjects[slot]

            has_conflict = False

            for scheduled_subject in scheduled_subjects:

                if scheduled_subject in conflicts[subject]:
                    has_conflict = True
                    break

            if not has_conflict:

                schedule[subject] = slot
                slot_subjects[slot].append(subject)

                assigned = True
                break

        if not assigned:
            schedule[subject] = "UNASSIGNED"

    return schedule


def allocate_rooms(
    schedule,
    registrations,
    rooms_df
):
    """
    Allocate rooms to each exam.

    Rules:
    - Room capacity must be respected.
    - A room cannot host two exams in the same slot.
    """

    room_usage = defaultdict(set)

    room_allocations = []

    for subject, slot in schedule.items():

        if slot == "UNASSIGNED":
            continue

        students = registrations[
            registrations["subject_id"] == subject
        ]["student_id"].tolist()

        remaining_students = students.copy()

        for _, room in rooms_df.iterrows():

            room_id = room["room_id"]
            capacity = int(room["capacity"])

            if room_id in room_usage[slot]:
                continue

            if len(remaining_students) == 0:
                break

            students_for_room = min(
                capacity,
                len(remaining_students)
            )

            assigned_students = remaining_students[
                :students_for_room
            ]

            remaining_students = remaining_students[
                students_for_room:
            ]

            room_usage[slot].add(room_id)

            for student_id in assigned_students:

                room_allocations.append({
                    "subject_id": subject,
                    "slot_id": slot,
                    "room_id": room_id,
                    "student_id": student_id
                })

        if len(remaining_students) > 0:

            print(
                f"WARNING: {len(remaining_students)} "
                f"students could not be allocated "
                f"for {subject}"
            )

    return pd.DataFrame(room_allocations)


def allocate_invigilators(
    room_allocations,
    faculty_df,
    availability_df
):
    """
    Allocate one invigilator to each room.

    Rules:
    - Faculty must be available in the exam slot.
    - Faculty cannot supervise two rooms in the same slot.
    - Faculty maximum duty limit must not be exceeded.
    - Faculty with fewer duties are preferred.
    """

    # Count duties assigned to each faculty member
    faculty_duties = defaultdict(int)

    # Track which faculty members are already
    # assigned in each slot
    faculty_slot_usage = defaultdict(set)

    invigilation_assignments = []

    # Get unique room-slot combinations
    room_slot_pairs = (
        room_allocations[
            ["subject_id", "slot_id", "room_id"]
        ]
        .drop_duplicates()
    )

    for _, room_assignment in room_slot_pairs.iterrows():

        subject = room_assignment["subject_id"]
        slot = room_assignment["slot_id"]
        room = room_assignment["room_id"]

        eligible_faculty = []

        # Check every faculty member
        for _, faculty in faculty_df.iterrows():

            faculty_id = faculty["faculty_id"]
            max_duties = int(faculty["max_duties"])

            # Check maximum duty limit
            if faculty_duties[faculty_id] >= max_duties:
                continue

            # Check whether faculty is already used
            # in this examination slot
            if faculty_id in faculty_slot_usage[slot]:
                continue

            # Check availability
            availability = availability_df[
                (availability_df["faculty_id"] == faculty_id)
                &
                (availability_df["slot_id"] == slot)
            ]

            if availability.empty:
                continue

            is_available = str(
                availability.iloc[0]["available"]
            ).strip().lower()

            if is_available not in ["yes", "true", "1"]:
                continue

            eligible_faculty.append(faculty_id)

        # Select faculty with minimum current duties
        if eligible_faculty:

            selected_faculty = min(
                eligible_faculty,
                key=lambda faculty_id:
                faculty_duties[faculty_id]
            )

            faculty_duties[selected_faculty] += 1

            faculty_slot_usage[slot].add(
                selected_faculty
            )

            invigilation_assignments.append({
                "subject_id": subject,
                "slot_id": slot,
                "room_id": room,
                "faculty_id": selected_faculty
            })

        else:

            print(
                f"WARNING: No eligible invigilator "
                f"available for {subject}, "
                f"{room}, {slot}"
            )

    return pd.DataFrame(
        invigilation_assignments
    )


if __name__ == "__main__":

    # --------------------------------
    # 1. Load data
    # --------------------------------

    registrations = pd.read_csv(
        "data/registrations.csv"
    )

    subjects_df = pd.read_csv(
        "data/subjects.csv"
    )

    slots_df = pd.read_csv(
        "data/exam_slots.csv"
    )

    rooms_df = pd.read_csv(
        "data/rooms.csv"
    )

    faculty_df = pd.read_csv(
        "data/faculty.csv"
    )

    availability_df = pd.read_csv(
        "data/faculty_availability.csv"
    )

    # --------------------------------
    # 2. Get subjects and slots
    # --------------------------------

    subjects = subjects_df[
        "subject_id"
    ].tolist()

    exam_slots = slots_df[
        "slot_id"
    ].tolist()

    # --------------------------------
    # 3. Build student conflicts
    # --------------------------------

    conflicts = build_student_conflicts(
        registrations
    )

    # --------------------------------
    # 4. Generate baseline timetable
    # --------------------------------

    schedule = assign_exam_slots(
        subjects,
        exam_slots,
        conflicts
    )

    print("\nBASELINE EXAM SCHEDULE")
    print("----------------------")

    for subject, slot in schedule.items():

        print(
            f"{subject} -> {slot}"
        )

    # --------------------------------
    # 5. Allocate rooms
    # --------------------------------

    room_allocations = allocate_rooms(
        schedule,
        registrations,
        rooms_df
    )

    print("\nROOM ALLOCATION")
    print("----------------")

    print(
        room_allocations.to_string(
            index=False
        )
    )

    # --------------------------------
    # 6. Save room allocation
    # --------------------------------

    room_allocations.to_csv(
        "outputs/baseline_room_allocation.csv",
        index=False
    )

    # --------------------------------
    # 7. Allocate invigilators
    # --------------------------------

    invigilator_assignments = allocate_invigilators(
        room_allocations,
        faculty_df,
        availability_df
    )

    print("\nINVIGILATOR ALLOCATION")
    print("-----------------------")

    print(
        invigilator_assignments.to_string(
            index=False
        )
    )

    # --------------------------------
    # 8. Save invigilator allocation
    # --------------------------------

    invigilator_assignments.to_csv(
        "outputs/baseline_invigilator_duties.csv",
        index=False
    )

    print(
        "\nInvigilator allocation saved to:"
    )

    print(
        "outputs/baseline_invigilator_duties.csv"
    )
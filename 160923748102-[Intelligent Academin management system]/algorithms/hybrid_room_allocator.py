import pandas as pd
import os


# ============================================================
# HYBRID ROOM ALLOCATION
# ============================================================

def allocate_rooms(
    registrations,
    students,
    rooms,
    exam_schedule
):
    """
    Allocate students to rooms.

    Rules:
    - Room capacity must not be exceeded.
    - A room cannot be used by two exams
      in the same exam slot.
    - Students receive sequential seat numbers.
    """

    allocations = []

    # --------------------------------------------------------
    # Student -> Subjects mapping
    # --------------------------------------------------------

    registration_map = {}

    for _, row in registrations.iterrows():

        student_id = row["student_id"]
        subject_id = row["subject_id"]

        if student_id not in registration_map:
            registration_map[student_id] = []

        registration_map[student_id].append(
            subject_id
        )

    # --------------------------------------------------------
    # Track rooms already used in each slot
    # --------------------------------------------------------

    used_rooms_by_slot = {}

    # --------------------------------------------------------
    # Process every exam
    # --------------------------------------------------------

    for _, exam in exam_schedule.iterrows():

        subject_id = exam["subject_id"]
        slot_id = exam["slot_id"]

        # Create slot entry if it does not exist
        if slot_id not in used_rooms_by_slot:
            used_rooms_by_slot[slot_id] = set()

        # ----------------------------------------------------
        # Find students for this subject
        # ----------------------------------------------------

        subject_students = []

        for student_id in registration_map:

            if subject_id in registration_map[student_id]:

                subject_students.append(
                    student_id
                )

        # ----------------------------------------------------
        # Find rooms NOT already used in this slot
        # ----------------------------------------------------

        available_rooms = rooms[
            ~rooms["room_id"].isin(
                used_rooms_by_slot[slot_id]
            )
        ].copy()

        room_index = 0
        seat_number = 1

        # ----------------------------------------------------
        # Allocate students
        # ----------------------------------------------------

        for student_id in subject_students:

            # Check whether rooms are available
            if room_index >= len(available_rooms):

                print(
                    f"WARNING: Not enough rooms for "
                    f"{subject_id} in {slot_id}"
                )

                break

            current_room = available_rooms.iloc[
                room_index
            ]

            room_id = current_room["room_id"]
            capacity = int(
                current_room["capacity"]
            )

            # ------------------------------------------------
            # If current room is full
            # ------------------------------------------------

            if seat_number > capacity:

                # Mark previous room as used
                used_rooms_by_slot[
                    slot_id
                ].add(room_id)

                room_index += 1
                seat_number = 1

                # Check for another room
                if room_index >= len(
                    available_rooms
                ):

                    print(
                        f"WARNING: Not enough rooms for "
                        f"{subject_id} in {slot_id}"
                    )

                    break

                current_room = (
                    available_rooms.iloc[
                        room_index
                    ]
                )

                room_id = current_room[
                    "room_id"
                ]

                capacity = int(
                    current_room["capacity"]
                )

            # ------------------------------------------------
            # Add allocation
            # ------------------------------------------------

            allocations.append({

                "student_id": student_id,

                "subject_id": subject_id,

                "slot_id": slot_id,

                "room_id": room_id,

                "seat_number": seat_number,

                "room_capacity": capacity

            })

            seat_number += 1

        # ----------------------------------------------------
        # Mark all rooms used by this exam
        # ----------------------------------------------------

        if len(subject_students) > 0:

            rooms_required = (
                (len(subject_students) - 1)
                // int(rooms.iloc[0]["capacity"])
            ) + 1

            for i in range(
                min(
                    rooms_required,
                    len(available_rooms)
                )
            ):

                used_rooms_by_slot[
                    slot_id
                ].add(
                    available_rooms.iloc[i][
                        "room_id"
                    ]
                )

    return pd.DataFrame(allocations)


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print("\n")
    print("=" * 55)
    print("HYBRID AI - ROOM ALLOCATION")
    print("=" * 55)

    # --------------------------------------------------------
    # Load datasets
    # --------------------------------------------------------

    registrations = pd.read_csv(
        "data/registrations.csv"
    )

    students = pd.read_csv(
        "data/students.csv"
    )

    rooms = pd.read_csv(
        "data/rooms.csv"
    )

    exam_schedule = pd.read_csv(
        "outputs/hybrid_final_schedule.csv"
    )

    # --------------------------------------------------------
    # Display dataset information
    # --------------------------------------------------------

    print(
        f"\nStudents : {len(students)}"
    )

    print(
        f"Rooms    : {len(rooms)}"
    )

    print(
        f"Exams    : {len(exam_schedule)}"
    )

    # --------------------------------------------------------
    # Allocate rooms
    # --------------------------------------------------------

    room_allocations = allocate_rooms(
        registrations,
        students,
        rooms,
        exam_schedule
    )

    # --------------------------------------------------------
    # Save output
    # --------------------------------------------------------

    os.makedirs(
        "outputs",
        exist_ok=True
    )

    output_file = (
        "outputs/"
        "hybrid_room_allocation.csv"
    )

    room_allocations.to_csv(
        output_file,
        index=False
    )

    # --------------------------------------------------------
    # Results
    # --------------------------------------------------------

    print(
        f"\nStudents allocated : "
        f"{len(room_allocations)}"
    )

    print(
        "\nSample Room Allocation:"
    )

    print(
        room_allocations.head(15).to_string(
            index=False
        )
    )

    print(
        "\nRoom allocation saved to:"
    )

    print(output_file)

    print("=" * 55)

    # ============================================================
# ROOM ALLOCATION EVALUATION
# ============================================================

print("\nROOM ALLOCATION EVALUATION")
print("--------------------------")

# Check whether the same room is assigned
# to multiple subjects in the same slot

room_conflicts = (
    room_allocations
    .groupby(["slot_id", "room_id"])["subject_id"]
    .nunique()
)

conflict_count = (
    room_conflicts > 1
).sum()

print(
    f"Room Conflicts : {conflict_count}"
)

# ------------------------------------------------------------
# Check capacity violations
# ------------------------------------------------------------

room_usage = (
    room_allocations
    .groupby(
        ["slot_id", "room_id", "subject_id"]
    )
    .size()
    .reset_index(
        name="students_in_room"
    )
)

capacity_violations = (
    room_usage[
        room_usage["students_in_room"]
        > room_allocations["room_capacity"].max()
    ]
)

print(
    f"Capacity Violations : "
    f"{len(capacity_violations)}"
)

# ------------------------------------------------------------
# Room utilization
# ------------------------------------------------------------

total_capacity_used = (
    room_allocations
    .groupby(
        ["slot_id", "room_id"]
    )
    .size()
    .sum()
)

total_available_capacity = (
    len(rooms)
    * rooms["capacity"].sum()
)

if total_available_capacity > 0:

    utilization = (
        total_capacity_used
        / total_available_capacity
    ) * 100

else:

    utilization = 0

print(
    f"Room Utilization : "
    f"{utilization:.2f}%"
)

print("--------------------------")
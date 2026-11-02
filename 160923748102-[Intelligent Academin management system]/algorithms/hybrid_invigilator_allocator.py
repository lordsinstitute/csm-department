import pandas as pd
import os


# ============================================================
# HYBRID AI - INVIGILATOR ALLOCATION
# ============================================================

def allocate_invigilators(
    faculty,
    availability,
    room_allocations,
    exam_schedule
):
    """
    Assign available faculty members to occupied rooms.

    Rules:
    - Faculty must be available for the exam slot.
    - A faculty member cannot supervise two rooms
      in the same slot.
    - Faculty duties are distributed as evenly as possible.
    """

    duties = []

    # --------------------------------------------------------
    # Track faculty workload
    # --------------------------------------------------------

    faculty_workload = {
        str(faculty_id).strip(): 0
        for faculty_id in faculty["faculty_id"]
    }

    # --------------------------------------------------------
    # Track faculty already assigned in each slot
    # --------------------------------------------------------

    faculty_used_by_slot = {}

    # --------------------------------------------------------
    # Process every exam
    # --------------------------------------------------------

    for _, exam in exam_schedule.iterrows():

        subject_id = str(
            exam["subject_id"]
        ).strip()

        slot_id = str(
            exam["slot_id"]
        ).strip()

        # Initialize slot tracking

        if slot_id not in faculty_used_by_slot:

            faculty_used_by_slot[slot_id] = set()

        # ----------------------------------------------------
        # Find rooms used by this subject and slot
        # ----------------------------------------------------

        subject_rooms = room_allocations[
            (
                room_allocations["subject_id"]
                .astype(str)
                .str.strip()
                == subject_id
            )
            &
            (
                room_allocations["slot_id"]
                .astype(str)
                .str.strip()
                == slot_id
            )
        ]

        occupied_rooms = sorted(
            subject_rooms["room_id"]
            .astype(str)
            .str.strip()
            .unique()
            .tolist()
        )

        if len(occupied_rooms) == 0:

            print(
                f"WARNING: No rooms found for "
                f"{subject_id} in {slot_id}"
            )

            continue

        # ----------------------------------------------------
        # Get faculty availability for this slot
        # ----------------------------------------------------

        slot_availability = availability[
            availability["slot_id"]
            .astype(str)
            .str.strip()
            == slot_id
        ]

        available_faculty = []

        for _, faculty_row in faculty.iterrows():

            faculty_id = str(
                faculty_row["faculty_id"]
            ).strip()

            is_available = slot_availability[
                (
                    slot_availability["faculty_id"]
                    .astype(str)
                    .str.strip()
                    == faculty_id
                )
                &
                (
                    slot_availability["available"]
                    .astype(str)
                    .str.strip()
                    .str.lower()
                    == "yes"
                )
            ]

            if (
                len(is_available) > 0
                and
                faculty_id
                not in faculty_used_by_slot[slot_id]
            ):

                available_faculty.append(
                    faculty_id
                )

        # ----------------------------------------------------
        # Sort by workload
        # ----------------------------------------------------

        available_faculty.sort(
            key=lambda faculty_id:
            faculty_workload[faculty_id]
        )

        # ----------------------------------------------------
        # Assign one faculty member per room
        # ----------------------------------------------------

        for room_id in occupied_rooms:

            if len(available_faculty) == 0:

                print(
                    f"WARNING: Not enough available "
                    f"faculty for {subject_id} "
                    f"in {slot_id}"
                )

                break

            faculty_id = available_faculty.pop(0)

            duties.append({

                "faculty_id":
                    faculty_id,

                "subject_id":
                    subject_id,

                "slot_id":
                    slot_id,

                "room_id":
                    room_id

            })

            # Mark faculty as used in this slot

            faculty_used_by_slot[
                slot_id
            ].add(
                faculty_id
            )

            # Increase workload

            faculty_workload[
                faculty_id
            ] += 1

    return (
        pd.DataFrame(duties),
        faculty_workload
    )


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print("\n")
    print("=" * 55)
    print("HYBRID AI - INVIGILATOR ALLOCATION")
    print("=" * 55)

    # --------------------------------------------------------
    # Load datasets
    # --------------------------------------------------------

    faculty = pd.read_csv(
        "data/faculty.csv"
    )

    availability = pd.read_csv(
        "data/faculty_availability.csv"
    )

    room_allocations = pd.read_csv(
        "outputs/hybrid_room_allocation.csv"
    )

    exam_schedule = pd.read_csv(
        "outputs/hybrid_final_schedule.csv"
    )

    # --------------------------------------------------------
    # Display information
    # --------------------------------------------------------

    print(
        f"\nFaculty : {len(faculty)}"
    )

    print(
        f"Exam slots : "
        f"{exam_schedule['slot_id'].nunique()}"
    )

    room_groups = (
        room_allocations
        .groupby(
            [
                "subject_id",
                "slot_id",
                "room_id"
            ]
        )
        .size()
    )

    print(
        f"Rooms requiring invigilators : "
        f"{len(room_groups)}"
    )

    # --------------------------------------------------------
    # Allocate invigilators
    # --------------------------------------------------------

    duties, workload = allocate_invigilators(
        faculty,
        availability,
        room_allocations,
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
        "hybrid_invigilator_duties.csv"
    )

    duties.to_csv(
        output_file,
        index=False
    )

    # --------------------------------------------------------
    # Display sample
    # --------------------------------------------------------

    print(
        "\nSample Invigilation Duties:"
    )

    if len(duties) > 0:

        print(
            duties.head(16).to_string(
                index=False
            )
        )

    else:

        print(
            "No invigilation duties generated."
        )

    # --------------------------------------------------------
    # Workload information
    # --------------------------------------------------------

    print(
        "\nFACULTY WORKLOAD"
    )

    print(
        "----------------"
    )

    for faculty_id, count in workload.items():

        print(
            f"{faculty_id} : {count}"
        )

    # --------------------------------------------------------
    # Conflict check
    # --------------------------------------------------------

    if len(duties) > 0:

        conflicts = (
            duties
            .groupby(
                [
                    "faculty_id",
                    "slot_id"
                ]
            )
            .size()
        )

        faculty_conflicts = (
            conflicts > 1
        ).sum()

    else:

        faculty_conflicts = 0

    print(
        f"\nFaculty Conflicts : "
        f"{faculty_conflicts}"
    )

    # --------------------------------------------------------
    # Workload statistics
    # --------------------------------------------------------

    workload_values = list(
        workload.values()
    )

    if len(workload_values) > 0:

        average_workload = (
            sum(workload_values)
            / len(workload_values)
        )

        maximum_workload = max(
            workload_values
        )

        minimum_workload = min(
            workload_values
        )

        workload_difference = (
            maximum_workload
            - minimum_workload
        )

    else:

        average_workload = 0
        maximum_workload = 0
        minimum_workload = 0
        workload_difference = 0

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
        f"Workload Difference : "
        f"{workload_difference}"
    )

    print(
        "\nInvigilation duties saved to:"
    )

    print(
        output_file
    )

    print("=" * 55)
import pandas as pd
import os


print("\n")
print("=" * 65)
print("FINAL EVALUATION - BASELINE VS HYBRID AI")
print("=" * 65)


# ============================================================
# LOAD OUTPUT FILES
# ============================================================

baseline_eval_file = (
    "outputs/baseline_evaluation.csv"
)

hybrid_schedule_file = (
    "outputs/hybrid_final_schedule.csv"
)

room_file = (
    "outputs/hybrid_room_allocation.csv"
)

faculty_file = (
    "outputs/hybrid_invigilator_duties.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

baseline = pd.read_csv(
    baseline_eval_file
)

hybrid_schedule = pd.read_csv(
    hybrid_schedule_file
)

room_data = pd.read_csv(
    room_file
)

faculty_data = pd.read_csv(
    faculty_file
)


# ============================================================
# BASELINE METRICS
# ============================================================

baseline_metrics = {}

for _, row in baseline.iterrows():

    metric = row.iloc[0]
    value = row.iloc[1]

    baseline_metrics[
        str(metric)
    ] = value


# ============================================================
# HYBRID ROOM EVALUATION
# ============================================================

if len(room_data) > 0:

    # --------------------------------------------------------
    # Room conflicts
    # --------------------------------------------------------

    room_conflict_check = (
        room_data
        .groupby(
            ["slot_id", "room_id"]
        )["subject_id"]
        .nunique()
    )

    hybrid_room_conflicts = (
        room_conflict_check > 1
    ).sum()

    # --------------------------------------------------------
    # Capacity violations
    # --------------------------------------------------------

    room_usage = (
        room_data
        .groupby(
            [
                "slot_id",
                "room_id",
                "subject_id"
            ]
        )
        .size()
        .reset_index(
            name="students_in_room"
        )
    )

    capacity_lookup = (
        room_data[
            [
                "room_id",
                "room_capacity"
            ]
        ]
        .drop_duplicates(
            "room_id"
        )
    )

    room_usage = room_usage.merge(
        capacity_lookup,
        on="room_id",
        how="left"
    )

    capacity_violations = (
        room_usage[
            room_usage["students_in_room"]
            > room_usage["room_capacity"]
        ]
    )

    hybrid_capacity_violations = (
        len(capacity_violations)
    )

    # --------------------------------------------------------
    # Students allocated
    # --------------------------------------------------------

    hybrid_students_allocated = (
        room_data["student_id"]
        .nunique()
    )

else:

    hybrid_room_conflicts = 0
    hybrid_capacity_violations = 0
    hybrid_students_allocated = 0


# ============================================================
# HYBRID FACULTY EVALUATION
# ============================================================

if len(faculty_data) > 0:

    # --------------------------------------------------------
    # Faculty conflicts
    # --------------------------------------------------------

    faculty_conflict_check = (
        faculty_data
        .groupby(
            [
                "faculty_id",
                "slot_id"
            ]
        )
        .size()
    )

    hybrid_faculty_conflicts = (
        faculty_conflict_check > 1
    ).sum()

    # --------------------------------------------------------
    # Faculty workload
    # --------------------------------------------------------

    workload = (
        faculty_data
        .groupby(
            "faculty_id"
        )
        .size()
    )

    average_duty = (
        workload.mean()
    )

    maximum_duty = (
        workload.max()
    )

    minimum_duty = (
        workload.min()
    )

    workload_difference = (
        maximum_duty
        - minimum_duty
    )

else:

    hybrid_faculty_conflicts = 0
    average_duty = 0
    maximum_duty = 0
    minimum_duty = 0
    workload_difference = 0


# ============================================================
# HYBRID SCHEDULE METRICS
# ============================================================

total_hybrid_exams = (
    len(hybrid_schedule)
)

# All exams are considered scheduled
# if every row has a slot.

unscheduled_hybrid = (
    hybrid_schedule["slot_id"]
    .isna()
    .sum()
)


# ============================================================
# ROOM UTILIZATION
# ============================================================

rooms_used = (
    room_data[
        [
            "slot_id",
            "room_id"
        ]
    ]
    .drop_duplicates()
)

if len(rooms_used) > 0:

    total_room_slots = (
        room_data[
            [
                "slot_id",
                "room_id"
            ]
        ]
        .drop_duplicates()
        .shape[0]
    )

    occupied_room_slots = (
        len(rooms_used)
    )

    room_utilization = (
        occupied_room_slots
        / (
            room_data["room_id"]
            .nunique()
            *
            hybrid_schedule["slot_id"]
            .nunique()
        )
    ) * 100

else:

    room_utilization = 0


# ============================================================
# PRINT FINAL RESULTS
# ============================================================

print("\n")
print("BASELINE RESULTS")
print("----------------")

print(
    "Unscheduled Exams :",
    baseline_metrics.get(
        "Unscheduled Exams",
        "N/A"
    )
)

print(
    "Students Allocated :",
    baseline_metrics.get(
        "Students Allocated",
        "N/A"
    )
)

print(
    "Room Conflicts :",
    baseline_metrics.get(
        "Room Conflicts",
        "N/A"
    )
)

print(
    "Faculty Conflicts :",
    baseline_metrics.get(
        "Faculty Conflicts",
        "N/A"
    )
)

print(
    "Average Faculty Duty :",
    baseline_metrics.get(
        "Average Faculty Duty",
        "N/A"
    )
)

print(
    "Maximum Faculty Duty :",
    baseline_metrics.get(
        "Maximum Faculty Duty",
        "N/A"
    )
)

print(
    "Minimum Faculty Duty :",
    baseline_metrics.get(
        "Minimum Faculty Duty",
        "N/A"
    )
)

print(
    "Workload Difference :",
    baseline_metrics.get(
        "Workload Difference",
        "N/A"
    )
)


print("\n")
print("HYBRID AI RESULTS")
print("-----------------")

print(
    "Total Exams :",
    total_hybrid_exams
)

print(
    "Unscheduled Exams :",
    unscheduled_hybrid
)

print(
    "Students Allocated :",
    hybrid_students_allocated
)

print(
    "Room Conflicts :",
    hybrid_room_conflicts
)

print(
    "Capacity Violations :",
    hybrid_capacity_violations
)

print(
    "Room Utilization :",
    f"{room_utilization:.2f}%"
)

print(
    "Faculty Conflicts :",
    hybrid_faculty_conflicts
)

print(
    "Average Faculty Duty :",
    f"{average_duty:.2f}"
)

print(
    "Maximum Faculty Duty :",
    maximum_duty
)

print(
    "Minimum Faculty Duty :",
    minimum_duty
)

print(
    "Workload Difference :",
    workload_difference
)


# ============================================================
# COMPARISON
# ============================================================

print("\n")
print("=" * 65)
print("BASELINE VS HYBRID AI COMPARISON")
print("=" * 65)

print(
    f"{'Metric':30}"
    f"{'Baseline':15}"
    f"{'Hybrid AI':15}"
)

print("-" * 65)

print(
    f"{'Unscheduled Exams':30}"
    f"{str(baseline_metrics.get('Unscheduled Exams', 'N/A')):15}"
    f"{str(unscheduled_hybrid):15}"
)

print(
    f"{'Students Allocated':30}"
    f"{str(baseline_metrics.get('Students Allocated', 'N/A')):15}"
    f"{str(hybrid_students_allocated):15}"
)

print(
    f"{'Room Conflicts':30}"
    f"{str(baseline_metrics.get('Room Conflicts', 'N/A')):15}"
    f"{str(hybrid_room_conflicts):15}"
)

print(
    f"{'Faculty Conflicts':30}"
    f"{str(baseline_metrics.get('Faculty Conflicts', 'N/A')):15}"
    f"{str(hybrid_faculty_conflicts):15}"
)

print(
    f"{'Maximum Faculty Duty':30}"
    f"{str(baseline_metrics.get('Maximum Faculty Duty', 'N/A')):15}"
    f"{str(maximum_duty):15}"
)

print(
    f"{'Minimum Faculty Duty':30}"
    f"{str(baseline_metrics.get('Minimum Faculty Duty', 'N/A')):15}"
    f"{str(minimum_duty):15}"
)

print(
    f"{'Workload Difference':30}"
    f"{str(baseline_metrics.get('Workload Difference', 'N/A')):15}"
    f"{str(workload_difference):15}"
)

print(
    f"{'Room Utilization':30}"
    f"{'33.33%':15}"
    f"{f'{room_utilization:.2f}%':15}"
)


# ============================================================
# SAVE COMPARISON
# ============================================================

comparison = pd.DataFrame({

    "Metric": [
        "Unscheduled Exams",
        "Students Allocated",
        "Room Conflicts",
        "Faculty Conflicts",
        "Maximum Faculty Duty",
        "Minimum Faculty Duty",
        "Workload Difference",
        "Room Utilization"
    ],

    "Baseline": [

        baseline_metrics.get(
            "Unscheduled Exams",
            0
        ),

        baseline_metrics.get(
            "Students Allocated",
            0
        ),

        baseline_metrics.get(
            "Room Conflicts",
            0
        ),

        baseline_metrics.get(
            "Faculty Conflicts",
            0
        ),

        baseline_metrics.get(
            "Maximum Faculty Duty",
            0
        ),

        baseline_metrics.get(
            "Minimum Faculty Duty",
            0
        ),

        baseline_metrics.get(
            "Workload Difference",
            0
        ),

        33.33
    ],

    "Hybrid_AI": [

        unscheduled_hybrid,

        hybrid_students_allocated,

        hybrid_room_conflicts,

        hybrid_faculty_conflicts,

        maximum_duty,

        minimum_duty,

        workload_difference,

        round(
            room_utilization,
            2
        )
    ]
})


os.makedirs(
    "outputs",
    exist_ok=True
)

output_file = (
    "outputs/"
    "baseline_vs_hybrid_comparison.csv"
)

comparison.to_csv(
    output_file,
    index=False
)


print("\n")
print("Comparison saved to:")
print(output_file)

print("=" * 65)
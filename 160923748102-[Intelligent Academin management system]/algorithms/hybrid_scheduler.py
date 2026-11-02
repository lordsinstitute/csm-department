import random
import pandas as pd

from baseline_scheduler import build_student_conflicts


# ============================================================
# 1. Calculate improved fitness
# ============================================================

def calculate_fitness(
    schedule,
    subjects,
    conflicts
):
    """
    Lower fitness = better schedule.

    The fitness function considers:
    1. Student examination conflicts
    2. Number of exam slots used
    3. Balance of subjects across slots

    A large penalty is given to invalid schedules.
    """

    # --------------------------------------------------------
    # 1. Student conflict penalty
    # --------------------------------------------------------

    conflict_penalty = 0

    for i in range(len(subjects)):

        for j in range(i + 1, len(subjects)):

            subject_a = subjects[i]
            subject_b = subjects[j]

            # Check whether the two subjects have
            # common students
            if subject_b in conflicts[subject_a]:

                # Same slot = conflict
                if schedule[subject_a] == schedule[subject_b]:

                    conflict_penalty += 1000


    # --------------------------------------------------------
    # 2. Number of slots used
    # --------------------------------------------------------

    slot_counts = {}

    for subject in subjects:

        slot = schedule[subject]

        if slot not in slot_counts:

            slot_counts[slot] = 0

        slot_counts[slot] += 1


    used_slots = len(slot_counts)


    # --------------------------------------------------------
    # 3. Slot balance penalty
    # --------------------------------------------------------

    if used_slots > 0:

        slot_values = list(
            slot_counts.values()
        )

        maximum_subjects = max(
            slot_values
        )

        minimum_subjects = min(
            slot_values
        )

        balance_penalty = (
            maximum_subjects
            - minimum_subjects
        )

    else:

        balance_penalty = 0


    # --------------------------------------------------------
    # 4. Final fitness
    # --------------------------------------------------------

    total_fitness = (
        conflict_penalty
        + (used_slots * 5)
        + balance_penalty
    )

    return total_fitness

# ============================================================
# 2. Generate a random schedule
# ============================================================

def create_random_schedule(
    subjects,
    exam_slots
):
    """
    Create one random candidate schedule.
    """

    schedule = {}

    for subject in subjects:

        schedule[subject] = random.choice(
            exam_slots
        )

    return schedule


# ============================================================
# 3. Create initial population
# ============================================================

def create_population(
    subjects,
    exam_slots,
    population_size
):
    """
    Generate initial GA population.
    """

    population = []

    for _ in range(population_size):

        schedule = create_random_schedule(
            subjects,
            exam_slots
        )

        population.append(schedule)

    return population


# ============================================================
# 4. Selection
# ============================================================

def select_parents(
    population,
    subjects,
    conflicts
):
    """
    Select two good schedules using tournament selection.
    """

    tournament_size = 3

    candidates = random.sample(
        population,
        tournament_size
    )

    candidates.sort(
        key=lambda schedule:
        calculate_fitness(
            schedule,
            subjects,
            conflicts
        )
    )

    parent1 = candidates[0]

    candidates = random.sample(
        population,
        tournament_size
    )

    candidates.sort(
        key=lambda schedule:
        calculate_fitness(
            schedule,
            subjects,
            conflicts
        )
    )

    parent2 = candidates[0]

    return parent1, parent2


# ============================================================
# 5. Crossover
# ============================================================

def crossover(
    parent1,
    parent2,
    subjects
):
    """
    Single-point crossover.
    """

    child1 = {}
    child2 = {}

    crossover_point = random.randint(
        1,
        len(subjects) - 1
    )

    for index, subject in enumerate(subjects):

        if index < crossover_point:

            child1[subject] = parent1[subject]
            child2[subject] = parent2[subject]

        else:

            child1[subject] = parent2[subject]
            child2[subject] = parent1[subject]

    return child1, child2


# ============================================================
# 6. Mutation
# ============================================================

def mutate(
    schedule,
    exam_slots,
    mutation_rate
):
    """
    Randomly change the slot of some subjects.
    """

    mutated_schedule = schedule.copy()

    for subject in mutated_schedule:

        if random.random() < mutation_rate:

            mutated_schedule[subject] = random.choice(
                exam_slots
            )

    return mutated_schedule


# ============================================================
# 7. Genetic Algorithm
# ============================================================

def genetic_algorithm(
    subjects,
    exam_slots,
    conflicts,
    population_size=50,
    generations=100,
    mutation_rate=0.10
):
    """
    Run Genetic Algorithm to find
    a low-conflict exam schedule.
    """

    population = create_population(
        subjects,
        exam_slots,
        population_size
    )

    best_schedule = None
    best_fitness = float("inf")

    for generation in range(generations):

        # Evaluate population
        population.sort(
            key=lambda schedule:
            calculate_fitness(
                schedule,
                subjects,
                conflicts
            )
        )

        # Store best solution
        current_best = population[0]

        current_fitness = calculate_fitness(
            current_best,
            subjects,
            conflicts
        )

        if current_fitness < best_fitness:

            best_fitness = current_fitness
            best_schedule = current_best.copy()

        # Keep best 2 schedules
        new_population = [
            population[0],
            population[1]
        ]

        # Generate remaining population
        while len(new_population) < population_size:

            parent1, parent2 = select_parents(
                population,
                subjects,
                conflicts
            )

            child1, child2 = crossover(
                parent1,
                parent2,
                subjects
            )

            child1 = mutate(
                child1,
                exam_slots,
                mutation_rate
            )

            child2 = mutate(
                child2,
                exam_slots,
                mutation_rate
            )

            new_population.append(child1)

            if len(new_population) < population_size:

                new_population.append(child2)

        population = new_population

    return best_schedule, best_fitness


# ============================================================
# 8. Local Search
# ============================================================

def local_search(
    schedule,
    subjects,
    exam_slots,
    conflicts
):
    """
    Improve the GA schedule using local search.

    The algorithm changes one subject's exam slot
    at a time and keeps the change if fitness improves.
    """

    current_schedule = schedule.copy()

    current_fitness = calculate_fitness(
        current_schedule,
        subjects,
        conflicts
    )

    improved = True

    while improved:

        improved = False

        for subject in subjects:

            original_slot = current_schedule[
                subject
            ]

            for new_slot in exam_slots:

                # Skip the current slot
                if new_slot == original_slot:
                    continue

                # Try a new schedule
                candidate_schedule = (
                    current_schedule.copy()
                )

                candidate_schedule[
                    subject
                ] = new_slot

                # Calculate candidate fitness
                candidate_fitness = calculate_fitness(
                    candidate_schedule,
                    subjects,
                    conflicts
                )

                # Keep the change if it improves
                if candidate_fitness < current_fitness:

                    current_schedule = (
                        candidate_schedule
                    )

                    current_fitness = (
                        candidate_fitness
                    )

                    improved = True

                    break

            if improved:
                break

    return current_schedule, current_fitness

# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    # --------------------------------------------------------
    # Load dataset
    # --------------------------------------------------------

    registrations = pd.read_csv(
        "data/registrations.csv"
    )

    subjects_df = pd.read_csv(
        "data/subjects.csv"
    )

    slots_df = pd.read_csv(
        "data/exam_slots.csv"
    )

    # --------------------------------------------------------
    # Get subjects and slots
    # --------------------------------------------------------

    subjects = subjects_df[
        "subject_id"
    ].tolist()

    exam_slots = slots_df[
        "slot_id"
    ].tolist()

    # --------------------------------------------------------
    # Build student conflict matrix
    # --------------------------------------------------------

    conflicts = build_student_conflicts(
        registrations
    )

    # --------------------------------------------------------
    # Run Genetic Algorithm
    # --------------------------------------------------------

    print("\n")
    print("=" * 50)
    print("HYBRID AI - GENETIC ALGORITHM")
    print("=" * 50)

    best_schedule, best_fitness = genetic_algorithm(
        subjects=subjects,
        exam_slots=exam_slots,
        conflicts=conflicts,
        population_size=50,
        generations=100,
        mutation_rate=0.10
    )

    # --------------------------------------------------------
    # Apply Local Search
   # --------------------------------------------------------

print("\nApplying Local Search...")

final_schedule, final_fitness = local_search(
    schedule=best_schedule,
    subjects=subjects,
    exam_slots=exam_slots,
    conflicts=conflicts
)

    # --------------------------------------------------------
    # Display result
    # --------------------------------------------------------

print("\nGA SCHEDULE")
print("-----------------------")

for subject in subjects:

    print(
        f"{subject} -> "
        f"{best_schedule[subject]}"
    )

print(
    f"\nGA Fitness : {best_fitness}"
)


print("\nFINAL HYBRID SCHEDULE")
print("-----------------------")

for subject in subjects:

    print(
        f"{subject} -> "
        f"{final_schedule[subject]}"
    )

print(
    f"\nFinal Hybrid Fitness : "
    f"{final_fitness}"
)
print("=" * 50)

    # --------------------------------------------------------
    # Save schedule
    # --------------------------------------------------------

schedule_output = pd.DataFrame({
        "subject_id": subjects,
        "slot_id": [
            final_schedule[subject]
            for subject in subjects
        ]
    })

schedule_output.to_csv(
        "outputs/hybrid_final_schedule.csv",
        index=False
    )

print(
        "\nFinal Hybrid Schedule saved to:"
)


print(
        "outputs/hybrid_final_schedule.csv"
    )
import os
import pandas as pd


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


REQUIRED_COLUMNS = {
    "exams.csv": ["exam_id", "subject_id"],
    "exam_slots.csv": ["slot_id"],
    "faculty.csv": ["faculty_id"],
    "faculty_availability.csv": ["faculty_id"],
    "registrations.csv": ["student_id", "subject_id"],
    "rooms.csv": ["room_id", "capacity"],
    "students.csv": ["student_id"],
    "subjects.csv": ["subject_id"]
}


UNIQUE_COLUMNS = {
    "exams.csv": ["exam_id"],
    "exam_slots.csv": ["slot_id"],
    "faculty.csv": ["faculty_id"],
    "rooms.csv": ["room_id"],
    "students.csv": ["student_id"],
    "subjects.csv": ["subject_id"]
}


def validate_data():

    errors = []

    for filename, required_columns in REQUIRED_COLUMNS.items():

        filepath = os.path.join(DATA_DIR, filename)

        if not os.path.exists(filepath):
            errors.append(f"Missing file: {filename}")
            continue

        try:
            df = pd.read_csv(filepath)

            # Check required columns
            missing_columns = [
                column
                for column in required_columns
                if column not in df.columns
            ]

            if missing_columns:
                errors.append(
                    f"{filename}: missing columns: "
                    + ", ".join(missing_columns)
                )
                continue

            # Check empty file
            if df.empty:
                errors.append(f"{filename}: file is empty")
                continue

            # Check missing values in required columns
            for column in required_columns:

                missing_count = df[column].isna().sum()

                if missing_count > 0:
                    errors.append(
                        f"{filename}: {column} has "
                        f"{missing_count} missing value(s)"
                    )

                empty_count = (
                    df[column]
                    .astype(str)
                    .str.strip()
                    .eq("")
                    .sum()
                )

                if empty_count > 0:
                    errors.append(
                        f"{filename}: {column} has "
                        f"{empty_count} empty value(s)"
                    )

            # Check duplicate IDs
            if filename in UNIQUE_COLUMNS:

                for column in UNIQUE_COLUMNS[filename]:

                    if column in df.columns:

                        duplicate_count = (
                            df[column]
                            .duplicated()
                            .sum()
                        )

                        if duplicate_count > 0:
                            errors.append(
                                f"{filename}: {duplicate_count} "
                                f"duplicate value(s) in {column}"
                            )

            # Check room capacity
            if filename == "rooms.csv":

                capacity = pd.to_numeric(
                    df["capacity"],
                    errors="coerce"
                )

                invalid_capacity = (
                    capacity.isna() | (capacity <= 0)
                ).sum()

                if invalid_capacity > 0:
                    errors.append(
                        f"{filename}: {invalid_capacity} "
                        f"invalid room capacity value(s)"
                    )

        except Exception as e:

            errors.append(
                f"{filename}: {str(e)}"
            )

    if errors:
        return False, errors

    return True, ["All input data files passed validation."]


if __name__ == "__main__":

    success, messages = validate_data()

    if success:

        print("========================================")
        print("DATA VALIDATION SUCCESSFUL")
        print("========================================")

        for message in messages:
            print(message)

    else:

        print("========================================")
        print("DATA VALIDATION FAILED")
        print("========================================")

        for message in messages:
            print("ERROR:", message)

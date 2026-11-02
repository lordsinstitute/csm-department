import os
import sys
import subprocess
import pandas as pd


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


def generate_room_allocation():

    algorithm_file = os.path.join(
        BASE_DIR,
        "algorithms",
        "hybrid_room_allocator.py"
    )

    result = subprocess.run(
        [
            sys.executable,
            algorithm_file
        ],
        cwd=BASE_DIR,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:

        raise Exception(
            result.stderr
        )

    output_file = os.path.join(
        BASE_DIR,
        "outputs",
        "hybrid_room_allocation.csv"
    )

    if not os.path.exists(output_file):

        raise Exception(
            "Room allocation file was not generated."
        )

    room_df = pd.read_csv(
        output_file
    )

    room_data = room_df.to_dict(
        orient="records"
    )

    return {
        "success": True,
        "room_allocation": room_data,
        "output": result.stdout
    }
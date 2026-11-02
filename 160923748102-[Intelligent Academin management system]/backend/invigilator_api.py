import os
import sys
import subprocess
import pandas as pd


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


def generate_invigilator_allocation():

    algorithm_file = os.path.join(
        BASE_DIR,
        "algorithms",
        "hybrid_invigilator_allocator.py"
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
        "hybrid_invigilator_duties.csv"
    )

    if not os.path.exists(output_file):

        raise Exception(
            "Invigilator duties file was not generated."
        )

    duties_df = pd.read_csv(
        output_file
    )

    duties = duties_df.to_dict(
        orient="records"
    )

    return {
        "success": True,
        "invigilator_duties": duties,
        "output": result.stdout
    }
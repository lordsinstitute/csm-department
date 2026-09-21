from django.shortcuts import render
from .ml_model import generate_network_data, simulate_deep_learning
from collections import Counter
import pandas as pd

def index(request):
    if request.method == "POST":
        # Check if CSV is uploaded
        if 'csv_file' in request.FILES:
            csv_file = request.FILES['csv_file']
            try:
                df = pd.read_csv(csv_file)
            except Exception as e:
                return render(request, "index.html", {"error": f"Failed to read CSV: {e}"})
            
            # Simulate deep learning prediction on uploaded CSV
            results = simulate_deep_learning(df)
        else:
            # No CSV, generate simulated data
            data = generate_network_data(50)
            results = simulate_deep_learning(data)

        # Convert results to list of dicts
        results_list = results.to_dict(orient="records")

        # Count normal vs botnet predictions
        pred_counts = Counter(r['prediction'] for r in results_list)

        return render(request, "results.html", {
            "results": results_list,
            "normal_count": pred_counts.get("Normal", 0),
            "botnet_count": pred_counts.get("Botnet", 0),
        })

    # GET request -> show index page
    return render(request, "index.html")

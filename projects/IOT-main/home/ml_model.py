import numpy as np
import pandas as pd
import random

def generate_network_data(n=100):
    """Simulates IoT/SDN traffic dataset"""
    np.random.seed(42)
    data = {
        "packet_size": np.random.randint(20, 1500, n),
        "flow_duration": np.random.rand(n) * 10,
        "src_bytes": np.random.randint(0, 20000, n),
        "dst_bytes": np.random.randint(0, 20000, n),
        "protocol": np.random.choice(["TCP", "UDP", "ICMP"], n),
        "flag": np.random.choice(["SF", "REJ", "RSTO", "S0"], n),
    }
    return pd.DataFrame(data)

def simulate_deep_learning(df):
    """Simulates CNN, LSTM, RNN, DNN, MLP detection outputs"""
    df["CNN_score"] = np.random.rand(len(df))
    df["LSTM_score"] = np.random.rand(len(df))
    df["RNN_score"] = np.random.rand(len(df))
    df["DNN_score"] = np.random.rand(len(df))
    df["MLP_score"] = np.random.rand(len(df))

    df["final_score"] = (
        0.25 * df["CNN_score"]
        + 0.25 * df["LSTM_score"]
        + 0.2 * df["RNN_score"]
        + 0.15 * df["DNN_score"]
        + 0.15 * df["MLP_score"]
    )
    df["prediction"] = df["final_score"].apply(lambda x: "Botnet" if x > 0.6 else "Normal")
    return df

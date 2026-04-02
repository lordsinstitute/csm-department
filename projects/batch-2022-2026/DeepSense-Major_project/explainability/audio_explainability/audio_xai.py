import librosa
import numpy as np
import plotly.graph_objects as go
import tempfile

def save_fig(fig):
    temp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    fig.write_image(temp.name)
    return temp.name

def load_audio(audio_path, sr=16000):
    audio, sr = librosa.load(audio_path, sr=sr)
    return audio, sr


def plot_waveform_plotly(audio, sr):
    time_axis = np.linspace(
        0,
        len(audio) / sr,
        num=len(audio)
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=time_axis,
            y=audio,
            mode="lines",
            name="Amplitude",
            line=dict(width=1)
        )
    )

    fig.update_layout(
        title="Amplitude Waveform (Temporal Signal Behavior)",
        xaxis_title="Time (s)",
        yaxis_title="Amplitude",
        template="plotly_dark"
    )

    return fig


# -------------------------------
# MFCC – Interactive Heatmap
# -------------------------------
def plot_mfcc_plotly(audio, sr, n_mfcc=40):
    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=n_mfcc)

    fig = go.Figure(
        data=go.Heatmap(
            z=mfcc,
            colorscale="Viridis"
        )
    )

    fig.update_layout(
        title="MFCC Heatmap (Explainability)",
        xaxis_title="Time",
        yaxis_title="MFCC Coefficients",
        template="plotly_dark"
    )

    return fig, mfcc


# -------------------------------
# Spectral Centroid – Interactive
# -------------------------------
def plot_spectral_centroid_plotly(audio, sr):
    spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
    t = librosa.frames_to_time(range(len(spectral_centroid)), sr=sr)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=t,
        y=spectral_centroid,
        mode="lines",
        name="Spectral Centroid"
    ))

    fig.update_layout(
        title="Spectral Centroid (Frequency Instability)",
        xaxis_title="Time (s)",
        yaxis_title="Hz",
        template="plotly_dark"
    )

    return fig, spectral_centroid


# -------------------------------
# ZCR – Interactive
# -------------------------------
def plot_zcr_plotly(audio, sr):
    zcr = librosa.feature.zero_crossing_rate(audio)[0]
    t = librosa.frames_to_time(range(len(zcr)), sr=sr)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=t,
        y=zcr,
        mode="lines",
        name="ZCR"
    ))

    fig.update_layout(
        title="Zero Crossing Rate (Signal Irregularity)",
        xaxis_title="Time (s)",
        yaxis_title="Rate",
        template="plotly_dark"
    )

    return fig, zcr


def explain_audio(audio_path):
    audio, sr = load_audio(audio_path)

    fig_waveform = plot_waveform_plotly(audio, sr)
    fig_mfcc, mfcc = plot_mfcc_plotly(audio, sr)
    fig_sc, sc = plot_spectral_centroid_plotly(audio, sr)
    fig_zcr, zcr = plot_zcr_plotly(audio, sr)

    mfcc_img = save_fig(fig_mfcc)
    sc_img = save_fig(fig_sc)
    zcr_img = save_fig(fig_zcr)

    return {
        "waveform_fig": fig_waveform,
        "mfcc_fig": fig_mfcc,
        "spectral_centroid_fig": fig_sc,
        "zcr_fig": fig_zcr,

        # images for LLM
        "mfcc_img": mfcc_img,
        "spectral_img": sc_img,
        "zcr_img": zcr_img
    }


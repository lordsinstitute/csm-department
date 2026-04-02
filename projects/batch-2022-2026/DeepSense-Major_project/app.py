import streamlit as st
import uuid
import os
import time
from backend.llm_explainer import explain_with_llm

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="DeepSense",
    page_icon="🧠",
    layout="wide"
)

# ============================================================
# Global CSS — dark forensic dashboard theme
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Sora:wght@300;400;600;700&display=swap');

:root {
    --bg-base:        #0d1117;
    --bg-surface:     #161b22;
    --bg-card:        #1c2230;
    --border:         #2a3347;
    --accent:         #00d4ff;
    --accent-dim:     rgba(0, 212, 255, 0.12);
    --accent-glow:    0 0 18px rgba(0, 212, 255, 0.25);
    --danger:         #ff4d6d;
    --safe:           #3ddc97;
    --text-primary:   #e6edf3;
    --text-secondary: #8b949e;
    --text-muted:     #484f58;
    --radius-sm:      8px;
    --radius-md:      14px;
    --radius-lg:      20px;
    --shadow-card:    0 4px 24px rgba(0,0,0,0.45);
}

.stApp {
    background-color: var(--bg-base);
    font-family: 'Sora', sans-serif;
    color: var(--text-primary);
}

#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 1.8rem 2.5rem 3rem 2.5rem;
    max-width: 1280px;
}

[data-testid="stSidebar"] {
    background-color: var(--bg-surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * {
    font-family: 'Sora', sans-serif !important;
    color: var(--text-primary) !important;
}
[data-testid="stSidebarContent"] { padding: 1.5rem 1.2rem; }

[data-testid="stTabs"] [role="tablist"] {
    background: var(--bg-surface);
    border-radius: var(--radius-md);
    padding: 4px;
    border: 1px solid var(--border);
    gap: 4px;
}
[data-testid="stTabs"] [role="tab"] {
    background: transparent;
    border: none !important;
    color: var(--text-secondary) !important;
    font-family: 'Sora', sans-serif;
    font-weight: 600;
    font-size: 0.85rem;
    border-radius: var(--radius-sm) !important;
    padding: 0.55rem 1.2rem !important;
    transition: all 0.2s ease;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    background: var(--accent-dim) !important;
    color: var(--accent) !important;
    box-shadow: var(--accent-glow);
}
[data-testid="stTabs"] [role="tab"]:hover {
    background: var(--bg-card) !important;
    color: var(--text-primary) !important;
}
[data-testid="stTabs"] [role="tablist"] + div { border: none !important; }

h1 { font-size: 1.75rem !important; font-weight: 700 !important; letter-spacing: -0.5px; color: var(--text-primary) !important; }
h2 { font-size: 1.25rem !important; font-weight: 600 !important; color: var(--text-primary) !important; }
h3 { font-size: 1rem !important; font-weight: 600 !important; color: var(--accent) !important; }

hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }

[data-testid="stFileUploader"] {
    background: var(--bg-card);
    border: 1.5px dashed var(--border);
    border-radius: var(--radius-md);
    padding: 1.2rem;
    transition: border-color 0.2s;
}
[data-testid="stFileUploader"]:hover { border-color: var(--accent); }
[data-testid="stFileUploader"] * { color: var(--text-secondary) !important; }

[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, var(--accent), #0099bb) !important;
    border-radius: 99px;
}
[data-testid="stProgressBar"] > div {
    background: var(--bg-card) !important;
    border-radius: 99px;
    height: 8px !important;
}

[data-testid="stMetric"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 1rem 1.2rem !important;
}
[data-testid="stMetricLabel"] { color: var(--text-secondary) !important; font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: 0.08em; }
[data-testid="stMetricValue"] { color: var(--text-primary) !important; font-family: 'DM Mono', monospace !important; font-size: 1.6rem !important; }

[data-testid="stImage"] img {
    border-radius: var(--radius-md) !important;
    border: 1px solid var(--border) !important;
}

[data-testid="stPlotlyChart"] { background: transparent !important; }

.stCaption, caption, [data-testid="stCaptionContainer"] {
    color: var(--text-muted) !important;
    font-size: 0.75rem !important;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# Reusable helper components
# ============================================================
def verdict_badge(label, prob):
    is_fake = "fake" in label.lower()
    color   = "var(--danger)" if is_fake else "var(--safe)"
    bg      = "rgba(255,77,109,0.12)" if is_fake else "rgba(61,220,151,0.12)"
    icon    = "⚠️" if is_fake else "✅"
    pct     = f"{prob*100:.1f}%"
    st.markdown(f"""
    <div style='display:flex;align-items:center;gap:1.2rem;
                background:{bg};border:1.5px solid {color};
                border-radius:var(--radius-md);padding:1.3rem 1.6rem;
                width:100%;margin:0.75rem 0 0 0;box-sizing:border-box'>
        <span style='font-size:2rem'>{icon}</span>
        <div>
            <div style='font-family:Sora,sans-serif;font-weight:700;
                        font-size:1.35rem;color:{color}'>{label}</div>
            <div style='font-family:DM Mono,monospace;font-size:0.85rem;
                        color:var(--text-secondary)'>Fake probability: {pct}</div>
        </div>
    </div>""", unsafe_allow_html=True)


def compact_metrics_row(fake_prob, real_prob):
    """Renders Fake Prob | Real Prob | Confidence Meter in a single compact row."""
    fake_pct = fake_prob * 100
    real_pct = real_prob * 100
    bar_fill = int(fake_pct)
    st.markdown(f"""
    <style>
    @keyframes fillBar {{
        from {{ width: 0%; }}
        to   {{ width: {bar_fill}%; }}
    }}
    .conf-bar-inner {{
        animation: fillBar 0.9s cubic-bezier(.4,0,.2,1) forwards;
    }}
    </style>
    <div style='display:flex;align-items:stretch;gap:0.85rem;
                margin:1rem 0 0 0;flex-wrap:wrap;width:100%'>
        <!-- Fake Probability -->
        <div style='flex:1;min-width:130px;background:var(--bg-card);
                    border:1px solid rgba(255,77,109,0.4);
                    border-radius:var(--radius-md);padding:1.4rem 1.4rem'>
            <div style='font-family:Sora,sans-serif;font-size:0.68rem;font-weight:600;
                        text-transform:uppercase;letter-spacing:0.1em;
                        color:var(--danger);margin-bottom:0.55rem'>Fake Probability</div>
            <div style='font-family:DM Mono,monospace;font-size:1.9rem;
                        font-weight:700;color:var(--text-primary)'>{fake_pct:.1f}%</div>
        </div>
        <!-- Real Probability -->
        <div style='flex:1;min-width:130px;background:var(--bg-card);
                    border:1px solid rgba(61,220,151,0.4);
                    border-radius:var(--radius-md);padding:1.4rem 1.4rem'>
            <div style='font-family:Sora,sans-serif;font-size:0.68rem;font-weight:600;
                        text-transform:uppercase;letter-spacing:0.1em;
                        color:var(--safe);margin-bottom:0.55rem'>Real Probability</div>
            <div style='font-family:DM Mono,monospace;font-size:1.9rem;
                        font-weight:700;color:var(--text-primary)'>{real_pct:.1f}%</div>
        </div>
        <!-- Confidence Meter -->
        <div style='flex:2;min-width:200px;background:var(--bg-card);
                    border:1px solid var(--border);
                    border-radius:var(--radius-md);padding:1.4rem 1.4rem'>
            <div style='font-family:Sora,sans-serif;font-size:0.68rem;font-weight:600;
                        text-transform:uppercase;letter-spacing:0.1em;
                        color:var(--accent);margin-bottom:0.75rem'>Confidence Meter</div>
            <div style='background:rgba(255,255,255,0.07);border-radius:99px;
                        height:10px;overflow:hidden'>
                <div class='conf-bar-inner'
                     style='height:100%;border-radius:99px;
                            background:linear-gradient(90deg,var(--accent),#0099bb)'></div>
            </div>
            <div style='font-family:DM Mono,monospace;font-size:0.72rem;
                        color:var(--text-secondary);margin-top:0.55rem'>{fake_pct:.1f}% confidence — fake</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def section_header(icon, title, subtitle=None):
    sub_html = f"<div style='color:var(--text-secondary);font-size:0.85rem;margin-top:0.25rem'>{subtitle}</div>" if subtitle else ""
    st.markdown(f"""
    <div style='margin-bottom:1.5rem;padding-bottom:1rem;border-bottom:1px solid var(--border)'>
        <div style='display:flex;align-items:center;gap:0.6rem'>
            <span style='font-size:1.4rem'>{icon}</span>
            <span style='font-family:Sora,sans-serif;font-weight:700;
                         font-size:1.4rem;color:var(--text-primary)'>{title}</span>
        </div>
        {sub_html}
    </div>""", unsafe_allow_html=True)


def subsection_heading(icon, title):
    """Clean heading-only label — replaces the old bar-style containers."""
    st.markdown(f"""
    <div style='display:flex;align-items:center;gap:0.5rem;
                margin:1.5rem 0 0.75rem 0'>
        <span style='font-size:1rem'>{icon}</span>
        <span style='font-family:Sora,sans-serif;font-weight:600;font-size:0.9rem;
                     color:var(--text-secondary);text-transform:uppercase;
                     letter-spacing:0.08em'>{title}</span>
    </div>
    """, unsafe_allow_html=True)


def xai_section_label(text):
    st.markdown(f"""
    <div style='font-family:Sora,sans-serif;font-size:0.7rem;font-weight:600;
                text-transform:uppercase;letter-spacing:0.1em;
                color:var(--accent);margin:1.25rem 0 0.5rem 0'>{text}</div>
    """, unsafe_allow_html=True)


def ai_explanation_card(text):
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,rgba(0,212,255,0.06),rgba(0,212,255,0.02));
                border:1px solid rgba(0,212,255,0.25);border-radius:var(--radius-md);
                padding:1.2rem 1.4rem;margin-top:0.5rem'>
        <div style='font-family:Sora,sans-serif;font-size:0.7rem;font-weight:600;
                    text-transform:uppercase;letter-spacing:0.1em;
                    color:var(--accent);margin-bottom:0.75rem'>🤖 AI Explanation</div>
        <div style='color:var(--text-primary);font-size:0.9rem;line-height:1.7'>{text}</div>
    </div>""", unsafe_allow_html=True)


# ============================================================
# BACKEND IMPORTS
# ============================================================
from backend.audio import predict_audio
from backend.image import predict_image
from backend.video import predict_video
from explainability.audio_explainability.audio_xai import explain_audio
from explainability.image_explainability.image_xai import explain_image
from explainability.video_explainability.video_xai import explain_video


def save_uploaded_file(uploaded_file, suffix):
    temp_name = f"cache/temp_{uuid.uuid4().hex}.{suffix}"
    with open(temp_name, "wb") as f:
        f.write(uploaded_file.read())
    return temp_name


def animated_progress(prob):
    # kept for backward compat but no longer called directly
    bar = st.progress(0)
    for i in range(int(prob * 100)):
        time.sleep(0.01)
        bar.progress(i + 1)


def loading_spinner(label="Processing…"):
    """Returns a Streamlit spinner context manager with a consistent label."""
    return st.spinner(label)


# ============================================================
# Sidebar
# ============================================================
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:0.5rem 0 1.5rem 0'>
        <div style='font-size:2.2rem;margin-bottom:0.3rem'>🧠</div>
        <div style='font-family:Sora,sans-serif;font-weight:700;font-size:1.1rem;
                    color:#e6edf3'>DeepSense</div>
        <div style='font-family:DM Mono,monospace;font-size:0.7rem;
                    color:var(--text-muted);letter-spacing:0.05em'>
            XAI · Multimedia Forensics
        </div>
    </div>
    <hr style='border-color:var(--border);margin:0 0 1.5rem 0'>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='font-family:Sora,sans-serif;font-size:0.7rem;font-weight:600;
                text-transform:uppercase;letter-spacing:0.1em;
                color:var(--text-muted);margin-bottom:0.75rem'>Supported Inputs</div>
    """, unsafe_allow_html=True)

    for icon, label, fmts in [
        ("🖼️", "Images", "JPG · JPEG · PNG"),
        ("🎵", "Audio",  "WAV · MP3"),
        ("🎥", "Video",  "MP4 · AVI · MOV"),
    ]:
        st.markdown(f"""
        <div style='display:flex;align-items:center;gap:0.7rem;
                    background:var(--bg-card);border:1px solid var(--border);
                    border-radius:var(--radius-sm);padding:0.65rem 0.9rem;
                    margin-bottom:0.5rem'>
            <span style='font-size:1rem'>{icon}</span>
            <div>
                <div style='font-family:Sora,sans-serif;font-size:0.8rem;
                            font-weight:600;color:var(--text-primary)'>{label}</div>
                <div style='font-family:DM Mono,monospace;font-size:0.68rem;
                            color:var(--text-muted)'>{fmts}</div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <hr style='border-color:var(--border);margin:1.5rem 0 1rem 0'>
    <div style='font-family:Sora,sans-serif;font-size:0.72rem;color:var(--text-muted);
                line-height:1.6;text-align:center'>
        Powered by Grad-CAM, MFCC<br>and LLM-based explainability
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# Tab layout
# ============================================================
tab_image, tab_audio, tab_video = st.tabs([
    "  🖼  Image Detection  ",
    "  🎵  Audio Detection  ",
    "  🎥  Video Detection  "
])


# ==========================================================
# 🖼 IMAGE DETECTION
# ==========================================================
with tab_image:

    section_header("🖼️", "Image Deepfake Detection",
                   "Upload a facial image to analyse authenticity using Grad-CAM")

    uploaded_image = st.file_uploader(
        "Upload an Image",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_image:
        col1, col2 = st.columns([3, 5])

        with col1:
            st.markdown("""
            <div style='font-family:Sora,sans-serif;font-size:0.7rem;font-weight:600;
                        text-transform:uppercase;letter-spacing:0.1em;
                        color:var(--text-muted);margin-bottom:0.5rem'>📷  Uploaded Image</div>
            """, unsafe_allow_html=True)
            st.image(uploaded_image, caption="Uploaded Image", use_container_width=True)

        temp_path = save_uploaded_file(uploaded_image, "jpg")

        with col2:
            # ── Detection Result ──────────────────────────────────────
            subsection_heading("📊", "Analysis Result")
            with st.spinner("Running detection…"):
                label, prob = predict_image(temp_path)

            compact_metrics_row(prob, 1 - prob)
            verdict_badge(label, prob)

        st.markdown("<div style='margin:1.5rem 0'></div>", unsafe_allow_html=True)

        # ── Explainability ────────────────────────────────────────────
        subsection_heading("🔎", "Grad-CAM Explainability")
        with st.spinner("Generating Grad-CAM visualisation…"):
            import tempfile
            import cv2

            fig, cam_img = explain_image(
                img_path=temp_path,
                last_conv_layer_name="block14_sepconv2_act"
            )

        st.pyplot(fig)

        temp_cam = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        cv2.imwrite(temp_cam.name, cam_img)

        # ── AI Explanation ────────────────────────────────────────────
        subsection_heading("🤖", "AI Explanation")
        with st.spinner("Generating AI explanation…"):
            llm_text = explain_with_llm(
                modality="image",
                prediction=label,
                confidence=prob,
                image_paths=[temp_cam.name]
            )

        ai_explanation_card(llm_text)

        os.remove(temp_path)


# ==========================================================
# 🎵 AUDIO DETECTION
# ==========================================================
with tab_audio:

    section_header("🎵", "Audio Deepfake Detection",
                   "Upload a voice recording to detect synthesis artefacts via spectral analysis")

    uploaded_audio = st.file_uploader(
        "Upload an Audio File",
        type=["wav", "mp3"]
    )

    if uploaded_audio:
        temp_path = save_uploaded_file(uploaded_audio, "wav")

        col1, col2 = st.columns([3, 5])

        with col1:
            st.markdown("""
            <div style='font-family:Sora,sans-serif;font-size:0.7rem;font-weight:600;
                        text-transform:uppercase;letter-spacing:0.1em;
                        color:var(--text-muted);margin-bottom:0.5rem'>🎵  Uploaded Audio</div>
            """, unsafe_allow_html=True)
            st.audio(uploaded_audio)

        with col2:
            # ── Detection Result ──────────────────────────────────────────
            subsection_heading("📊", "Analysis Result")
            with st.spinner("Running audio detection…"):
                label, probs = predict_audio(temp_path)

            compact_metrics_row(probs["fake"], probs["real"])
            verdict_badge(label, probs["fake"])

        st.markdown("<div style='margin:1.5rem 0'></div>", unsafe_allow_html=True)

        # ── Spectral XAI ──────────────────────────────────────────────
        subsection_heading("🔎", "Audio XAI — Spectral Features")
        with st.spinner("Computing spectral features…"):
            xai_outputs = explain_audio(temp_path)

        chart_col1, chart_col2 = st.columns(2, gap="medium")
        with chart_col1:
            xai_section_label("Waveform")
            st.plotly_chart(xai_outputs["waveform_fig"], use_container_width=True)
            xai_section_label("Spectral Centroid")
            st.plotly_chart(xai_outputs["spectral_centroid_fig"], use_container_width=True)
        with chart_col2:
            xai_section_label("MFCC Coefficients")
            st.plotly_chart(xai_outputs["mfcc_fig"], use_container_width=True)
            xai_section_label("Zero-Crossing Rate")
            st.plotly_chart(xai_outputs["zcr_fig"], use_container_width=True)

        # ── AI Explanation ────────────────────────────────────────────
        subsection_heading("🤖", "AI Explanation")
        with st.spinner("Generating AI explanation…"):
            llm_text = explain_with_llm(
                modality="audio",
                prediction=label,
                confidence=probs["fake"],
                image_paths=[
                    xai_outputs["mfcc_img"],
                    xai_outputs["spectral_img"],
                    xai_outputs["zcr_img"]
                ]
            )

        ai_explanation_card(llm_text)

        os.remove(temp_path)


# ==========================================================
# 🎥 VIDEO DETECTION
# ==========================================================
with tab_video:

    section_header("🎥", "Video Deepfake Detection",
                   "Upload a video clip to analyse key frames for temporal face inconsistencies")

    uploaded_video = st.file_uploader(
        "Upload a Video",
        type=["mp4", "avi", "mov"]
    )

    if uploaded_video:
        temp_path = save_uploaded_file(uploaded_video, "mp4")

        col1, col2 = st.columns([3, 5])

        with col1:
            st.markdown("""
            <div style='font-family:Sora,sans-serif;font-size:0.7rem;font-weight:600;
                        text-transform:uppercase;letter-spacing:0.1em;
                        color:var(--text-muted);margin-bottom:0.5rem'>🎥  Uploaded Video</div>
            """, unsafe_allow_html=True)
            st.video(uploaded_video)

        with col2:
            # ── Detection Result ──────────────────────────────────────────
            subsection_heading("📊", "Analysis Result")
            with st.spinner("Running video detection…"):
                label, prob = predict_video(temp_path)

            compact_metrics_row(prob, 1 - prob)
            verdict_badge(label, prob)

        st.markdown("<div style='margin:1.5rem 0'></div>", unsafe_allow_html=True)

        # ── Grad-CAM Key Frames ───────────────────────────────────────
        subsection_heading("🔎", "Grad-CAM Key Frames")
        with st.spinner("Extracting Grad-CAM key frames…"):
            import tempfile
            import cv2

            cam_frames = explain_video(
                video_path=temp_path,
                last_conv_layer_name="block14_sepconv2_act",
                max_frames=6
            )

        cols = st.columns(3)
        for i, frame in enumerate(cam_frames):
            with cols[i % 3]:
                st.image(frame, caption=f"Frame {i+1}", width=260)

        frame_paths = []
        for frame in cam_frames[:3]:
            temp_frame = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            cv2.imwrite(temp_frame.name, frame)
            frame_paths.append(temp_frame.name)

        # ── AI Explanation ────────────────────────────────────────────
        subsection_heading("🤖", "AI Explanation")
        with st.spinner("Generating AI explanation…"):
            try:
                llm_text = explain_with_llm(
                    modality="video",
                    prediction=label,
                    confidence=prob,
                    image_paths=frame_paths
                )
                ai_explanation_card(llm_text)
            except Exception as e:
                explanation = "⚠️ Error generating explanation"
                ai_explanation_card(explanation)

        os.remove(temp_path)


# ==========================================================
# Footer
# ==========================================================
st.markdown("""
<div style='margin-top:3rem;padding:1.25rem 0;
            border-top:1px solid var(--border);
            display:flex;justify-content:space-between;align-items:center;
            flex-wrap:wrap;gap:0.5rem'>
    <span style='font-family:Sora,sans-serif;font-size:0.75rem;color:var(--text-muted)'>
        © DeepSense &nbsp;·&nbsp; Explainable AI for Multimedia Deepfake Detection
    </span>
    <span style='font-family:DM Mono,monospace;font-size:0.7rem;color:var(--text-muted)'>
        Grad-CAM · MFCC · ZCR · LLM
    </span>
</div>
""", unsafe_allow_html=True)
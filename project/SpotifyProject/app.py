
import streamlit as st
import pandas as pd
import joblib


st.set_page_config(page_title="Audio Track Popularity Predictor", layout="centered")
st.title("🎵 Audio Track Popularity Predictor")
st.write("Enter or select the audio features below to get the predicted high-popularity probability.")


@st.cache_resource
def load_saved_models():
    return {
        "XGBoost": joblib.load("xgb_model.pkl"),
        "Random Forest": joblib.load("rf_model.pkl"),
        "Logistic Regression": joblib.load("lr_model.pkl"),
        "Neural Network": joblib.load("nn_model.pkl")
    }

models_dict = load_saved_models()


st.sidebar.header("🛠️ Model Settings")
selected_model_name = st.sidebar.selectbox("Choose a classification model:", options=list(models_dict.keys()))
selected_model = models_dict[selected_model_name]


st.header("🎛️ Audio Features Input")
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Core Audio")
    danceability = st.slider("Danceability", 0.0, 1.0, 0.6, 0.01)
    energy = st.slider("Energy", 0.0, 1.0, 0.7, 0.01)
    loudness = st.number_input("Loudness (dB)", -60.0, 0.0, -6.0, 0.1)
    valence = st.slider("Valence (Positivity)", 0.0, 1.0, 0.5, 0.01)

with col2:
    st.subheader("Acoustics & Style")
    speechiness = st.slider("Speechiness", 0.0, 1.0, 0.05, 0.01)
    acousticness = st.slider("Acousticness", 0.0, 1.0, 0.2, 0.01)
    instrumentalness = st.slider("Instrumentalness", 0.0, 1.0, 0.0, 0.01)
    liveness = st.slider("Liveness", 0.0, 1.0, 0.15, 0.01)

with col3:
    st.subheader("Metadata & Track Info")
    tempo = st.number_input("Tempo (BPM)", 40.0, 250.0, 120.0, 1.0)
    duration_minutes = st.number_input("Duration (Minutes)", 0.5, 20.0, 3.5, 0.1)
    year = st.number_input("Release Year", 1950, 2030, 2026, 1)
    featured_artists_count = st.number_input("Featured Artists Count", 0, 10, 0, 1)
    
    # Categorical/Discrete values mapping
    key = st.selectbox("Key", options=list(range(12)), format_func=lambda x: f"Key {x}")
    mode = st.radio("Mode", options=[0, 1], format_func=lambda x: "Major (1)" if x == 1 else "Minor (0)")
    time_signature = st.selectbox("Time Signature", options=[3, 4, 5], index=1)


# Feature Engineering & Exact Ordering


energy_danceability = energy * danceability
valence_danceability = valence * danceability
energy_loudness = energy * loudness
acoustic_energy_ratio = acousticness / (energy + 1e-5) 


input_dict = {
    'energy': energy,
    'tempo': tempo,
    'danceability': danceability,
    'loudness': loudness,
    'liveness': liveness,
    'valence': valence,
    'time_signature': time_signature,
    'speechiness': speechiness,
    'instrumentalness': instrumentalness,
    'mode': mode,
    'key': key,
    'acousticness': acousticness,
    'year': year,
    'duration_minutes': duration_minutes,
    'featured_artists_count': featured_artists_count,
    'energy_danceability': energy_danceability,
    'valence_danceability': valence_danceability,
    'energy_loudness': energy_loudness,
    'acoustic_energy_ratio': acoustic_energy_ratio
}


expected_order = [
    'energy', 'tempo', 'danceability', 'loudness', 'liveness', 'valence', 
    'time_signature', 'speechiness', 'instrumentalness', 'mode', 'key', 
    'acousticness', 'year', 'duration_minutes', 'featured_artists_count', 
    'energy_danceability', 'valence_danceability', 'energy_loudness', 'acoustic_energy_ratio'
]

input_data = pd.DataFrame([input_dict])[expected_order]


probs = selected_model.predict_proba(input_data)
probability = probs[0][1]


st.markdown("---")
st.header("🎯 Prediction Evaluation Output")
st.metric(label=f"Probability of being High-Popularity (via {selected_model_name})", value=f"{probability * 100:.2f}%")

if probability >= 0.70:
    st.success("🔥 High Probability! Fits popular track signature trends.")
elif probability >= 0.40:
    st.warning("⚠️ Moderate Probability. Fits baseline structural mainstream options.")
else:
    st.error("📉 Low Probability. This profile appears structurally niche.")


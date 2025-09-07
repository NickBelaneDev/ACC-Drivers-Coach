# app.py
import streamlit as st
import pandas as pd

# --- Seitenkonfiguration ---
st.set_page_config(page_title="Mein Projekt", page_icon="✨", layout="wide")

# --- Sidebar ---
st.sidebar.title("Navigation")
seite = st.sidebar.radio("Gehe zu:", ["Startseite", "Daten", "Einstellungen"])

# --- Startseite ---
if seite == "Startseite":
    st.title("🚀 Willkommen zu meinem Projekt")
    st.write("Dies ist dein Streamlit-Template. Hier kannst du direkt loslegen.")
    name = st.text_input("Wie heißt du?")
    if name:
        st.success(f"Hallo {name}, schön dass du hier bist!")

# --- Daten ---
elif seite == "Daten":
    st.title("📊 Datenübersicht")
    datei = st.file_uploader("CSV-Datei hochladen", type=["csv"])

    @st.cache_data(show_spinner=False)
    def load_csv(file):
        import pandas as pd
        return pd.read_csv(file)

    if datei:
        df = load_csv(datei)

        with st.expander("Vorschau"):
            st.dataframe(df.head(200), use_container_width=True)

        # Spaltenfinder (ohne Kopien)
        def find_col(cands):
            m = {c.lower(): c for c in df.columns}
            for c in cands:
                if c.lower() in m: return m[c.lower()]
            return None

        x_col = find_col(["Distance","distance","laptime","timestamp","seconds","ms"])
        x_data = df[x_col] if x_col else None

        select_01 = st.selectbox("Parameters", ["Throttle", "Brake"])

        signals = {
            "THROTTLE": ["THROTTLE","throttle"],
            "STEERANGLE": ["STEERANGLE","steerangle","steer_angle","steering"],
            "BRAKE": ["BRAKE","brake","brake_pressure"],
            "SPEED": ["SPEED","speed","kmh","mph"]
        }

        # Downsampling (Slider)
        step = st.slider("Downsampling", 1, 50, 1)
        idx = slice(None, None, step)

        c1, c2 = st.columns(2)
        for i, (label, variants) in enumerate(signals.items()):
            colname = find_col(variants)
            if not colname:
                st.warning(f"{label}: Spalte nicht gefunden.")
                continue

            # Kein copy, nur Ansicht + optionaler X
            plot_df = df.loc[idx, [colname]]
            if x_data is not None:
                plot_df = plot_df.set_index(df.loc[idx, x_col])

            target = c1 if i % 2 == 0 else c2
            with target:
                st.subheader(label)
                st.line_chart(plot_df, use_container_width=True)
# --- Einstellungen ---
elif seite == "Einstellungen":
    st.title("⚙️ Einstellungen")
    theme = st.selectbox("Wähle ein Theme:", ["Hell", "Dunkel"])
    st.write(f"Aktuell ausgewählt: **{theme}**")

import streamlit as st
from streamlit_calendar import calendar

st.set_page_config(page_title="Calendario de Citas", layout="wide")

# — Login —
if "role" not in st.session_state:
    st.session_state.role = ""
if st.session_state.role == "":
    with st.form("login_form"):
        st.write("Inicia sesión")
        role = st.selectbox("Elige tu rol", ["Veterinario", "Administrador"])
        if st.form_submit_button("Iniciar sesión"):
            st.session_state.role = role
    st.stop()

st.sidebar.write(f"Rol: {st.session_state.role}")

# — Inicializar citas en sesión —
if "appointments" not in st.session_state:
    st.session_state.appointments = []

# — Preparar eventos —
events = [
    {
        "id": a["id"],
        "title": f"{a['animal_name']} – {a['treatment']}",
        "start": f"{a['date']}T{a['time']}",
        "end":   f"{a['date']}T{a['time']}"
    }
    for a in st.session_state.appointments
]


st.title("Calendario de Citas")
state = calendar(events=events, key="calendar")

# — Capturar cambio de fecha/hora —
if state.get("eventChange", {}).get("event"):
    ev = state["eventChange"]["event"]
    appt = next(a for a in st.session_state.appointments if a["id"] == ev["id"])
    appt["date"], appt["time"] = ev["start"].split("T")
    # Streamlit detecta el cambio en session_state y refresca automáticamente
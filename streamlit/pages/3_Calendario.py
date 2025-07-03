import streamlit as st
from streamlit_calendar import calendar

# Inicializar sesión
if "appointments" not in st.session_state:
    st.session_state.appointments = []
    st.session_state._id_counter  = 1

st.title("Calendario de Citas – Clínica Veterinaria")

events = [
    {
        "id":    a["id"],
        "title": f"{a['animal_name']} – {a['treatment']}",
        "start": f"{a['date']}T{a['time']}",
        "end":   f"{a['date']}T{a['time']}"
    }
    for a in st.session_state.appointments
]

state = calendar(events=events, key="calendar")

if state.get("eventChange", {}).get("event"):
    ev = state["eventChange"]["event"]
    appt = next(a for a in st.session_state.appointments if a['id'] == ev['id'])
    appt['date'], appt['time'] = ev["start"].split("T")
    st.experimental_rerun()
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Dashboard Clínica Veterinaria", layout="wide")

# Inicializar almacenamiento en  sesión
if "appointments" not in st.session_state:
    st.session_state.appointments = []
    st.session_state._id_counter = 1

# Crear DataFrame local
df = pd.DataFrame(st.session_state.appointments)

st.title("Dashboard – Estado de Citas y Facturación")

if df.empty:
    st.info("No hay citas registradas.")
else:
    # Parsear
    df['datetime'] = pd.to_datetime(df['date'] + 'T' + df['time'])
    próximas = df[df['datetime'] >= datetime.now()].sort_values('datetime').head(5)
    pendientes = df[df['status'] == 'pending']

    # Métricas
    col1, col2 = st.columns(2)
    col1.metric("Próximas citas", len(próximas))
    col2.metric("Citas pendientes de facturar", len(pendientes))

    st.subheader("5 próximas citas")
    st.table(próximas[['id','animal_name','owner_name','treatment','datetime']]
             .rename(columns={'datetime':'Fecha y hora'}))
#cambio de prueba


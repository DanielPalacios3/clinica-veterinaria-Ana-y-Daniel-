import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Citas – Clínica Veterinaria")

# Inicializar sesión
if "appointments" not in st.session_state:
    st.session_state.appointments = []
    st.session_state._id_counter = 1

mode = st.sidebar.selectbox("Modo", ["Crear cita", "Finalizar cita"])

# lista tratamientos
treatments = [
    "Análisis: sangre y hormonales", "Vacunación", "Desparasitación",
    "Revisión general", "Cardiología", "Cutánea", "Broncológica",
    "Ecografías", "Limpieza bucal", "Extracción dental",
    "Cirugía – Castración", "Cirugía – Abdominal", "Cirugía – Cardíaca",
    "Cirugía – Articular y ósea", "Cirugía – Hernias"
]

if mode == "Crear cita":
    st.title("Crear Nueva Cita")
    with st.form("form_cita"):
        animal_name = st.text_input("Nombre del animal")
        owner_name  = st.text_input("Nombre del dueño")
        treatment   = st.selectbox("Tratamiento", treatments)
        date        = st.date_input("Fecha", datetime.now())
        time        = st.time_input("Hora", datetime.now().time())
        if st.form_submit_button("Crear cita"):
            appt = {
                "id":             st.session_state._id_counter,
                "animal_name":    animal_name,
                "owner_name":     owner_name,
                "treatment":      treatment,
                "date":           date.isoformat(),
                "time":           time.strftime("%H:%M:%S"),
                "status":         "pending",
                "treatments_done": [],
                "payment_method":  "",
                "invoice":         {}
            }
            st.session_state.appointments.append(appt)
            st.session_state._id_counter += 1
            st.success(f"Cita #{appt['id']} creada")
            st.json(appt)

else:
    st.title("Finalizar Cita y Generar Factura")
    df = pd.DataFrame(st.session_state.appointments)
    pendientes = df[df['status'] == 'pending']
    if pendientes.empty:
        st.info("No hay citas pendientes.")
    else:
        opciones = pendientes.apply(
            lambda r: f"{r['id']} | {r['animal_name']} – {r['treatment']} ({r['date']} {r['time']})",
            axis=1
        ).tolist()
        sel = st.selectbox("Selecciona cita", opciones)
        idx = int(sel.split("|")[0].strip())
        cita = next(a for a in st.session_state.appointments if a['id']==idx)

        realizados = st.multiselect(
            "Tratamientos realizados",
            treatments,
            default=[cita['treatment']]
        )
        pago = st.selectbox("Forma de pago", ["Transferencia","Efectivo","Tarjeta"])

        if st.button("Finalizar cita"):
            cita['status'] = 'done'
            cita['treatments_done'] = realizados
            cita['payment_method']  = pago
            # generar factura  simple
            invoice = {
                "invoice_id": f"INV-{cita['id']:04d}",
                "owner": cita['owner_name'],
                "animal": cita['animal_name'],
                "treatments": realizados,
                "total": len(realizados)*50.0,
                "payment_method": pago,
            }
            cita['invoice'] = invoice
            st.success("Cita finalizada y factura:")
            st.json(invoice)

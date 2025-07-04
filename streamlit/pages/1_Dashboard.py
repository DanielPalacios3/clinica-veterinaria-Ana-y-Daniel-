import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Dashboard Clínica Veterinaria", layout="wide")

# — Login —
if "role" not in st.session_state:
    st.session_state.role = "Veterinario"  # valor por defecto

st.sidebar.selectbox(
    "Elige tu rol",
    ["Veterinario", "Administrador"],
    index=0 if st.session_state.role == "Veterinario" else 1,
    key="role"
)


# — Sidebar —
st.sidebar.write(f"Rol: {st.session_state.role}")
st.sidebar.markdown("Versión v0.5.1")

# — Inicializar datos en sesión —
for key in ["appointments", "owners", "pets", "products", "sales"]:
    if key not in st.session_state:
        st.session_state[key] = []
for cnt in ["_id_counter","owner_id_counter","pet_id_counter","product_id_counter","sale_id_counter"]:
    if cnt not in st.session_state:
        st.session_state[cnt] = 1

# — Construir dataframes —
df_app = pd.DataFrame(st.session_state.appointments)
df_own = pd.DataFrame(st.session_state.owners)
df_pet = pd.DataFrame(st.session_state.pets)
df_prod = pd.DataFrame(st.session_state.products)

# — Cálculo de métricas citas —
if not df_app.empty:
    df_app["datetime"] = pd.to_datetime(df_app["date"] + "T" + df_app["time"])
    próximas = df_app[df_app["datetime"] >= datetime.now()].sort_values("datetime").head(5)
    pendientes = df_app[df_app["status"] == "pending"]
else:
    próximas = pd.DataFrame()
    pendientes = pd.DataFrame()

# — Cálculo de métricas clientes —
total_owners = len(df_own)
total_pets = len(df_pet)
fallecidas = int((df_pet["status"] == "fallecido").sum()) if not df_pet.empty else 0

# — Cálculo de métricas productos —
total_prods = len(df_prod)
total_units = int(df_prod["stock"].sum()) if not df_prod.empty else 0
low_stock_cnt = int((df_prod["stock"] < 5).sum()) if not df_prod.empty else 0

# — Mostrar métricas —
st.title("Dashboard Clínica Veterinaria")

st.subheader("Resumen de citas y clientes")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Próximas citas", len(próximas))
c2.metric("Citas pendientes de facturar", len(pendientes))
c3.metric("Dueños registrados", total_owners)
c4.metric("Mascotas registradas", total_pets)
c5.metric("Mascotas fallecidas", fallecidas)

st.subheader("Resumen de inventario de productos")
p1, p2, p3 = st.columns(3)
p1.metric("Productos distintos", total_prods)
p2.metric("Unidades en stock", total_units)
p3.metric("Productos bajo stock (<5)", low_stock_cnt)

# — Tablas detalladas —
if not próximas.empty:
    st.subheader("5 próximas citas")
    st.table(
        próximas[["id","animal_name","owner_name","treatment","datetime"]]
        .rename(columns={"datetime":"Fecha y hora"})
    )

if not df_own.empty:
    st.subheader("Dueños registrados")
    st.table(
        df_own[["id","name","dni","phone"]]
        .rename(columns={"id":"ID","name":"Nombre","dni":"DNI","phone":"Teléfono"})
    )

if not df_prod.empty:
    st.subheader("Productos en inventario")
    st.table(
        df_prod[["id","name","category","brand","price","stock"]]
        .rename(columns={
            "id":"ID","name":"Nombre","category":"Categoría",
            "brand":"Marca","price":"Precio","stock":"Stock"
        })
    )

# — Historial clínico por mascota —
if not df_app.empty:
    st.subheader("Historial clínico")
    animales = sorted(df_app["animal_name"].unique())
    seleccionado = st.selectbox("Selecciona mascota", animales)
    hist = df_app[df_app["animal_name"] == seleccionado].sort_values("datetime")
    hist = hist.assign(
        Factura=hist["invoice"].apply(lambda inv: inv.get("invoice_id") if isinstance(inv, dict) else "")
    )
    st.table(
        hist[["date","time","status","treatments_done","Factura"]]
        .rename(columns={
            "date":"Fecha","time":"Hora","status":"Estado",
            "treatments_done":"Tratamientos realizados"
        })
    )



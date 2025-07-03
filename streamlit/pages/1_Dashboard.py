import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Dashboard Clínica Veterinaria", layout="wide")

# Inicializar sesión
if "appointments" not in st.session_state:
    st.session_state.appointments = []
    st.session_state._id_counter = 1
if "owners" not in st.session_state:
    st.session_state.owners = []
    st.session_state.owner_id_counter = 1
if "pets" not in st.session_state:
    st.session_state.pets = []
    st.session_state.pet_id_counter = 1
if "products" not in st.session_state:
    st.session_state.products = []
    st.session_state.product_id_counter = 1

st.title("Dashboard – Citas, Clientes y Productos")

# Citas
df_app = pd.DataFrame(st.session_state.appointments)
if not df_app.empty:
    df_app['datetime'] = pd.to_datetime(df_app['date'] + 'T' + df_app['time'])
    próximas = df_app[df_app['datetime'] >= datetime.now()].sort_values('datetime').head(5)
    pendientes = df_app[df_app['status'] == 'pending']
else:
    próximas = pd.DataFrame()
    pendientes = pd.DataFrame()

# Clientes
df_own = pd.DataFrame(st.session_state.owners)
df_pet = pd.DataFrame(st.session_state.pets)
total_owners = len(df_own)
total_pets   = len(df_pet)
fallecidas   = int((df_pet['status'] == 'fallecido').sum()) if not df_pet.empty else 0
# Productos
df_prod = pd.DataFrame(st.session_state.products)
if not df_prod.empty:
    total_prods    = len(df_prod)
    total_units    = int(df_prod['stock'].sum())
    low_stock_cnt  = int((df_prod['stock'] < 5).sum())
else:
    total_prods   = 0
    total_units   = 0
    low_stock_cnt = 0

# Mostrar métricas
st.subheader("Resumen General")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Próximas citas",      len(próximas))
c2.metric("Citas por facturar",   len(pendientes))
c3.metric("Dueños registrados",   total_owners)
c4.metric("Mascotas registradas", total_pets)
c5.metric("Mascotas fallecidas",  fallecidas)

st.subheader("Inventario de Productos")
p1, p2, p3 = st.columns(3)
p1.metric("Productos distintos", total_prods)
p2.metric("Unidades en stock",   total_units)
p3.metric("Productos bajo stock", low_stock_cnt)

if not df_prod.empty:
    st.subheader("Listado de Productos")
    st.table(df_prod[['id','name','category','brand','price','stock']].rename(columns={
        'id':'ID','name':'Nombre','category':'Categoría',
        'brand':'Marca','price':'Precio','stock':'Stock'
    }))


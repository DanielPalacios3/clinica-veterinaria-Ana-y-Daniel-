import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Operaciones Clínica Veterinaria", layout="wide")

# Inicializar sesión
if "appointments" not in st.session_state:
    st.session_state.appointments       = []
    st.session_state._id_counter        = 1
if "owners" not in st.session_state:
    st.session_state.owners             = []
    st.session_state.owner_id_counter   = 1
if "pets" not in st.session_state:
    st.session_state.pets               = []
    st.session_state.pet_id_counter     = 1
if "products" not in st.session_state:
    st.session_state.products           = []
    st.session_state.product_id_counter = 1
if "sales" not in st.session_state:
    st.session_state.sales             = []
    st.session_state.sale_id_counter    = 1

# Tratamientos y categorías
treatments = [
    "Análisis: sangre y hormonales","Vacunación","Desparasitación",
    "Revisión general","Cardiología","Cutánea","Broncológica",
    "Ecografías","Limpieza bucal","Extracción dental",
    "Cirugía – Castración","Cirugía – Abdominal","Cirugía – Cardíaca",
    "Cirugía – Articular y ósea","Cirugía – Hernias"
]
categories = ["Vitaminas","Cremas analgésicas","Desparasitador","Belleza"]

section = st.sidebar.selectbox("Sección", ["Citas", "Clientes", "Productos"])
# —————— Citas ——————
if section == "Citas":
    mode = st.sidebar.selectbox("Modo citas", ["Crear cita", "Finalizar cita"])
    st.title(f"{mode}")

    # Crear / Finalizar cita (igual que v0.3)…
    # [omitido aquí para brevedad, manten tu implementación v0.3]

# —————— Clientes ——————
elif section == "Clientes":
    action = st.sidebar.selectbox("Acción", [
        "Alta dueño", "Alta mascota", "Buscar cliente",
        "Eliminar mascota", "Eliminar dueño"
    ])
    st.title(action)
    # Gestión de clientes (igual que v0.3)…
    # [igual que en v0.3]
# —————— Productos ——————
else:
    action = st.sidebar.selectbox("Acción", [
        "Alta producto", "Baja producto", "Modificar precio",
        "Buscar producto", "Venta de producto", "Recepción stock"
    ])
    st.title(action)
    df_prod = pd.DataFrame(st.session_state.products)

    # Alta producto
    if action == "Alta producto":
        with st.form("form_alta_prod"):
            name     = st.text_input("Nombre del producto")
            category = st.selectbox("Categoría", categories)
            brand    = st.text_input("Marca")
            price    = st.number_input("Precio (€)", min_value=0.0, format="%.2f")
            stock    = st.number_input("Stock inicial", min_value=0, step=1)
            if st.form_submit_button("Registrar producto"):
                prod = {
                    "id":       st.session_state.product_id_counter,
                    "name":     name,
                    "category": category,
                    "brand":    brand,
                    "price":    price,
                    "stock":    int(stock)
                }
        st.session_state.products.append(prod)
        st.session_state.product_id_counter += 1
        st.success(f"Producto #{prod['id']} registrado")
        st.json(prod)

    # Baja producto
    elif action == "Baja producto":
        if df_prod.empty:
            st.info("No hay productos registrados.")
        else:
            opts = df_prod.apply(lambda r: f"{r['id']} | {r['name']}", axis=1).tolist()
            sel = st.selectbox("Selecciona producto", opts)
            pid = int(sel.split("|")[0].strip())
            if st.button("Eliminar producto"):
                st.session_state.products = [
                    p for p in st.session_state.products if p['id'] != pid
                ]
                st.success(f"Producto #{pid} eliminado")
# Modificar precio
    elif action == "Modificar precio":
        if df_prod.empty:
            st.info("No hay productos.")
        else:
            opts = df_prod.apply(lambda r: f"{r['id']} | {r['name']} (€{r['price']})", axis=1).tolist()
            sel = st.selectbox("Selecciona producto", opts)
            pid = int(sel.split("|")[0].strip())
            prod = next(p for p in st.session_state.products if p['id']==pid)
            new_price = st.number_input("Nuevo precio (€)", value=float(prod['price']), format="%.2f")
            if st.button("Actualizar precio"):
                prod['price'] = new_price
                st.success(f"Precio actualizado a €{new_price:.2f}")
                st.json(prod)

 # Buscar producto
    elif action == "Buscar producto":
        by = st.radio("Buscar por", ["Nombre","Categoría"])
        if by == "Nombre":
            term = st.text_input("Nombre (parcial)")
            if st.button("Buscar"):
                res = df_prod[df_prod['name'].str.contains(term, case=False)]
                if res.empty:
                    st.warning("No hay resultados.")
                else:
                    st.table(res)
        else:
            cat = st.selectbox("Categoría", categories)
            res = df_prod[df_prod['category']==cat]
            if res.empty:
                st.warning("No hay productos en esta categoría.")
            else:
                st.table(res)
# Venta de producto
    elif action == "Venta de producto":
        if df_prod.empty:
            st.info("No hay productos para vender.")
        else:
            opts = df_prod.apply(lambda r: f"{r['id']} | {r['name']} (stock: {r['stock']})", axis=1).tolist()
            sel = st.selectbox("Selecciona producto", opts)
            pid = int(sel.split("|")[0].strip())
            prod = next(p for p in st.session_state.products if p['id']==pid)
            qty = st.number_input("Cantidad a vender", min_value=1, max_value=int(prod['stock']), step=1)
            pago = st.selectbox("Forma de pago", ["Transferencia","Efectivo","Tarjeta"])
            if st.button("Vender"):
                if qty > prod['stock']:
                    st.error("Cantidad supera stock disponible.")
                else:
                    prod['stock'] -= qty
                    sale = {
                        "sale_id": st.session_state.sale_id_counter,
                        "date":    datetime.now().isoformat(),
                        "items":   [{"product": prod['name'], "qty": qty, "unit_price": prod['price']}],
                        "total":   qty * prod['price'],
                        "payment": pago
                    }
            st.session_state.sales.append(sale)
            st.session_state.sale_id_counter += 1
            st.success("Venta registrada e inventario actualizado")
            st.json(sale)
# Recepción de stock
    else:
        if df_prod.empty:
            st.info("No hay productos para recepción.")
        else:
            opts = df_prod.apply(lambda r: f"{r['id']} | {r['name']}", axis=1).tolist()
            sel = st.selectbox("Selecciona producto", opts)
            pid = int(sel.split("|")[0].strip())
            add_qty = st.number_input("Cantidad a recibir", min_value=1, step=1)
            if st.button("Actualizar stock"):
                prod = next(p for p in st.session_state.products if p['id']==pid)
                prod['stock'] += int(add_qty)
                st.success(f"Stock de '{prod['name']}' incrementado en {add_qty}")
                st.json(prod)


        
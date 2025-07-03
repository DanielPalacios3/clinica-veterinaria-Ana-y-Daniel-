import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Operaciones Clínica Veterinaria", layout="wide")

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
st.sidebar.markdown("Versión v0.5.1")

# — Inicializar datos en sesión —
for key in ["appointments", "owners", "pets", "products", "sales"]:
    if key not in st.session_state:
        st.session_state[key] = []
for cnt in ["_id_counter","owner_id_counter","pet_id_counter","product_id_counter","sale_id_counter"]:
    if cnt not in st.session_state:
        st.session_state[cnt] = 1

# — Listas auxiliares —
treatments = [
    "Análisis: sangre y hormonales","Vacunación","Desparasitación",
    "Revisión general","Cardiología","Cutánea","Broncológica",
    "Ecografías","Limpieza bucal","Extracción dental",
    "Cirugía – Castración","Cirugía – Abdominal","Cirugía – Cardíaca",
    "Cirugía – Articular y ósea","Cirugía – Hernias"
]
categories = ["Vitaminas","Cremas analgésicas","Desparasitador","Belleza"]

# — Secciones —
section = st.sidebar.selectbox("Sección", ["Citas","Clientes","Productos","Tests"])

# — Sección Citas —
if section == "Citas":
    mode = st.sidebar.selectbox("Modo citas", ["Crear cita","Finalizar cita"])
    st.header(mode)

    if mode == "Crear cita":
        with st.form("form_crear_cita"):
            animal = st.text_input("Nombre del animal")
            owner = st.text_input("Nombre del dueño")
            treatment = st.selectbox("Tratamiento", treatments)
            date = st.date_input("Fecha", datetime.now())
            time = st.time_input("Hora", datetime.now().time())
            submit = st.form_submit_button("Crear cita")
        if submit:
            appt = {
                "id": st.session_state._id_counter,
                "animal_name": animal,
                "owner_name": owner,
                "treatment": treatment,
                "date": date.isoformat(),
                "time": time.strftime("%H:%M:%S"),
                "status": "pending",
                "treatments_done": [],
                "payment_method": "",
                "invoice": {}
            }
            st.session_state.appointments.append(appt)
            st.session_state._id_counter += 1
            st.success(f"Cita {appt['id']} creada")
            st.json(appt)

    else:  # Finalizar cita
        df_app = pd.DataFrame(st.session_state.appointments)
        pendientes = df_app[df_app["status"] == "pending"]
        if pendientes.empty:
            st.info("No hay citas pendientes.")
        else:
            sel = st.selectbox(
                "Selecciona cita",
                pendientes.apply(lambda r: f"{r['id']} | {r['animal_name']} – {r['treatment']} ({r['date']} {r['time']})", axis=1)
            )
            idx = int(sel.split("|")[0].strip())
            with st.form("form_finalizar_cita"):
                realizados = st.multiselect("Tratamientos realizados", treatments, default=[next(a for a in st.session_state.appointments if a["id"]==idx)["treatment"]])
                pago = st.selectbox("Forma de pago", ["Transferencia","Efectivo","Tarjeta"])
                submit = st.form_submit_button("Finalizar cita")
            if submit:
                appt = next(a for a in st.session_state.appointments if a["id"]==idx)
                appt["status"] = "done"
                appt["treatments_done"] = realizados
                appt["payment_method"] = pago
                invoice = {
                    "invoice_id": f"INV-{appt['id']:04d}",
                    "owner": appt["owner_name"],
                    "animal": appt["animal_name"],
                    "treatments": realizados,
                    "total": len(realizados)*50.0,
                    "payment_method": pago
                }
                appt["invoice"] = invoice
                st.success("Cita finalizada y factura generada")
                st.json(invoice)

# — Sección Clientes —
elif section == "Clientes":
    # definir acciones según rol
    acciones = ["Buscar cliente"]
    if st.session_state.role == "Administrador":
        acciones = ["Alta dueño","Alta mascota"] + acciones + ["Eliminar mascota","Eliminar dueño"]
    action = st.sidebar.selectbox("Acción", acciones)
    st.header(action)


    if action == "Alta dueño":
        with st.form("form_alta_dueño"):
            name = st.text_input("Nombre completo")
            dni = st.text_input("DNI")
            address = st.text_input("Dirección")
            phone = st.text_input("Teléfono")
            email = st.text_input("Correo electrónico")
            submit = st.form_submit_button("Registrar dueño")
        if submit:
            owner = {
                "id": st.session_state.owner_id_counter,
                "name": name,
                "dni": dni,
                "address": address,
                "phone": phone,
                "email": email
            }
            st.session_state.owners.append(owner)
            st.session_state.owner_id_counter += 1
            st.success(f"Dueño {owner['id']} registrado")
            st.json(owner)

    elif action == "Alta mascota":
        if not st.session_state.owners:
            st.info("Registra primero al dueño.")
        else:
            opts = [f"{o['id']} | {o['name']}" for o in st.session_state.owners]
            sel = st.selectbox("Selecciona dueño", opts)
            owner_id = int(sel.split("|")[0].strip())
            with st.form("form_alta_mascota"):
                name = st.text_input("Nombre de la mascota")
                species = st.text_input("Especie")
                breed = st.text_input("Raza")
                birth = st.date_input("Fecha de nacimiento")
                pats = st.text_area("Patologías previas (separadas por comas)")
                submit = st.form_submit_button("Registrar mascota")
            if submit:
                pet = {
                    "id": st.session_state.pet_id_counter,
                    "name": name,
                    "species": species,
                    "breed": breed,
                    "birth_date": birth.isoformat(),
                    "pathologies": [p.strip() for p in pats.split(",") if p.strip()],
                    "owner_id": owner_id,
                    "status": "active"
                }
                st.session_state.pets.append(pet)
                st.session_state.pet_id_counter += 1
                st.success(f"Mascota {pet['id']} registrada")
                st.json(pet)

    elif action == "Buscar cliente":
        by = st.radio("Buscar por", ["DNI","Teléfono"])
        term = st.text_input("Valor de búsqueda")
        if st.button("Buscar"):
            matches = [
                o for o in st.session_state.owners
                if (by=="DNI" and o["dni"]==term) or (by=="Teléfono" and o["phone"]==term)
            ]
            if not matches:
                st.error("No se encontró ningún dueño.")
            else:
                for o in matches:
                    st.subheader(f"Dueño {o['id']}: {o['name']}")
                    st.write(f"- DNI: {o['dni']}")
                    st.write(f"- Dirección: {o['address']}")
                    st.write(f"- Teléfono: {o['phone']}")
                    st.write(f"- Email: {o['email']}")
                    pets = [p for p in st.session_state.pets if p["owner_id"]==o["id"]]
                    if pets:
                        st.write("Mascotas asociadas:")
                        for p in pets:
                            st.write(f"  - {p['id']} {p['name']} ({p['status']})")
                    else:
                        st.write("Sin mascotas asociadas.")
                        st.write("Sin mascotas asociadas.")

    elif action == "Eliminar mascota":
        active = [p for p in st.session_state.pets if p["status"]=="active"]
        if not active:
            st.info("No hay mascotas activas.")
        else:
            opts = [f"{p['id']} | {p['name']}" for p in active]
            sel = st.selectbox("Selecciona mascota", opts)
            pet_id = int(sel.split("|")[0].strip())
            choice = st.radio("Acción", ["Marcar fallecido","Eliminar definitivamente"])
            if st.button("Ejecutar"):
                idx = next(i for i,p in enumerate(st.session_state.pets) if p["id"]==pet_id)
                if choice == "Marcar fallecido":
                    st.session_state.pets[idx]["status"] = "fallecido"
                    st.success(f"Mascota {pet_id} marcada como fallecida")
                else:
                    st.session_state.pets.pop(idx)
                    st.success(f"Mascota {pet_id} eliminada")

    else:  # Eliminar dueño
        if not st.session_state.owners:
            st.info("No hay dueños registrados.")
        else:
            opts = [f"{o['id']} | {o['name']}" for o in st.session_state.owners]
            sel = st.selectbox("Selecciona dueño", opts)
            owner_id = int(sel.split("|")[0].strip())
            if st.button("Eliminar dueño y sus mascotas"):
                st.session_state.pets = [p for p in st.session_state.pets if p["owner_id"]!=owner_id]
                st.session_state.owners = [o for o in st.session_state.owners if o["id"]!=owner_id]
                st.success(f"Dueño {owner_id} y sus mascotas eliminados")

# — Sección Productos —
elif section == "Productos":
    acciones = ["Buscar producto","Venta de producto"]
    if st.session_state.role == "Administrador":
        acciones = ["Alta producto","Recepción stock","Modificar precio","Baja producto"] + acciones
    action = st.sidebar.selectbox("Acción", acciones)
    st.header(action)
    df_prod = pd.DataFrame(st.session_state.products)


    if action == "Alta producto":
        with st.form("form_alta_producto"):
            name = st.text_input("Nombre del producto")
            category = st.selectbox("Categoría", categories)
            brand = st.text_input("Marca")
            price = st.number_input("Precio (€)", min_value=0.0, format="%.2f")
            stock = st.number_input("Stock inicial", min_value=0, step=1)
            submit = st.form_submit_button("Registrar producto")
        if submit:
            prod = {
                "id": st.session_state.product_id_counter,
                "name": name,
                "category": category,
                "brand": brand,
                "price": price,
                "stock": int(stock)
            }
            st.session_state.products.append(prod)
            st.session_state.product_id_counter += 1
            st.success(f"Producto {prod['id']} registrado")
            st.json(prod)

    elif action == "Recepción stock":
        if df_prod.empty:
            st.info("No hay productos.")
        else:
            opts = df_prod.apply(lambda r: f"{r['id']} | {r['name']}", axis=1).tolist()
            sel = st.selectbox("Selecciona producto", opts)
            pid = int(sel.split("|")[0].strip())
            with st.form("form_recepcion_stock"):
                qty = st.number_input("Cantidad a recibir", min_value=1, step=1)
                submit = st.form_submit_button("Actualizar stock")
            if submit:
                prod = next(p for p in st.session_state.products if p["id"]==pid)
                prod["stock"] += int(qty)
                st.success(f"Stock de producto {pid} incrementado en {qty}")
                st.json(prod)

    elif action == "Modificar precio":
        if df_prod.empty:
            st.info("No hay productos.")
        else:
            opts = df_prod.apply(lambda r: f"{r['id']} | {r['name']} (€{r['price']})", axis=1).tolist()
            sel = st.selectbox("Selecciona producto", opts)
            pid = int(sel.split("|")[0].strip())
            prod = next(p for p in st.session_state.products if p["id"]==pid)
            with st.form("form_modificar_precio"):
                new_price = st.number_input("Nuevo precio (€)", value=float(prod["price"]), format="%.2f")
                submit = st.form_submit_button("Actualizar precio")
            if submit:
                prod["price"] = new_price
                st.success(f"Precio de producto {pid} actualizado a €{new_price:.2f}")
                st.json(prod)

    elif action == "Baja producto":
        if df_prod.empty:
            st.info("No hay productos.")
        else:
            opts = df_prod.apply(lambda r: f"{r['id']} | {r['name']}", axis=1).tolist()
            sel = st.selectbox("Selecciona producto", opts)
            pid = int(sel.split("|")[0].strip())
            if st.button("Eliminar producto"):
                st.session_state.products = [p for p in st.session_state.products if p["id"]!=pid]
                st.success(f"Producto {pid} eliminado")

    elif action == "Buscar producto":
        criterio = st.radio("Buscar por", ["Nombre","Categoría"])
        if criterio == "Nombre":
            term = st.text_input("Nombre (parcial)")
            if st.button("Buscar"):
                res = df_prod[df_prod["name"].str.contains(term, case=False)]
                if res.empty:
                    st.warning("No se encontraron productos.")
                else:
                    st.table(res)
        else:
            cat = st.selectbox("Categoría", categories)
            res = df_prod[df_prod["category"]==cat]
            if res.empty:
                st.warning("No hay productos en esta categoría.")
            else:
                st.table(res)

    else:  # Venta de producto
        if df_prod.empty:
            st.info("No hay productos.")
        else:
            opts = df_prod.apply(lambda r: f"{r['id']} | {r['name']} (stock {r['stock']})", axis=1).tolist()
            sel = st.selectbox("Selecciona producto", opts)
            pid = int(sel.split("|")[0].strip())
            prod = next(p for p in st.session_state.products if p["id"]==pid)
            with st.form("form_venta_producto"):
                qty = st.number_input("Cantidad a vender", min_value=1, max_value=prod["stock"], step=1)
                pago = st.selectbox("Forma de pago", ["Transferencia","Efectivo","Tarjeta"])
                submit = st.form_submit_button("Vender")
            if submit:
                prod["stock"] -= int(qty)
                sale = {
                    "sale_id": st.session_state.sale_id_counter,
                    "date": datetime.now().isoformat(),
                    "items": [{"product": prod["name"], "qty": qty, "unit_price": prod["price"]}],
                    "total": qty * prod["price"],
                    "payment": pago
                }
                st.session_state.sales.append(sale)
                st.session_state.sale_id_counter += 1
                st.success("Venta registrada")
                st.json(sale)

# — Sección Tests —
else:
    st.header("Pruebas de integridad")
    errors = []
    # Citas duplicadas
    ids = [a["id"] for a in st.session_state.appointments]
    if len(ids) != len(set(ids)):
        errors.append("IDs de citas duplicados")
    # Stock negativo
    for p in st.session_state.products:
        if p["stock"] < 0:
            errors.append(f"Stock negativo en producto {p['id']}")
    # Mascotas sin dueño válido
    owner_ids = {o["id"] for o in st.session_state.owners}
    for pet in st.session_state.pets:
        if pet["owner_id"] not in owner_ids:
            errors.append(f"Mascota {pet['id']} sin dueño válido")
    if not errors:
        st.success("Todas las pruebas pasaron correctamente")
    else:
        for e in errors:
            st.error(e)

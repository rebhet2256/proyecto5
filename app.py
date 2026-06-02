"""
app.py — EGGROUTE
Sistema de Optimizacion de Distribucion de Huevos
Investigacion Operativa | Modelo de Transporte | SciPy
"""

import streamlit as st
import pandas as pd
import numpy as np
import os

from transporte import resolver_transporte, validar_datos
from utils import (
    crear_grafico_barras,
    crear_grafico_circular,
    crear_sankey,
    crear_heatmap_costos,
    ALMACENES_DEFAULT,
    CLIENTES_DEFAULT,
    COSTOS_DEFAULT,
)

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EGGROUTE — Distribucion de Huevos",
    page_icon="🥚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inyectar CSS
css_path = os.path.join(os.path.dirname(__file__), "styles.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
if 'almacenes' not in st.session_state:
    st.session_state.almacenes = ALMACENES_DEFAULT.copy()
if 'clientes' not in st.session_state:
    st.session_state.clientes = CLIENTES_DEFAULT.copy()
if 'costos' not in st.session_state:
    st.session_state.costos = [row[:] for row in COSTOS_DEFAULT]
if 'resultado' not in st.session_state:
    st.session_state.resultado = None

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo / Brand
    st.markdown("""
    <div style="
        padding: 28px 20px 20px;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 8px;
    ">
        <div style="
            font-family: 'Sora', 'Inter', sans-serif;
            font-size: 22px;
            font-weight: 700;
            color: #FB8C00;
            letter-spacing: -0.01em;
            margin-bottom: 4px;
        ">🥚 EGGROUTE</div>
        <div style="
            font-size: 11.5px;
            color: #9CA3AF;
            font-weight: 400;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        ">Distribucion Inteligente</div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation
    st.markdown("""
    <div style="
        padding: 8px 12px 4px;
        font-size: 10px;
        color: #6B7280;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    ">NAVEGACION</div>
    """, unsafe_allow_html=True)

    pagina = st.radio(
        label="Selecciona una página",
        options=[
            "⌂  Inicio",
            "◫  Almacenes",
            "◧  Clientes",
            "⇄  Costos de Transporte",
            "⚙  Optimizacion",
            "◨  Resultados",
            "ⓘ  Acerca del Proyecto",
        ],
        label_visibility="hidden",
    )

    # Status panel at bottom
    st.markdown("<div style='flex:1'></div>", unsafe_allow_html=True)
    n_a = len(st.session_state.almacenes)
    n_c = len(st.session_state.clientes)
    oferta_t = sum(a['oferta'] for a in st.session_state.almacenes)
    demanda_t = sum(c['demanda'] for c in st.session_state.clientes)

    color_bal = "#43A047" if abs(oferta_t - demanda_t) < 1 else "#F59E0B"
    lbl_bal = "Balanceado" if abs(oferta_t - demanda_t) < 1 else "Desequilibrado"

    st.markdown(f"""
    <div style="
        margin: 16px 8px 0;
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
        padding: 14px 16px;
        border: 1px solid rgba(255,255,255,0.07);
    ">
        <div style="font-size:10.5px;color:#9CA3AF;font-weight:700;
                    text-transform:uppercase;letter-spacing:0.08em;
                    margin-bottom:10px;">Estado del Modelo</div>
        <div style="display:flex;justify-content:space-between;
                    margin-bottom:6px;font-size:12.5px;color:#D1D5DB;">
            <span>Almacenes</span>
            <span style="color:#FB8C00;font-weight:600;">{n_a}</span>
        </div>
        <div style="display:flex;justify-content:space-between;
                    margin-bottom:6px;font-size:12.5px;color:#D1D5DB;">
            <span>Clientes</span>
            <span style="color:#FB8C00;font-weight:600;">{n_c}</span>
        </div>
        <div style="display:flex;justify-content:space-between;
                    margin-bottom:6px;font-size:12.5px;color:#D1D5DB;">
            <span>Oferta total</span>
            <span style="color:#D1D5DB;font-weight:500;">{oferta_t:,}</span>
        </div>
        <div style="display:flex;justify-content:space-between;
                    margin-bottom:10px;font-size:12.5px;color:#D1D5DB;">
            <span>Demanda total</span>
            <span style="color:#D1D5DB;font-weight:500;">{demanda_t:,}</span>
        </div>
        <div style="
            background:{color_bal}22;
            border:1px solid {color_bal}55;
            border-radius:6px;
            padding:5px 10px;
            text-align:center;
            font-size:11px;
            font-weight:600;
            color:{color_bal};
        ">{lbl_bal}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="
        padding: 16px 8px 20px;
        font-size: 11px;
        color: #4B5563;
        text-align: center;
        border-top: 1px solid rgba(255,255,255,0.06);
        margin-top: 14px;
    ">
        Investigacion Operativa<br>
        <span style="color:#6B7280;">Universidad — 2026</span>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def page_header(titulo, subtitulo="", icono=""):
    st.markdown(f"""
    <div style="
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 14px;
        padding: 28px 32px 24px;
        margin-bottom: 28px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        display: flex;
        align-items: center;
        gap: 16px;
    ">
        <div style="font-size: 36px; line-height: 1;">{icono}</div>
        <div>
            <div style="
                font-family: 'Sora', 'Inter', sans-serif;
                font-size: 26px;
                font-weight: 700;
                color: #111827;
                letter-spacing: -0.02em;
                line-height: 1.15;
            ">{titulo}</div>
            {f'<div style="font-size:14px;color:#6B7280;margin-top:4px;font-weight:400;">{subtitulo}</div>' if subtitulo else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)


def card(contenido_html, padding="20px 24px"):
    st.markdown(f"""
    <div style="
        background:#FFFFFF;
        border:1px solid #E5E7EB;
        border-radius:12px;
        padding:{padding};
        box-shadow:0 1px 3px rgba(0,0,0,0.06);
        margin-bottom:16px;
    ">{contenido_html}</div>
    """, unsafe_allow_html=True)


def kpi_badge(label, valor, color="#FB8C00", icono=""):
    return f"""
    <div style="
        background:#FFFFFF;
        border:1px solid #E5E7EB;
        border-radius:12px;
        padding:20px 24px;
        box-shadow:0 1px 3px rgba(0,0,0,0.06);
        border-top:3px solid {color};
    ">
        <div style="font-size:11px;color:#6B7280;font-weight:700;
                    text-transform:uppercase;letter-spacing:0.06em;
                    margin-bottom:8px;">{icono} {label}</div>
        <div style="font-size:26px;font-weight:700;color:#111827;
                    font-family:'Sora','Inter',sans-serif;
                    letter-spacing:-0.02em;">{valor}</div>
    </div>
    """


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: INICIO
# ─────────────────────────────────────────────────────────────────────────────
def pagina_inicio():
    page_header(
        "Sistema de Optimizacion de Distribucion de Huevos",
        "Modelo de Transporte y Programacion Lineal — Investigacion Operativa",
        "🥚"
    )

    n_a = len(st.session_state.almacenes)
    n_c = len(st.session_state.clientes)
    oferta_t = sum(a['oferta'] for a in st.session_state.almacenes)
    estado_sol = st.session_state.resultado['estado'] if st.session_state.resultado else "Sin calcular"

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(kpi_badge("Almacenes", str(n_a), "#1F2937", "🏭"), unsafe_allow_html=True)
    with col2:
        st.markdown(kpi_badge("Clientes", str(n_c), "#FB8C00", "🏪"), unsafe_allow_html=True)
    with col3:
        st.markdown(kpi_badge("Oferta Total", f"{oferta_t:,} cajas", "#43A047", "📦"), unsafe_allow_html=True)
    with col4:
        color_e = "#43A047" if estado_sol == "OPTIMO" else "#6B7280"
        st.markdown(kpi_badge("Estado", estado_sol, color_e, "✅"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_desc, col_flujo = st.columns([3, 2])

    with col_desc:
        card("""
        <div style="font-family:'Sora','Inter',sans-serif;font-size:17px;
                    font-weight:600;color:#111827;margin-bottom:12px;">
            ¿Que es EGGROUTE?
        </div>
        <div style="font-size:14px;color:#374151;line-height:1.75;">
            <b>EGGROUTE</b> es un sistema de optimizacion logistica que aplica el
            <b>Modelo de Transporte</b> de Investigacion Operativa para determinar
            la distribucion optima de cajas de huevos desde almacenes hacia
            puntos de venta en <b>La Paz y El Alto</b>.
        </div>
        <div style="font-size:14px;color:#374151;line-height:1.75;margin-top:12px;">
            El objetivo es <b>minimizar el costo total de transporte</b> respetando
            la oferta disponible en cada almacen y satisfaciendo la demanda de
            cada cliente, usando <b>Programacion Lineal resuelta con SciPy HiGHS</b>.
        </div>
        <div style="margin-top:18px;display:flex;gap:10px;flex-wrap:wrap;">
            <span style="background:#FB8C0015;color:#FB8C00;border:1px solid #FB8C0040;
                         border-radius:20px;padding:5px 14px;font-size:12px;font-weight:600;">
                Modelo de Transporte
            </span>
            <span style="background:#43A04715;color:#43A047;border:1px solid #43A04740;
                         border-radius:20px;padding:5px 14px;font-size:12px;font-weight:600;">
                Programacion Lineal
            </span>
            <span style="background:#3B82F615;color:#3B82F6;border:1px solid #3B82F640;
                         border-radius:20px;padding:5px 14px;font-size:12px;font-weight:600;">
                Metodo Simplex (SciPy)
            </span>
            <span style="background:#1F293715;color:#1F2937;border:1px solid #1F293740;
                         border-radius:20px;padding:5px 14px;font-size:12px;font-weight:600;">
                Plotly Visualizations
            </span>
        </div>
        """)

    with col_flujo:
        card("""
        <div style="font-family:'Sora','Inter',sans-serif;font-size:15px;
                    font-weight:600;color:#111827;margin-bottom:16px;">
            Flujo del Sistema
        </div>
        <div style="display:flex;flex-direction:column;gap:0;">
            <div style="display:flex;align-items:center;gap:12px;padding:10px 0;
                        border-bottom:1px solid #F3F4F6;">
                <div style="width:30px;height:30px;background:#FB8C00;border-radius:50%;
                             display:flex;align-items:center;justify-content:center;
                             font-size:13px;font-weight:700;color:white;flex-shrink:0;">1</div>
                <div style="font-size:13.5px;color:#374151;">Registrar <b>almacenes</b> y oferta disponible</div>
            </div>
            <div style="display:flex;align-items:center;gap:12px;padding:10px 0;
                        border-bottom:1px solid #F3F4F6;">
                <div style="width:30px;height:30px;background:#FB8C00;border-radius:50%;
                             display:flex;align-items:center;justify-content:center;
                             font-size:13px;font-weight:700;color:white;flex-shrink:0;">2</div>
                <div style="font-size:13.5px;color:#374151;">Registrar <b>clientes</b> y demanda requerida</div>
            </div>
            <div style="display:flex;align-items:center;gap:12px;padding:10px 0;
                        border-bottom:1px solid #F3F4F6;">
                <div style="width:30px;height:30px;background:#FB8C00;border-radius:50%;
                             display:flex;align-items:center;justify-content:center;
                             font-size:13px;font-weight:700;color:white;flex-shrink:0;">3</div>
                <div style="font-size:13.5px;color:#374151;">Ingresar <b>matriz de costos</b> de transporte</div>
            </div>
            <div style="display:flex;align-items:center;gap:12px;padding:10px 0;
                        border-bottom:1px solid #F3F4F6;">
                <div style="width:30px;height:30px;background:#1F2937;border-radius:50%;
                             display:flex;align-items:center;justify-content:center;
                             font-size:13px;font-weight:700;color:white;flex-shrink:0;">4</div>
                <div style="font-size:13.5px;color:#374151;"><b>Optimizar</b> con SciPy (HiGHS)</div>
            </div>
            <div style="display:flex;align-items:center;gap:12px;padding:10px 0;">
                <div style="width:30px;height:30px;background:#43A047;border-radius:50%;
                             display:flex;align-items:center;justify-content:center;
                             font-size:13px;font-weight:700;color:white;flex-shrink:0;">5</div>
                <div style="font-size:13.5px;color:#374151;">Analizar <b>resultados</b> y visualizaciones</div>
            </div>
        </div>
        """)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1F2937 0%, #374151 100%);
        border-radius: 14px;
        padding: 24px 32px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 16px;
    ">
        <div>
            <div style="font-size:16px;font-weight:700;color:#FFFFFF;
                        font-family:'Sora','Inter',sans-serif;margin-bottom:4px;">
                ¿Listo para optimizar?
            </div>
            <div style="font-size:13px;color:#9CA3AF;">
                Los datos de ejemplo ya estan cargados. Ve a Optimizacion para resolver el modelo.
            </div>
        </div>
        <div style="
            background:#FB8C00;
            border-radius:8px;
            padding:10px 22px;
            font-size:13.5px;
            font-weight:700;
            color:white;
            cursor:pointer;
        ">⚙ Ir a Optimizacion →</div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: ALMACENES
# ─────────────────────────────────────────────────────────────────────────────
def pagina_almacenes():
    page_header("Almacenes", "Gestione los almacenes y su oferta disponible en cajas", "🏭")

    col_form, col_tabla = st.columns([1, 2])

    with col_form:
        card("""
        <div style="font-size:15px;font-weight:600;color:#111827;margin-bottom:16px;">
            Agregar Almacen
        </div>
        """)
        with st.form("form_almacen", clear_on_submit=True):
            nombre_a = st.text_input("Nombre del Almacen", placeholder="Ej: El Alto, Zona Sur...")
            oferta_a = st.number_input("Oferta disponible (cajas)", min_value=1, value=1000, step=100)
            submitted = st.form_submit_button("➕ Agregar Almacen", use_container_width=True)
            if submitted:
                if nombre_a.strip():
                    nombres_existentes = [a['nombre'].lower() for a in st.session_state.almacenes]
                    if nombre_a.strip().lower() in nombres_existentes:
                        st.error("Ya existe un almacen con ese nombre.")
                    else:
                        st.session_state.almacenes.append({
                            'nombre': nombre_a.strip(),
                            'oferta': oferta_a
                        })
                        st.session_state.resultado = None
                        st.success(f"Almacen '{nombre_a}' agregado correctamente.")
                        st.rerun()
                else:
                    st.error("Ingrese un nombre valido.")

        if len(st.session_state.almacenes) > 0:
            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            with st.expander("Restablecer datos de ejemplo"):
                if st.button("🔄 Cargar datos por defecto", use_container_width=True):
                    from utils import ALMACENES_DEFAULT
                    st.session_state.almacenes = ALMACENES_DEFAULT.copy()
                    st.session_state.resultado = None
                    st.rerun()

    with col_tabla:
        if st.session_state.almacenes:
            st.markdown("""
            <div style="font-size:13px;color:#6B7280;margin-bottom:10px;font-weight:500;">
                Puede editar la tabla directamente. Los cambios se aplican al guardar.
            </div>
            """, unsafe_allow_html=True)

            df_almacenes = pd.DataFrame(st.session_state.almacenes)
            df_edited = st.data_editor(
                df_almacenes,
                column_config={
                    "nombre": st.column_config.TextColumn("Almacen", width="medium"),
                    "oferta": st.column_config.NumberColumn(
                        "Oferta (cajas)",
                        min_value=1,
                        format="%d",
                        width="medium"
                    ),
                },
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True,
                key="editor_almacenes"
            )

            col_g, col_e = st.columns(2)
            with col_g:
                if st.button("💾 Guardar cambios", use_container_width=True):
                    nueva_lista = df_edited.dropna().to_dict('records')
                    nueva_lista = [
                        {'nombre': str(r['nombre']).strip(), 'oferta': int(r['oferta'])}
                        for r in nueva_lista
                        if str(r.get('nombre', '')).strip() and r.get('oferta', 0) > 0
                    ]
                    st.session_state.almacenes = nueva_lista
                    st.session_state.resultado = None
                    st.success("Almacenes actualizados.")
                    st.rerun()
            with col_e:
                if st.button("🗑️ Eliminar seleccion", use_container_width=True):
                    st.info("Use la tabla para eliminar filas directamente y luego guarde.")

            # Resumen
            oferta_total = sum(a['oferta'] for a in st.session_state.almacenes)
            st.markdown("<br>", unsafe_allow_html=True)
            cols = st.columns(3)
            with cols[0]:
                st.metric("Total Almacenes", len(st.session_state.almacenes))
            with cols[1]:
                st.metric("Oferta Total", f"{oferta_total:,} cajas")
            with cols[2]:
                prom = oferta_total // max(len(st.session_state.almacenes), 1)
                st.metric("Promedio por Almacen", f"{prom:,} cajas")
        else:
            st.info("No hay almacenes registrados. Agregue el primero usando el formulario.")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: CLIENTES
# ─────────────────────────────────────────────────────────────────────────────
def pagina_clientes():
    page_header("Clientes", "Gestione los clientes y su demanda requerida en cajas", "🏪")

    col_form, col_tabla = st.columns([1, 2])

    with col_form:
        card("""
        <div style="font-size:15px;font-weight:600;color:#111827;margin-bottom:16px;">
            Agregar Cliente
        </div>
        """)
        with st.form("form_cliente", clear_on_submit=True):
            nombre_c = st.text_input("Nombre del Cliente", placeholder="Ej: Mercado Rodriguez...")
            demanda_c = st.number_input("Demanda requerida (cajas)", min_value=1, value=500, step=50)
            submitted = st.form_submit_button("➕ Agregar Cliente", use_container_width=True)
            if submitted:
                if nombre_c.strip():
                    nombres_existentes = [c['nombre'].lower() for c in st.session_state.clientes]
                    if nombre_c.strip().lower() in nombres_existentes:
                        st.error("Ya existe un cliente con ese nombre.")
                    else:
                        st.session_state.clientes.append({
                            'nombre': nombre_c.strip(),
                            'demanda': demanda_c
                        })
                        st.session_state.resultado = None
                        st.success(f"Cliente '{nombre_c}' agregado correctamente.")
                        st.rerun()
                else:
                    st.error("Ingrese un nombre valido.")

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        with st.expander("Restablecer datos de ejemplo"):
            if st.button("🔄 Cargar datos por defecto", use_container_width=True, key="reset_clientes"):
                from utils import CLIENTES_DEFAULT
                st.session_state.clientes = CLIENTES_DEFAULT.copy()
                st.session_state.resultado = None
                st.rerun()

    with col_tabla:
        if st.session_state.clientes:
            st.markdown("""
            <div style="font-size:13px;color:#6B7280;margin-bottom:10px;font-weight:500;">
                Puede editar la tabla directamente. Los cambios se aplican al guardar.
            </div>
            """, unsafe_allow_html=True)

            df_clientes = pd.DataFrame(st.session_state.clientes)
            df_edited = st.data_editor(
                df_clientes,
                column_config={
                    "nombre": st.column_config.TextColumn("Cliente", width="medium"),
                    "demanda": st.column_config.NumberColumn(
                        "Demanda (cajas)",
                        min_value=1,
                        format="%d",
                        width="medium"
                    ),
                },
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True,
                key="editor_clientes"
            )

            if st.button("💾 Guardar cambios", use_container_width=True, key="guardar_clientes"):
                nueva_lista = df_edited.dropna().to_dict('records')
                nueva_lista = [
                    {'nombre': str(r['nombre']).strip(), 'demanda': int(r['demanda'])}
                    for r in nueva_lista
                    if str(r.get('nombre', '')).strip() and r.get('demanda', 0) > 0
                ]
                st.session_state.clientes = nueva_lista
                st.session_state.resultado = None
                st.success("Clientes actualizados.")
                st.rerun()

            demanda_total = sum(c['demanda'] for c in st.session_state.clientes)
            oferta_total = sum(a['oferta'] for a in st.session_state.almacenes)

            st.markdown("<br>", unsafe_allow_html=True)
            cols = st.columns(3)
            with cols[0]:
                st.metric("Total Clientes", len(st.session_state.clientes))
            with cols[1]:
                st.metric("Demanda Total", f"{demanda_total:,} cajas")
            with cols[2]:
                diff = oferta_total - demanda_total
                delta_color = "normal" if diff >= 0 else "inverse"
                st.metric("Balance Oferta-Demanda", f"{diff:+,}", delta=f"{diff:+,}", delta_color=delta_color)
        else:
            st.info("No hay clientes registrados. Agregue el primero usando el formulario.")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: COSTOS DE TRANSPORTE
# ─────────────────────────────────────────────────────────────────────────────
def pagina_costos():
    page_header(
        "Costos de Transporte",
        "Defina el costo (Bs.) por caja de transportar desde cada almacen hacia cada cliente",
        "⇄"
    )

    n_a = len(st.session_state.almacenes)
    n_c = len(st.session_state.clientes)

    if n_a == 0 or n_c == 0:
        st.warning("⚠️ Debe registrar almacenes y clientes primero antes de ingresar costos.")
        return

    # Ajustar la matriz de costos si cambio el tamanio
    costos = st.session_state.costos
    if len(costos) != n_a or (n_a > 0 and len(costos[0]) != n_c):
        nueva_matriz = []
        for i in range(n_a):
            fila = []
            for j in range(n_c):
                try:
                    fila.append(costos[i][j])
                except (IndexError, TypeError):
                    fila.append(1.0)
            nueva_matriz.append(fila)
        st.session_state.costos = nueva_matriz
        costos = nueva_matriz

    nombres_a = [a['nombre'] for a in st.session_state.almacenes]
    nombres_c = [c['nombre'] for c in st.session_state.clientes]

    st.markdown("""
    <div style="
        background:#FFF8F0;
        border:1px solid #FB8C0040;
        border-left:4px solid #FB8C00;
        border-radius:8px;
        padding:12px 18px;
        font-size:13.5px;
        color:#374151;
        margin-bottom:20px;
    ">
        <b>Instrucciones:</b> Ingrese el costo en <b>bolivianos (Bs.)</b> por caja de transportar
        desde cada almacen (filas) hacia cada cliente (columnas). Haga clic en cualquier celda para editarla.
    </div>
    """, unsafe_allow_html=True)

    df_costos = pd.DataFrame(costos, index=nombres_a, columns=nombres_c)

    col_config = {
        col: st.column_config.NumberColumn(col, min_value=0.0, format="%.2f", step=0.1)
        for col in nombres_c
    }

    df_edited = st.data_editor(
        df_costos,
        column_config=col_config,
        use_container_width=True,
        key="editor_costos"
    )

    col_b1, col_b2, col_b3 = st.columns([1, 1, 2])
    with col_b1:
        if st.button("💾 Guardar Costos", use_container_width=True):
            nueva_matriz = df_edited.values.tolist()
            st.session_state.costos = nueva_matriz
            st.session_state.resultado = None
            st.success("✅ Matriz de costos guardada correctamente.")
            st.rerun()
    with col_b2:
        if st.button("🔄 Restablecer Costos", use_container_width=True):
            from utils import COSTOS_DEFAULT
            st.session_state.costos = [row[:] for row in COSTOS_DEFAULT]
            st.session_state.resultado = None
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📊 Mapa de Calor de Costos", "📈 Estadisticas"])
    with tab1:
        fig_heatmap = crear_heatmap_costos(
            st.session_state.almacenes,
            st.session_state.clientes,
            st.session_state.costos
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)

    with tab2:
        costos_flat = [c for row in costos for c in row]
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("Costo Minimo", f"Bs. {min(costos_flat):.2f}")
        with c2: st.metric("Costo Maximo", f"Bs. {max(costos_flat):.2f}")
        with c3: st.metric("Costo Promedio", f"Bs. {np.mean(costos_flat):.2f}")
        with c4: st.metric("Desv. Estandar", f"Bs. {np.std(costos_flat):.2f}")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: OPTIMIZACION
# ─────────────────────────────────────────────────────────────────────────────
def pagina_optimizacion():
    page_header(
        "Optimizacion",
        "Configure y ejecute el modelo de programacion lineal",
        "⚙"
    )

    # Modelo matematico
    col_modelo, col_config = st.columns([3, 2])

    with col_modelo:
        card("""
        <div style="font-size:15px;font-weight:600;color:#111827;margin-bottom:16px;">
            Modelo Matematico — Problema de Transporte
        </div>

        <div style="margin-bottom:18px;">
            <div style="font-size:12px;font-weight:700;color:#6B7280;text-transform:uppercase;
                        letter-spacing:0.07em;margin-bottom:8px;">Funcion Objetivo</div>
            <div style="background:#F8FAFC;border:1px solid #E5E7EB;border-radius:8px;
                        padding:14px 18px;font-size:14px;color:#1F2937;font-family:monospace;
                        letter-spacing:0.02em;">
                Min Z = <span style="color:#FB8C00">Σᵢ Σⱼ</span> cᵢⱼ · xᵢⱼ
            </div>
            <div style="font-size:12.5px;color:#6B7280;margin-top:6px;padding-left:4px;">
                Minimizar la suma de costos de transporte ponderados por cantidad enviada.
            </div>
        </div>

        <div style="margin-bottom:18px;">
            <div style="font-size:12px;font-weight:700;color:#6B7280;text-transform:uppercase;
                        letter-spacing:0.07em;margin-bottom:8px;">Restricciones</div>
            <div style="display:flex;flex-direction:column;gap:8px;">
                <div style="background:#F0FDF4;border:1px solid #43A04730;border-radius:8px;
                            padding:12px 16px;">
                    <div style="font-size:13px;font-weight:600;color:#43A047;margin-bottom:4px;">
                        📦 Oferta de Almacenes
                    </div>
                    <div style="font-family:monospace;font-size:13px;color:#374151;">
                        Σⱼ xᵢⱼ ≤ sᵢ  ∀i
                    </div>
                    <div style="font-size:12px;color:#6B7280;margin-top:4px;">
                        No se puede enviar mas de lo disponible en cada almacen.
                    </div>
                </div>
                <div style="background:#FFF7ED;border:1px solid #FB8C0030;border-radius:8px;
                            padding:12px 16px;">
                    <div style="font-size:13px;font-weight:600;color:#FB8C00;margin-bottom:4px;">
                        🏪 Demanda de Clientes
                    </div>
                    <div style="font-family:monospace;font-size:13px;color:#374151;">
                        Σᵢ xᵢⱼ ≥ dⱼ  ∀j
                    </div>
                    <div style="font-size:12px;color:#6B7280;margin-top:4px;">
                        La demanda de cada cliente debe ser completamente satisfecha.
                    </div>
                </div>
                <div style="background:#F0F9FF;border:1px solid #3B82F630;border-radius:8px;
                            padding:12px 16px;">
                    <div style="font-size:13px;font-weight:600;color:#3B82F6;margin-bottom:4px;">
                        ✔ No Negatividad
                    </div>
                    <div style="font-family:monospace;font-size:13px;color:#374151;">
                        xᵢⱼ ≥ 0  ∀i,j
                    </div>
                    <div style="font-size:12px;color:#6B7280;margin-top:4px;">
                        No se pueden enviar cantidades negativas de producto.
                    </div>
                </div>
            </div>
        </div>

        <div>
            <div style="font-size:12px;font-weight:700;color:#6B7280;text-transform:uppercase;
                        letter-spacing:0.07em;margin-bottom:8px;">Notacion</div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;font-size:12.5px;color:#374151;">
                <div><code style="color:#FB8C00">i</code> — Almacen (origen)</div>
                <div><code style="color:#FB8C00">j</code> — Cliente (destino)</div>
                <div><code style="color:#1F2937">xᵢⱼ</code> — Cajas enviadas i→j</div>
                <div><code style="color:#1F2937">cᵢⱼ</code> — Costo unitario i→j</div>
                <div><code style="color:#43A047">sᵢ</code> — Oferta del almacen i</div>
                <div><code style="color:#43A047">dⱼ</code> — Demanda del cliente j</div>
            </div>
        </div>
        """)

    with col_config:
        n_a = len(st.session_state.almacenes)
        n_c = len(st.session_state.clientes)
        oferta_t = sum(a['oferta'] for a in st.session_state.almacenes)
        demanda_t = sum(c['demanda'] for c in st.session_state.clientes)

        card(f"""
        <div style="font-size:15px;font-weight:600;color:#111827;margin-bottom:16px;">
            Parametros del Modelo
        </div>
        <div style="display:flex;flex-direction:column;gap:10px;">
            <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:10px 14px;background:#F8FAFC;border-radius:8px;
                        border:1px solid #E5E7EB;">
                <div style="font-size:13px;color:#6B7280;font-weight:500;">Metodo</div>
                <div style="font-size:13px;color:#111827;font-weight:600;">Modelo de Transporte</div>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:10px 14px;background:#F8FAFC;border-radius:8px;
                        border:1px solid #E5E7EB;">
                <div style="font-size:13px;color:#6B7280;font-weight:500;">Solver</div>
                <div style="font-size:13px;color:#111827;font-weight:600;">SciPy + HiGHS</div>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:10px 14px;background:#F8FAFC;border-radius:8px;
                        border:1px solid #E5E7EB;">
                <div style="font-size:13px;color:#6B7280;font-weight:500;">Objetivo</div>
                <div style="font-size:13px;color:#111827;font-weight:600;">Minimizacion</div>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:10px 14px;background:#F8FAFC;border-radius:8px;
                        border:1px solid #E5E7EB;">
                <div style="font-size:13px;color:#6B7280;font-weight:500;">Almacenes</div>
                <div style="font-size:13px;color:#FB8C00;font-weight:700;">{n_a}</div>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:10px 14px;background:#F8FAFC;border-radius:8px;
                        border:1px solid #E5E7EB;">
                <div style="font-size:13px;color:#6B7280;font-weight:500;">Clientes</div>
                <div style="font-size:13px;color:#FB8C00;font-weight:700;">{n_c}</div>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:10px 14px;background:#F8FAFC;border-radius:8px;
                        border:1px solid #E5E7EB;">
                <div style="font-size:13px;color:#6B7280;font-weight:500;">Variables</div>
                <div style="font-size:13px;color:#111827;font-weight:600;">{n_a * n_c}</div>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:10px 14px;background:#F8FAFC;border-radius:8px;
                        border:1px solid #E5E7EB;">
                <div style="font-size:13px;color:#6B7280;font-weight:500;">Restricciones</div>
                <div style="font-size:13px;color:#111827;font-weight:600;">{n_a + n_c}</div>
            </div>
        </div>
        """)

    st.markdown("<br>", unsafe_allow_html=True)

    # Validar
    errores, advertencias = validar_datos(
        st.session_state.almacenes,
        st.session_state.clientes,
        st.session_state.costos
    )

    if errores:
        for e in errores:
            st.error(f"❌ {e}")
        return

    for adv in advertencias:
        st.warning(f"⚠️ {adv}")

    # Boton principal
    st.markdown("""
    <div style="
        background:linear-gradient(135deg,#1F2937 0%,#374151 100%);
        border-radius:14px;
        padding:28px 32px;
        text-align:center;
        margin:8px 0 24px;
    ">
        <div style="font-size:17px;font-weight:600;color:#FFFFFF;margin-bottom:6px;">
            Todo listo para calcular la solucion optima
        </div>
        <div style="font-size:13px;color:#9CA3AF;margin-bottom:0;">
            El algoritmo Simplex encontrara la distribucion de menor costo total.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_btn = st.columns([1, 2, 1])
    with col_btn[1]:
        calcular = st.button("🚀 Calcular Distribucion Optima", use_container_width=True)

    if calcular:
        with st.spinner("⚙️ Resolviendo modelo de transporte con SciPy HiGHS......"):
            import time
            time.sleep(0.4)  # UX pause
            resultado = resolver_transporte(
                st.session_state.almacenes,
                st.session_state.clientes,
                st.session_state.costos
            )
            st.session_state.resultado = resultado

        if resultado['estado'] == "OPTIMO":
            st.success(f"✅ Solucion optima encontrada. Costo total minimo: **Bs. {resultado['costo_total']:,.2f}**")
            st.balloons()
        elif resultado['estado'] == "INFACTIBLE":
            st.error("❌ El problema es infactible. Revise los datos.")
        else:
            st.warning(f"⚠️ Estado: {resultado['estado']}")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: RESULTADOS
# ─────────────────────────────────────────────────────────────────────────────
def pagina_resultados():
    page_header("Resultados", "Analisis detallado del plan optimo de distribucion", "◨")

    res = st.session_state.resultado

    if res is None:
        st.markdown("""
        <div style="
            background:#FFFFFF;
            border:2px dashed #E5E7EB;
            border-radius:14px;
            padding:60px 32px;
            text-align:center;
            margin:20px 0;
        ">
            <div style="font-size:48px;margin-bottom:16px;">📊</div>
            <div style="font-size:18px;font-weight:600;color:#374151;margin-bottom:8px;">
                No hay resultados aun
            </div>
            <div style="font-size:14px;color:#9CA3AF;">
                Dirígase a la sección <b>Optimizacion</b> y presione <b>Calcular Distribucion Optima</b>.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── KPIs ──
    estado = res['estado']
    color_estado = "#43A047" if estado == "OPTIMO" else "#EF4444"

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi_badge("Costo Total Minimo", f"Bs. {res['costo_total']:,.2f}", "#FB8C00", "💰"), unsafe_allow_html=True)
    with c2:
        oferta_util = sum(r['oferta_utilizada'] for r in res['resumen_oferta'])
        st.markdown(kpi_badge("Oferta Utilizada", f"{oferta_util:,.0f} cajas", "#1F2937", "📦"), unsafe_allow_html=True)
    with c3:
        clientes_ok = sum(1 for r in res['resumen_demanda'] if r['demanda_pendiente'] < 1)
        st.markdown(kpi_badge("Clientes Atendidos", f"{clientes_ok}/{len(res['resumen_demanda'])}", "#3B82F6", "🏪"), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_badge("Estado Solucion", estado, color_estado, "✅"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Plan optimo ──
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Plan Optimo",
        "🏭 Resumen Oferta",
        "🏪 Resumen Demanda",
        "📊 Visualizaciones"
    ])

    with tab1:
        st.markdown("""
        <div style="font-size:16px;font-weight:600;color:#111827;margin-bottom:14px;
                    font-family:'Sora','Inter',sans-serif;">
            Plan Optimo de Distribucion
        </div>
        """, unsafe_allow_html=True)

        if res['plan']:
            df_plan = pd.DataFrame(res['plan'])
            df_plan.columns = ['Almacen', 'Cliente', 'Cantidad (cajas)', 'Costo Unit. (Bs.)', 'Costo Total (Bs.)']
            df_plan['Cantidad (cajas)'] = df_plan['Cantidad (cajas)'].apply(lambda x: f"{x:,.0f}")
            df_plan['Costo Unit. (Bs.)'] = df_plan['Costo Unit. (Bs.)'].apply(lambda x: f"{x:.2f}")
            df_plan['Costo Total (Bs.)'] = df_plan['Costo Total (Bs.)'].apply(lambda x: f"{x:,.2f}")
            st.dataframe(df_plan, use_container_width=True, hide_index=True)

            st.markdown(f"""
            <div style="
                background:#F0FDF4;
                border:1px solid #43A04740;
                border-radius:10px;
                padding:14px 20px;
                margin-top:12px;
                display:flex;
                align-items:center;
                gap:12px;
            ">
                <div style="font-size:24px;">💰</div>
                <div>
                    <div style="font-size:12px;color:#6B7280;font-weight:600;
                                text-transform:uppercase;letter-spacing:0.06em;">
                        Costo Total Minimo
                    </div>
                    <div style="font-size:22px;font-weight:700;color:#43A047;
                                font-family:'Sora','Inter',sans-serif;">
                        Bs. {res['costo_total']:,.2f}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("No hay rutas activas en la solucion.")

    with tab2:
        st.markdown("""
        <div style="font-size:16px;font-weight:600;color:#111827;margin-bottom:14px;
                    font-family:'Sora','Inter',sans-serif;">
            Resumen de Oferta por Almacen
        </div>
        """, unsafe_allow_html=True)

        df_oferta = pd.DataFrame(res['resumen_oferta'])
        df_oferta.columns = ['Almacen', 'Disponible (cajas)', 'Utilizada (cajas)', 'Restante (cajas)']
        df_oferta['Disponible (cajas)'] = df_oferta['Disponible (cajas)'].apply(lambda x: f"{x:,.0f}")
        df_oferta['Utilizada (cajas)'] = df_oferta['Utilizada (cajas)'].apply(lambda x: f"{x:,.0f}")
        df_oferta['Restante (cajas)'] = df_oferta['Restante (cajas)'].apply(lambda x: f"{x:,.0f}")
        st.dataframe(df_oferta, use_container_width=True, hide_index=True)

    with tab3:
        st.markdown("""
        <div style="font-size:16px;font-weight:600;color:#111827;margin-bottom:14px;
                    font-family:'Sora','Inter',sans-serif;">
            Resumen de Demanda por Cliente
        </div>
        """, unsafe_allow_html=True)

        df_dem = pd.DataFrame(res['resumen_demanda'])
        df_dem.columns = ['Cliente', 'Demanda (cajas)', 'Satisfecha (cajas)', 'Pendiente (cajas)']
        df_dem['Demanda (cajas)'] = df_dem['Demanda (cajas)'].apply(lambda x: f"{x:,.0f}")
        df_dem['Satisfecha (cajas)'] = df_dem['Satisfecha (cajas)'].apply(lambda x: f"{x:,.0f}")
        df_dem['Pendiente (cajas)'] = df_dem['Pendiente (cajas)'].apply(lambda x: f"{x:,.0f}")
        st.dataframe(df_dem, use_container_width=True, hide_index=True)

    with tab4:
        if res['plan']:
            st.markdown("""
            <div style="font-size:16px;font-weight:600;color:#111827;margin-bottom:18px;
                        font-family:'Sora','Inter',sans-serif;">
                Visualizaciones del Plan Optimo
            </div>
            """, unsafe_allow_html=True)

            col_v1, col_v2 = st.columns(2)
            with col_v1:
                fig_bar = crear_grafico_barras(res['plan'])
                st.plotly_chart(fig_bar, use_container_width=True)
            with col_v2:
                fig_pie = crear_grafico_circular(res['resumen_oferta'])
                st.plotly_chart(fig_pie, use_container_width=True)

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            fig_sankey = crear_sankey(res['plan'])
            st.plotly_chart(fig_sankey, use_container_width=True)

            st.markdown("""
            <div style="
                background:#F8FAFC;
                border:1px solid #E5E7EB;
                border-radius:10px;
                padding:14px 20px;
                font-size:13px;
                color:#6B7280;
                margin-top:8px;
            ">
                <b>Lectura del Diagrama Sankey:</b> Los nodos de la izquierda (oscuros) representan almacenes.
                Los nodos de la derecha (naranjas) representan clientes. El ancho de cada flujo es proporcional
                a la cantidad de cajas enviadas.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No hay datos suficientes para generar visualizaciones.")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: ACERCA DEL PROYECTO
# ─────────────────────────────────────────────────────────────────────────────
def pagina_acerca():
    page_header("Acerca del Proyecto", "Documentacion academica y tecnica del sistema", "ⓘ")

    col1, col2 = st.columns([2, 1])

    with col1:
        card("""
        <div style="font-size:15px;font-weight:600;color:#111827;margin-bottom:16px;">
            Descripcion del Proyecto
        </div>
        <div style="font-size:14px;color:#374151;line-height:1.8;">
            <b>EGGROUTE</b> es un sistema de optimizacion logistica desarrollado como proyecto
            final de la materia de <b>Investigacion Operativa</b>.
        </div>
        <div style="font-size:14px;color:#374151;line-height:1.8;margin-top:12px;">
            El sistema aplica el <b>Modelo de Transporte</b>, una tecnica clasica de
            Programacion Lineal, para resolver el problema de distribucion de huevos
            desde almacenes en <b>La Paz y El Alto</b> hacia distintos puntos de venta.
        </div>
        <div style="margin-top:20px;">
            <div style="font-size:13px;font-weight:700;color:#6B7280;text-transform:uppercase;
                        letter-spacing:0.07em;margin-bottom:12px;">Tecnologias Utilizadas</div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
                <div style="background:#F8FAFC;border:1px solid #E5E7EB;border-radius:8px;
                            padding:10px 14px;font-size:13px;color:#374151;">
                    <span style="font-weight:600;color:#FB8C00;">Python</span> — Lenguaje principal
                </div>
                <div style="background:#F8FAFC;border:1px solid #E5E7EB;border-radius:8px;
                            padding:10px 14px;font-size:13px;color:#374151;">
                    <span style="font-weight:600;color:#FB8C00;">Streamlit</span> — Interfaz web
                </div>
                <div style="background:#F8FAFC;border:1px solid #E5E7EB;border-radius:8px;
                            padding:10px 14px;font-size:13px;color:#374151;">
                    <span style="font-weight:600;color:#FB8C00;">SciPy</span> — Solver HiGHS
                </div>
                <div style="background:#F8FAFC;border:1px solid #E5E7EB;border-radius:8px;
                            padding:10px 14px;font-size:13px;color:#374151;">
                    <span style="font-weight:600;color:#FB8C00;">Plotly</span> — Visualizaciones
                </div>
                <div style="background:#F8FAFC;border:1px solid #E5E7EB;border-radius:8px;
                            padding:10px 14px;font-size:13px;color:#374151;">
                    <span style="font-weight:600;color:#FB8C00;">Pandas</span> — Datos tabulares
                </div>
                <div style="background:#F8FAFC;border:1px solid #E5E7EB;border-radius:8px;
                            padding:10px 14px;font-size:13px;color:#374151;">
                    <span style="font-weight:600;color:#FB8C00;">NumPy</span> — Calculo numerico
                </div>
            </div>
        </div>
        """)

    with col2:
        card("""
        <div style="font-size:15px;font-weight:600;color:#111827;margin-bottom:16px;">
            Contexto del Caso
        </div>
        <div style="display:flex;flex-direction:column;gap:8px;font-size:13.5px;color:#374151;">
            <div style="display:flex;gap:8px;align-items:flex-start;">
                <span style="color:#FB8C00;font-size:16px;">🏭</span>
                <div><b>Origenes:</b> Almacenes en El Alto y La Paz</div>
            </div>
            <div style="display:flex;gap:8px;align-items:flex-start;">
                <span style="color:#FB8C00;font-size:16px;">🏪</span>
                <div><b>Destinos:</b> Mercados y supermercados</div>
            </div>
            <div style="display:flex;gap:8px;align-items:flex-start;">
                <span style="color:#FB8C00;font-size:16px;">📦</span>
                <div><b>Producto:</b> Cajas de huevos</div>
            </div>
            <div style="display:flex;gap:8px;align-items:flex-start;">
                <span style="color:#FB8C00;font-size:16px;">💰</span>
                <div><b>Moneda:</b> Bolivianos (Bs.)</div>
            </div>
            <div style="display:flex;gap:8px;align-items:flex-start;">
                <span style="color:#FB8C00;font-size:16px;">🎯</span>
                <div><b>Objetivo:</b> Minimizar costo total de transporte</div>
            </div>
        </div>
        """)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        card("""
        <div style="font-size:15px;font-weight:600;color:#111827;margin-bottom:14px;">
            Fundamento Matematico
        </div>
        <div style="font-size:13px;color:#374151;line-height:1.75;">
            El <b>Problema de Transporte</b> es un caso especial de Programacion Lineal
            donde se busca la forma mas economica de mover un bien desde multiples
            origenes hacia multiples destinos.
        </div>
        <div style="font-size:13px;color:#374151;line-height:1.75;margin-top:10px;">
            SciPy usa el solver <b>HiGHS</b> (sucesor del metodo Simplex) para
            encontrar el optimo global en tiempo polinomial.
        </div>
        """)

    st.markdown("<br>", unsafe_allow_html=True)
    card("""
    <div style="font-size:15px;font-weight:600;color:#111827;margin-bottom:16px;">
        Estructura del Proyecto
    </div>
    <div style="background:#1F2937;border-radius:10px;padding:20px 24px;
                font-family:monospace;font-size:13px;color:#D1D5DB;line-height:2;">
        <span style="color:#9CA3AF;">/eggroute</span><br>
        <span style="color:#FB8C00;">├── app.py</span>
        <span style="color:#6B7280;font-size:12px;margin-left:12px;">— Aplicacion principal Streamlit</span><br>
        <span style="color:#43A047;">├── transporte.py</span>
        <span style="color:#6B7280;font-size:12px;margin-left:12px;">— Modelo de transporte con SciPy HiGHS</span><br>
        <span style="color:#3B82F6;">├── utils.py</span>
        <span style="color:#6B7280;font-size:12px;margin-left:12px;">— Graficos Plotly y utilidades</span><br>
        <span style="color:#8B5CF6;">├── styles.css</span>
        <span style="color:#6B7280;font-size:12px;margin-left:12px;">— Estilos visuales personalizados</span><br>
        <span style="color:#EC4899;">├── requirements.txt</span>
        <span style="color:#6B7280;font-size:12px;margin-left:12px;">— Dependencias del proyecto</span><br>
        <span style="color:#F59E0B;">└── README.md</span>
        <span style="color:#6B7280;font-size:12px;margin-left:12px;">— Documentacion del sistema</span>
    </div>
    """)


# ─────────────────────────────────────────────────────────────────────────────
# ROUTER
# ─────────────────────────────────────────────────────────────────────────────
p = pagina.strip()

if "Inicio" in p:
    pagina_inicio()
elif "Almacenes" in p:
    pagina_almacenes()
elif "Clientes" in p:
    pagina_clientes()
elif "Costos" in p:
    pagina_costos()
elif "Optimizacion" in p:
    pagina_optimizacion()
elif "Resultados" in p:
    pagina_resultados()
elif "Acerca" in p:
    pagina_acerca()



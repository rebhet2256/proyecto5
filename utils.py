"""
utils.py
Utilidades y funciones auxiliares para EGGROUTE.
Visualizaciones con Plotly (requiere: pip install plotly)
"""

import pandas as pd
import numpy as np

try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_OK = True
except ImportError:
    PLOTLY_OK = False

COLORES = {
    'sidebar': '#1F2937',
    'acento': '#FB8C00',
    'positivo': '#43A047',
    'fondo': '#F8FAFC',
    'tarjeta': '#FFFFFF',
    'texto': '#111827',
    'texto_claro': '#6B7280',
    'borde': '#E5E7EB',
    'peligro': '#EF4444',
    'advertencia': '#F59E0B',
    'info': '#3B82F6',
}

PALETA_PLOTLY = [
    '#FB8C00', '#43A047', '#1F2937', '#3B82F6',
    '#EF4444', '#8B5CF6', '#EC4899', '#14B8A6'
]

RGBA_LINKS = [
    'rgba(251,140,0,0.40)', 'rgba(67,160,71,0.40)',
    'rgba(31,41,55,0.35)',  'rgba(59,130,246,0.40)'
]


def _empty_fig():
    if not PLOTLY_OK:
        return None
    fig = go.Figure()
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    return fig


def crear_grafico_barras(plan, titulo="Distribucion de Cajas por Cliente"):
    if not PLOTLY_OK or not plan:
        return _empty_fig()

    df = pd.DataFrame(plan)
    df_g = df.groupby(['cliente', 'almacen'])['cantidad'].sum().reset_index()

    fig = px.bar(
        df_g,
        x='cliente',
        y='cantidad',
        color='almacen',
        title=titulo,
        labels={'cantidad': 'Cajas', 'cliente': 'Cliente', 'almacen': 'Almacen'},
        color_discrete_sequence=PALETA_PLOTLY,
        text='cantidad'
    )
    fig.update_traces(
        texttemplate='%{text:,.0f}',
        textposition='outside',
        marker_line_width=0
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter, sans-serif', color=COLORES['texto']),
        title=dict(font=dict(size=16, color=COLORES['texto']), x=0.02),
        legend=dict(bgcolor='rgba(255,255,255,0.8)', bordercolor=COLORES['borde'], borderwidth=1),
        xaxis=dict(showgrid=False, tickangle=-15),
        yaxis=dict(showgrid=True, gridcolor='rgba(229,231,235,0.5)', gridwidth=1),
        bargap=0.25,
        margin=dict(t=60, b=60, l=40, r=20)
    )
    return fig


def crear_grafico_circular(resumen_oferta, titulo="Participacion por Almacen"):
    if not PLOTLY_OK or not resumen_oferta:
        return _empty_fig()

    df = pd.DataFrame(resumen_oferta)
    fig = go.Figure(data=[go.Pie(
        labels=df['almacen'],
        values=df['oferta_utilizada'],
        hole=0.45,
        marker=dict(colors=PALETA_PLOTLY, line=dict(color='white', width=3)),
        textinfo='label+percent',
        textfont=dict(size=13),
        hovertemplate='<b>%{label}</b><br>Cajas: %{value:,.0f}<br>Participacion: %{percent}<extra></extra>'
    )])
    fig.update_layout(
        title=dict(text=titulo, font=dict(size=16, color=COLORES['texto']), x=0.02),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter, sans-serif', color=COLORES['texto']),
        legend=dict(bgcolor='rgba(255,255,255,0.8)', bordercolor=COLORES['borde'], borderwidth=1),
        margin=dict(t=60, b=20, l=20, r=20),
        annotations=[dict(
            text='Oferta<br>Utilizada', x=0.5, y=0.5,
            font=dict(size=13, color=COLORES['texto_claro']), showarrow=False
        )]
    )
    return fig


def crear_sankey(plan, titulo="Flujo de Distribucion"):
    if not PLOTLY_OK or not plan:
        return _empty_fig()

    almacenes = list(dict.fromkeys(p['almacen'] for p in plan))
    clientes  = list(dict.fromkeys(p['cliente']  for p in plan))
    all_nodes = almacenes + clientes
    node_idx  = {n: i for i, n in enumerate(all_nodes)}

    sources, targets, values, labels = [], [], [], []
    for p in plan:
        sources.append(node_idx[p['almacen']])
        targets.append(node_idx[p['cliente']])
        values.append(p['cantidad'])
        labels.append(f"{p['cantidad']:,.0f} cajas | Bs.{p['costo_total']:,.2f}")

    colores_nodos = ['#1F2937' if n in almacenes else '#FB8C00' for n in all_nodes]
    link_colors   = [RGBA_LINKS[s % len(RGBA_LINKS)] for s in sources]

    fig = go.Figure(data=[go.Sankey(
        arrangement='snap',
        node=dict(
            pad=20, thickness=28,
            line=dict(color='white', width=2),
            label=all_nodes, color=colores_nodos,
            hovertemplate='<b>%{label}</b><br>Flujo total: %{value:,.0f} cajas<extra></extra>'
        ),
        link=dict(
            source=sources, target=targets, value=values,
            label=labels, color=link_colors,
            hovertemplate='%{label}<extra></extra>'
        )
    )])
    fig.update_layout(
        title=dict(text=titulo, font=dict(size=16, color=COLORES['texto']), x=0.02),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter, sans-serif', size=13, color=COLORES['texto']),
        margin=dict(t=60, b=20, l=20, r=20),
        height=420
    )
    return fig


def crear_heatmap_costos(almacenes, clientes, costos, titulo="Matriz de Costos de Transporte"):
    if not PLOTLY_OK:
        return _empty_fig()

    nombres_a = [a['nombre'] for a in almacenes]
    nombres_c = [c['nombre'] for c in clientes]

    fig = go.Figure(data=go.Heatmap(
        z=costos, x=nombres_c, y=nombres_a,
        colorscale=[[0, '#43A047'], [0.5, '#FB8C00'], [1, '#EF4444']],
        text=[[f'Bs. {v:.2f}' for v in row] for row in costos],
        texttemplate='%{text}',
        textfont=dict(size=13, color='white'),
        hovertemplate='<b>%{y} -> %{x}</b><br>Costo: Bs. %{z:.2f}<extra></extra>',
        showscale=True,
        colorbar=dict(title='Costo (Bs.)', tickfont=dict(size=11))
    ))
    fig.update_layout(
        title=dict(text=titulo, font=dict(size=16, color=COLORES['texto']), x=0.02),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter, sans-serif', color=COLORES['texto']),
        xaxis=dict(side='bottom', tickangle=-20),
        margin=dict(t=60, b=60, l=120, r=20)
    )
    return fig


# ── Datos de ejemplo por defecto ──────────────────────────────────────────────
ALMACENES_DEFAULT = [
    {'nombre': 'El Alto',       'oferta': 3000},
    {'nombre': 'La Paz Centro', 'oferta': 2500},
]

CLIENTES_DEFAULT = [
    {'nombre': 'Mercado Rodriguez', 'demanda': 1200},
    {'nombre': 'Villa Dolores',     'demanda': 1500},
    {'nombre': '16 de Julio',       'demanda': 1000},
    {'nombre': 'Hipermaxi',         'demanda':  800},
    {'nombre': 'Ketal',             'demanda': 1000},
]

COSTOS_DEFAULT = [
    [1.5, 1.0, 0.5, 2.0, 1.8],
    [0.8, 1.8, 2.5, 1.0, 1.2],
]

# 🥚 EGGROUTE — Sistema de Optimización de Distribución de Huevos

Sistema de optimización logística que aplica el **Modelo de Transporte** de Investigación Operativa
para determinar la distribución óptima de cajas de huevos desde almacenes hacia clientes en La Paz y El Alto.

## Instalación

```bash
pip install streamlit pandas numpy scipy plotly openpyxl
streamlit run app.py
```

## Estructura del Proyecto

```
/eggroute
├── app.py          — Aplicación principal Streamlit (UI + páginas)
├── transporte.py   — Modelo de Transporte con scipy.optimize.linprog (HiGHS)
├── utils.py        — Visualizaciones Plotly y datos por defecto
├── styles.css      — Estilos CSS personalizados (sidebar, tarjetas, tablas)
├── requirements.txt
└── README.md
```

## Páginas del Sistema

| Página | Descripción |
|--------|-------------|
| Inicio | KPIs resumen y descripción del sistema |
| Almacenes | CRUD de almacenes con oferta disponible |
| Clientes | CRUD de clientes con demanda requerida |
| Costos de Transporte | Matriz de costos editable + heatmap |
| Optimización | Modelo matemático + botón de cálculo |
| Resultados | Plan óptimo, KPIs, Sankey, barras, circular |
| Acerca del Proyecto | Documentación académica |

## Método

- **Modelo de Transporte** (Investigación Operativa)
- **Programación Lineal** con función objetivo de minimización
- **Solver HiGHS** vía `scipy.optimize.linprog`
- Manejo automático de problemas **balanceados y desequilibrados**

## Tecnologías

- Python 3.10+ · Streamlit · SciPy (HiGHS) · Plotly · Pandas · NumPy

## Materia

Investigación Operativa — Universidad, La Paz, 2026

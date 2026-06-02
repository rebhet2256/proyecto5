"""
transporte.py
Modulo de optimizacion del modelo de transporte para EGGROUTE.
Utiliza scipy.optimize.linprog (Simplex/HiGHS) para resolver el modelo.
"""

import numpy as np
from scipy.optimize import linprog
from typing import List, Dict


def resolver_transporte(
    almacenes: List[Dict],
    clientes: List[Dict],
    costos: List[List[float]]
) -> Dict:
    """
    Resuelve el Problema de Transporte mediante Programacion Lineal.
    Usa scipy.optimize.linprog (solver HiGHS/Simplex revisado).

    Variables: x[i,j] = cajas enviadas desde almacen i al cliente j
    Objetivo:  Minimizar sum(c[i,j] * x[i,j])
    S.t.:      sum_j x[i,j] = s[i]  (oferta)
               sum_i x[i,j] = d[j]  (demanda)
               x[i,j] >= 0
    """
    n_a = len(almacenes)
    n_c = len(clientes)
    n_vars = n_a * n_c

    nombres_a = [a['nombre'] for a in almacenes]
    nombres_c = [c['nombre'] for c in clientes]
    ofertas   = [float(a['oferta']) for a in almacenes]
    demandas  = [float(c['demanda']) for c in clientes]

    oferta_total  = sum(ofertas)
    demanda_total = sum(demandas)
    balanceado    = abs(oferta_total - demanda_total) < 1e-6

    # Si no esta balanceado, agrandar con ficticio
    ofertas_m  = ofertas[:]
    demandas_m = demandas[:]
    costos_m   = [row[:] for row in costos]
    n_a_m, n_c_m = n_a, n_c
    nombre_a_m = nombres_a[:]
    nombre_c_m = nombres_c[:]

    if oferta_total > demanda_total:
        nombre_c_m.append("Cliente Ficticio")
        demandas_m.append(oferta_total - demanda_total)
        for i in range(n_a_m):
            costos_m[i].append(0.0)
        n_c_m += 1
    elif demanda_total > oferta_total:
        nombre_a_m.append("Almacen Ficticio")
        ofertas_m.append(demanda_total - oferta_total)
        costos_m.append([0.0] * n_c_m)
        n_a_m += 1

    n_vars_m = n_a_m * n_c_m

    def idx(i, j): return i * n_c_m + j

    # Vector de costos (funcion objetivo)
    c = np.array([costos_m[i][j] for i in range(n_a_m) for j in range(n_c_m)], dtype=float)

    # Restricciones de igualdad: oferta + demanda
    n_eq = n_a_m + n_c_m
    A_eq = np.zeros((n_eq, n_vars_m))
    b_eq = np.zeros(n_eq)

    # Restricciones de oferta: sum_j x[i,j] = s[i]
    for i in range(n_a_m):
        for j in range(n_c_m):
            A_eq[i, idx(i, j)] = 1.0
        b_eq[i] = ofertas_m[i]

    # Restricciones de demanda: sum_i x[i,j] = d[j]
    for j in range(n_c_m):
        for i in range(n_a_m):
            A_eq[n_a_m + j, idx(i, j)] = 1.0
        b_eq[n_a_m + j] = demandas_m[j]

    # Limites: x[i,j] >= 0
    bounds = [(0, None)] * n_vars_m

    # Resolver
    result = linprog(
        c,
        A_eq=A_eq,
        b_eq=b_eq,
        bounds=bounds,
        method='highs'
    )

    estado_raw = result.message
    if result.status == 0:
        estado = "OPTIMO"
    elif result.status == 2:
        estado = "INFACTIBLE"
    elif result.status == 3:
        estado = "NO ACOTADO"
    else:
        estado = "NO RESUELTO"

    costo_total = float(result.fun) if result.status == 0 else 0.0

    # Extraer solucion
    x_sol = result.x if result.status == 0 else np.zeros(n_vars_m)

    # Plan de distribucion (solo rutas reales, sin ficticias)
    plan = []
    for i in range(n_a):
        for j in range(n_c):
            val = x_sol[idx(i, j)]
            if val > 1e-6:
                plan.append({
                    'almacen': nombres_a[i],
                    'cliente': nombres_c[j],
                    'cantidad': round(val, 2),
                    'costo_unit': costos[i][j],
                    'costo_total': round(val * costos[i][j], 2)
                })

    # Resumen oferta
    resumen_oferta = []
    for i, alm in enumerate(nombres_a):
        utilizado = sum(x_sol[idx(i, j)] for j in range(n_c))
        resumen_oferta.append({
            'almacen': alm,
            'oferta_disponible': ofertas[i],
            'oferta_utilizada': round(utilizado, 2),
            'oferta_restante': round(ofertas[i] - utilizado, 2)
        })

    # Resumen demanda
    resumen_demanda = []
    for j, cli in enumerate(nombres_c):
        satisfecho = sum(x_sol[idx(i, j)] for i in range(n_a))
        resumen_demanda.append({
            'cliente': cli,
            'demanda_requerida': demandas[j],
            'demanda_satisfecha': round(satisfecho, 2),
            'demanda_pendiente': round(demandas[j] - satisfecho, 2)
        })

    return {
        'estado': estado,
        'estado_raw': estado_raw,
        'costo_total': round(costo_total, 2),
        'plan': plan,
        'resumen_oferta': resumen_oferta,
        'resumen_demanda': resumen_demanda,
        'oferta_total': oferta_total,
        'demanda_total': demanda_total,
        'balanceado': balanceado,
        'n_variables': n_a_m * n_c_m,
        'n_restricciones': n_a_m + n_c_m
    }


def validar_datos(almacenes, clientes, costos):
    errores = []
    advertencias = []

    if len(almacenes) == 0:
        errores.append("Debe ingresar al menos un almacen.")
    if len(clientes) == 0:
        errores.append("Debe ingresar al menos un cliente.")

    for a in almacenes:
        if a.get('oferta', 0) <= 0:
            errores.append(f"La oferta del almacen '{a['nombre']}' debe ser mayor a 0.")

    for c in clientes:
        if c.get('demanda', 0) <= 0:
            errores.append(f"La demanda del cliente '{c['nombre']}' debe ser mayor a 0.")

    if len(costos) != len(almacenes):
        errores.append("La matriz de costos no coincide con el numero de almacenes.")
    else:
        for i, row in enumerate(costos):
            if len(row) != len(clientes):
                errores.append(f"La fila {i+1} de costos no coincide con el numero de clientes.")
            for v in row:
                if v < 0:
                    errores.append(f"Los costos no pueden ser negativos.")
                    break

    if not errores:
        oferta_t  = sum(a['oferta'] for a in almacenes)
        demanda_t = sum(c['demanda'] for c in clientes)
        if abs(oferta_t - demanda_t) > 1e-6:
            advertencias.append(
                f"Problema desequilibrado: Oferta ({oferta_t:,}) != Demanda ({demanda_t:,}). "
                "Se agregara una variable ficticia automaticamente."
            )

    return errores, advertencias

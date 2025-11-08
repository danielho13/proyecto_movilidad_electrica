# -*- coding: utf-8 -*-
"""
graficos.py
------------
Módulo de figuras para el dashboard de movilidad eléctrica.

• Todas las figuras devuelven plotly.graph_objects.Figure (o None).
• Plotly Express para construir charts; tipado con go.Figure.
• Carga única de datos; rutas relativas por defecto.
• Comentarios por bloque para identificar cada visualización.
• Soporta filtro por año para Top-10, Scatters y Coroplético.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import json
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# ================================
# 0) Utilidades y rutas
# ================================
def get_paths(data_dir: Path | str = "C:\Estudios\Talento_Tech\Proyecto_Talento_Tech\proyecto_movilidad_electrica\datos\limpios", geo_dir: Path | str = "C:\Estudios\Talento_Tech\Proyecto_Talento_Tech\proyecto_movilidad_electrica\geodatos") -> dict[str, Path]:
    data_dir = Path(data_dir)
    geo_dir = Path(geo_dir)
    return {
        "vehiculos_pib": data_dir / "vehiculos_pib.csv",
        "demografia": data_dir / "demografia_departamental.csv",
        "estaciones_epm_antioquia": data_dir / "estaciones_epm_antioquia.csv",
        "vehiculos_ev_hev_limpio": data_dir / "vehiculos_ev_hev_limpio.csv",  # opcional
        "geo_departamentos": geo_dir / "departamentos_colombia.geojson",       # para coroplético
    }


def list_years(data_dir: Path | str = "datos/limpios") -> list[int]:
    """
    Devuelve una lista ordenada de años únicos presentes en vehiculos_pib.csv.
    Útil para poblar el <select> del filtro en Flask.
    """
    p = Path(data_dir) / "vehiculos_pib.csv"
    df = pd.read_csv(p, encoding="utf-8")
    years = (
        pd.to_numeric(df["anio"], errors="coerce")
        .dropna()
        .astype(int)
        .unique()
        .tolist()
    )
    return sorted(years)


# =======================================
# 1) Carga y limpieza de datasets base
# =======================================
def load_base_data(paths: dict[str, Path]) -> tuple[pd.DataFrame, pd.DataFrame, Optional[pd.DataFrame]]:
    """Carga CSVs principales y aplica limpieza mínima."""
    # --- Vehículos + PIB ---
    veh_pib = pd.read_csv(paths["vehiculos_pib"], encoding="utf-8")
    veh_pib["anio"] = pd.to_numeric(veh_pib["anio"], errors="coerce")
    for c in ("ev_registrados", "hev_registrados", "pib_const_2015"):
        if c in veh_pib.columns:
            veh_pib[c] = pd.to_numeric(veh_pib[c], errors="coerce")
    veh_pib["departamento"] = (
        veh_pib["departamento"].astype(str).str.upper().str.strip()
        .str.replace(r"\bBOGOTÁ,?\s*D\.?C\.?\b", "BOGOTA", regex=True)
    )
    veh_pib["total_ev_hev"] = veh_pib[["ev_registrados", "hev_registrados"]].fillna(0).sum(axis=1)

    # --- Demografía (estática en el tiempo) ---
    demo = pd.read_csv(paths["demografia"], encoding="utf-8")
    demo["departamento"] = (
        demo["departamento"].astype(str).str.upper().str.strip()
        .str.replace(r"\bBOGOTÁ,?\s*D\.?C\.?\b", "BOGOTA", regex=True)
    )
    for c in ("poblacion_2018", "densidad_hab_km2", "area_km2"):
        if c in demo.columns:
            demo[c] = pd.to_numeric(demo[c], errors="coerce")

    # --- Estaciones (Antioquia) ---
    est: Optional[pd.DataFrame]
    try:
        est = pd.read_csv(paths["estaciones_epm_antioquia"], encoding="utf-8")
        est["tipo_estacion"] = est["tipo_estacion"].astype(str).str.strip().str.title()
        est["ciudad"] = est["ciudad"].astype(str).str.strip().str.title()
        est["estacion"] = est["estacion"].astype(str).str.strip().str.title()
        est["latitud"] = pd.to_numeric(est["latitud"], errors="coerce")
        est["longitud"] = pd.to_numeric(est["longitud"], errors="coerce")
        est = est.dropna(subset=["latitud", "longitud"])
    except FileNotFoundError:
        est = None

    return veh_pib, demo, est


# ==========================================================
# 2) Figuras “nacionales”: evolución y Top-10 departamentos
# ==========================================================
def fig_evolucion_nacional(veh_pib: pd.DataFrame, anio: int | None = None) -> go.Figure:
    """
    📈 Evolución nacional de EV y HEV por año (líneas).
    Siempre muestra toda la serie; si 'anio' viene, se resalta con una línea vertical.
    """
    nacional = (
        veh_pib.groupby("anio")[["ev_registrados", "hev_registrados"]]
        .sum()
        .reset_index()
        .sort_values("anio")
    )

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=nacional["anio"], y=nacional["ev_registrados"],
        mode="lines+markers", name="EV registrados"
    ))
    fig.add_trace(go.Scatter(
        x=nacional["anio"], y=nacional["hev_registrados"],
        mode="lines+markers", name="HEV registrados"
    ))

    # Resaltado opcional de año seleccionado
    if anio is not None and int(anio) in set(nacional["anio"].astype(int)):
        x = int(anio)
        fig.add_vline(x=x, line_width=2, line_dash="dot", line_color="#666")
        fig.add_annotation(
            x=x,
            y=max(nacional["ev_registrados"].max(), nacional["hev_registrados"].max()),
            text=f"Año {x}",
            showarrow=False, yshift=15, font=dict(color="#444")
        )

    fig.update_layout(
        title="Evolución nacional de vehículos eléctricos e híbridos registrados",
        xaxis_title="Año",
        yaxis_title="Número de vehículos",
        hovermode="x unified",
        template="plotly_white",
        legend=dict(title="", orientation="h", y=-0.2)
    )
    return fig


def fig_top10_departamentos(veh_pib: pd.DataFrame, anio: int | None = None) -> go.Figure:
    """
    🏆 Top-10 departamentos por total EV+HEV (último año o año seleccionado).
    """
    ultimo_anio = int(anio) if anio is not None else int(veh_pib["anio"].max())
    df_ultimo = veh_pib.loc[veh_pib["anio"] == ultimo_anio].copy()
    df_ultimo["total_ev_hev"] = df_ultimo[["ev_registrados", "hev_registrados"]].fillna(0).sum(axis=1)

    top10 = (
        df_ultimo.nlargest(10, "total_ev_hev")
        .sort_values("total_ev_hev", ascending=True)
    )

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=top10["departamento"],
        x=top10["ev_registrados"],
        name="EV",
        orientation="h",
        hovertemplate="EV registrados: %{x}<extra></extra>"
    ))
    fig.add_trace(go.Bar(
        y=top10["departamento"],
        x=top10["hev_registrados"],
        name="HEV",
        orientation="h",
        hovertemplate="HEV registrados: %{x}<extra></extra>"
    ))
    fig.update_layout(
        barmode="stack",
        title=f"Top 10 departamentos con más vehículos EV/HEV registrados ({ultimo_anio})",
        xaxis_title="Número de vehículos",
        yaxis_title="Departamento",
        template="plotly_white",
        legend=dict(title="", orientation="h", y=-0.2)
    )
    return fig


# ==================================================================
# 3) Figuras “territoriales”: relaciones PIB/Densidad vs Adopción
# ==================================================================
def _prep_territorial(veh_pib: pd.DataFrame, demo: pd.DataFrame, anio: int | None = None) -> tuple[pd.DataFrame, int]:
    """
    Une vehículos+PIB con demografía y calcula indicadores por departamento.
    Permite filtrar por año (si no se pasa, usa el último disponible).
    """
    df = veh_pib.merge(
        demo[["departamento", "codigo_depto", "area_km2", "poblacion_2018", "densidad_hab_km2"]],
        on="departamento", how="left"
    )
    df["total_ev_hev"] = df[["ev_registrados", "hev_registrados"]].fillna(0).sum(axis=1)
    df["pib_per_capita"] = pd.to_numeric(df["pib_const_2015"], errors="coerce") / df["poblacion_2018"]
    df["adopcion_ev_hev_por_1000hab"] = (df["total_ev_hev"] / df["poblacion_2018"]) * 1000

    anio_sel = int(anio) if anio is not None else int(df["anio"].max())
    df_anio = df[df["anio"] == anio_sel].copy()

    # Sanitizar
    for col in ("pib_per_capita", "adopcion_ev_hev_por_1000hab", "poblacion_2018", "densidad_hab_km2"):
        df_anio[col] = pd.to_numeric(df_anio[col], errors="coerce")
    df_anio = df_anio.replace([np.inf, -np.inf], np.nan)
    df_anio = df_anio.dropna(subset=["pib_per_capita", "adopcion_ev_hev_por_1000hab"])

    # Tamaño de burbuja seguro (evitar 0)
    med_pop = df_anio["poblacion_2018"].median()
    df_anio["poblacion_2018_size"] = (
        df_anio["poblacion_2018"].fillna(med_pop).clip(lower=max(1.0, 0.1 * med_pop))
    )

    return df_anio, anio_sel


def fig_scatter_pib_vs_adopcion(veh_pib: pd.DataFrame, demo: pd.DataFrame, anio: int | None = None) -> go.Figure:
    """💰 Dispersión: PIB per cápita vs adopción EV+HEV por 1000 hab (año seleccionado)."""
    df_anio, anio_max = _prep_territorial(veh_pib, demo, anio)
    fig = px.scatter(
        df_anio,
        x="pib_per_capita",
        y="adopcion_ev_hev_por_1000hab",
        size="poblacion_2018_size",
        size_max=40,
        color="departamento",
        hover_data={
            "codigo_depto": True,
            "area_km2": True,
            "densidad_hab_km2": True,
            "poblacion_2018": True
        },
        title=f"Relación PIB per cápita y adopción EV/HEV ({anio_max})",
        labels={
            "pib_per_capita": "PIB per cápita (constante 2015)",
            "adopcion_ev_hev_por_1000hab": "EV+HEV por cada 1000 hab"
        },
        template="plotly_white",
        trendline="ols"
    )
    return fig


def fig_scatter_densidad_vs_adopcion(veh_pib: pd.DataFrame, demo: pd.DataFrame, anio: int | None = None) -> go.Figure:
    """🏙️ Dispersión: Densidad poblacional vs adopción EV+HEV por 1000 hab (año seleccionado)."""
    df_anio, anio_max = _prep_territorial(veh_pib, demo, anio)
    fig = px.scatter(
        df_anio,
        x="densidad_hab_km2",
        y="adopcion_ev_hev_por_1000hab",
        size="poblacion_2018_size",
        size_max=40,
        color="departamento",
        hover_data={
            "codigo_depto": True,
            "area_km2": True,
            "pib_per_capita": True,
            "poblacion_2018": True
        },
        title=f"Densidad poblacional vs adopción EV/HEV ({anio_max})",
        labels={
            "densidad_hab_km2": "Densidad (hab/km²)",
            "adopcion_ev_hev_por_1000hab": "EV+HEV por cada 1000 hab"
        },
        template="plotly_white",
        trendline="ols"
    )
    return fig


# =========================================
# 4) Mapas: estaciones y coroplético EV+HEV
# =========================================
def fig_mapa_estaciones_antioquia(estaciones: pd.DataFrame | None) -> go.Figure | None:
    """
    ⚡ Mapa de puntos de estaciones EPM (Antioquia).
    Devuelve None si no hay dataset de estaciones.
    """
    if estaciones is None or estaciones.empty:
        return None

    fig = px.scatter_mapbox(
        estaciones,
        lat="latitud",
        lon="longitud",
        hover_name="estacion",
        hover_data={"tipo_estacion": True, "ciudad": True},
        color="tipo_estacion",
        title="Estaciones de carga EPM - Antioquia",
        mapbox_style="open-street-map",
        zoom=7,
        center={"lat": 6.25, "lon": -75.57},
        height=600
    )
    fig.update_traces(marker=dict(size=10, opacity=0.8))
    return fig


def fig_mapa_coropletico_ev_hev(veh_pib: pd.DataFrame, geojson_path: Path | str, anio: int | None = None) -> go.Figure | None:
    """
    🗺️ Mapa coroplético: total EV+HEV por departamento (año seleccionado).
    Requiere GeoJSON con propiedad 'DPTO_CCDGO' como identificador.
    """
    geojson_path = Path(geojson_path)
    if not geojson_path.exists():
        return None

    with open(geojson_path, "r", encoding="utf-8") as f:
        gj = json.load(f)

    veh = veh_pib.copy()
    veh["anio"] = pd.to_numeric(veh["anio"], errors="coerce")
    veh["ev_registrados"] = pd.to_numeric(veh["ev_registrados"], errors="coerce").fillna(0)
    veh["hev_registrados"] = pd.to_numeric(veh["hev_registrados"], errors="coerce").fillna(0)
    veh["total_ev_hev"] = veh["ev_registrados"] + veh["hev_registrados"]

    anio_max = int(anio) if anio is not None else int(veh["anio"].max())
    veh_map = (
        veh.loc[veh["anio"] == anio_max]
        .groupby(["codigo_departamento", "departamento"], as_index=False)["total_ev_hev"]
        .sum()
    )

    # Si tu GeoJSON usa DPTO_CCDGO con ceros a la izquierda, intenta igualar
    veh_map["codigo_departamento"] = veh_map["codigo_departamento"].astype(str).str.extract(r"(\d+)", expand=False)

    codes_gj = {feat["properties"].get("DPTO_CCDGO") for feat in gj["features"] if "properties" in feat}
    veh_codes_zfill = set(veh_map["codigo_departamento"].dropna().str.zfill(2))
    veh_codes_strip = set(veh_map["codigo_departamento"].dropna().str.lstrip("0"))
    inter_zfill = len(veh_codes_zfill & codes_gj)
    inter_strip = len(veh_codes_strip & codes_gj)
    if inter_zfill >= inter_strip:
        veh_map["codigo_match"] = veh_map["codigo_departamento"].str.zfill(2)
        feature_key = "properties.DPTO_CCDGO"
        loc_col = "codigo_match"
    else:
        veh_map["codigo_match"] = veh_map["codigo_departamento"].str.lstrip("0")
        feature_key = "properties.DPTO_CCDGO"
        loc_col = "codigo_match"

    fig = px.choropleth_mapbox(
        veh_map,
        geojson=gj,
        locations=loc_col,
        featureidkey=feature_key,
        color="total_ev_hev",
        color_continuous_scale="Viridis",
        range_color=(0, veh_map["total_ev_hev"].max() * 1.05),
        mapbox_style="carto-positron",
        zoom=4.3,
        center={"lat": 4.5, "lon": -74.1},
        opacity=0.8,
        labels={"total_ev_hev": "Vehículos EV+HEV"},
        title=f"Adopción de vehículos EV+HEV por departamento ({anio_max})"
    )

    fig.update_traces(
        hovertemplate="<b>%{customdata[0]}</b><br>Total EV+HEV: %{z:,}<extra></extra>",
        customdata=np.stack([veh_map["departamento"]], axis=-1)
    )
    fig.update_layout(margin={"r":0,"t":60,"l":0,"b":0})
    return fig


# ==================================================
# 5) Helper para construir todas las figuras
# ==================================================
def build_all_figures(
    data_dir: Path | str = "datos/limpios",
    geo_dir: Path | str = "geodatos",
    anio: int | None = None
) -> dict[str, go.Figure | None]:
    """
    Construye todas las figuras listas para incrustar en Flask.
    Si 'anio' viene, filtra Top-10, Scatters y Coroplético por ese año.
    La evolución siempre muestra toda la serie, con posible resaltado del año.
    """
    paths = get_paths(data_dir, geo_dir)
    veh_pib, demo, est = load_base_data(paths)

    return {
        "evolucion": fig_evolucion_nacional(veh_pib, anio=None if anio is None else int(anio)),
        "top10": fig_top10_departamentos(veh_pib, anio),
        "pib_vs_adopcion": fig_scatter_pib_vs_adopcion(veh_pib, demo, anio),
        "densidad_vs_adopcion": fig_scatter_densidad_vs_adopcion(veh_pib, demo, anio),
        "mapa_estaciones": fig_mapa_estaciones_antioquia(est),
        "mapa_coropletico": fig_mapa_coropletico_ev_hev(veh_pib, paths["geo_departamentos"], anio),
    }


# ==================================================
# 6) Ejecución directa (prueba local)
# ==================================================
if __name__ == "__main__":
    # Prueba rápida fuera de Flask (abre un visor para cada figura disponible).
    from plotly.io import show

    figs = build_all_figures()
    for name, fig in figs.items():
        if fig is not None:
            print(f"Mostrando: {name}")
            show(fig)

# export_static.py
from pathlib import Path
from graficos import build_all_figures

def export_static(output="entregas/dashboard_estatico.html", embed_js=True, anio=None):
    figs = build_all_figures(anio=anio)
    parts = []
    for name, fig in figs.items():
        if fig is None:
            continue
        # True = embebe plotly.js (100% offline). "cdn" = requiere internet.
        parts.append(f'<h2 style="font-family:system-ui;margin:16px 0">{name.replace("_"," ").title()}</h2>')
        parts.append(fig.to_html(full_html=False, include_plotlyjs=True if embed_js else "cdn"))

    html = f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<title>Dashboard estático</title></head>
<body style="margin:24px;background:#f8f9fb">{''.join(parts)}</body></html>"""

    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print("✅ Archivo generado:", out.resolve())

if __name__ == "__main__":
    export_static()  # cambia anio=2022 si quieres fijar un año

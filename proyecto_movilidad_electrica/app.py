from flask import Flask, render_template, request
from graficos import build_all_figures, list_years


app = Flask(__name__)

@app.route("/")
def index():
    # Año seleccionado por GET (?anio=2022)
    anio = request.args.get("anio", type=int)

    # Lista de años para el <select>
    years = list_years()          # p.ej. [2018, 2019, 2020, 2021, 2022]
    if anio is not None and anio not in years:
        anio = None               # valor inválido -> fallback al último dentro de graficos.py

    figs = build_all_figures(anio=anio)
    html_figs = {k: (v.to_html(full_html=False, include_plotlyjs="cdn") if v is not None else None)
                 for k, v in figs.items()}

    return render_template("index.html",
                           years=years, anio_selected=anio,
                           **html_figs)

if __name__ == "__main__":
    app.run(debug=True)


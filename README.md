# 🚗 Análisis de Adopción de Vehículos Eléctricos e Híbridos en Colombia

### 📊 Proyecto final – Nivel Explorador: Análisis de Datos  
**Línea de investigación:** Transición Energética Justa  

---

## 🌎 Descripción del proyecto

Este proyecto analiza la evolución de la adopción de **vehículos eléctricos (EV)** e **híbridos (HEV)** en los departamentos de Colombia entre 2019 y 2025.  
Se estudian las relaciones entre la tasa de adopción y factores territoriales como el **PIB per cápita**, la **densidad poblacional** y la **infraestructura de carga eléctrica**.

El trabajo combina **análisis de datos, visualización interactiva y despliegue web** para aportar evidencia sobre el avance de la movilidad eléctrica en el país.

---

## 🧭 Objetivos

- Analizar la evolución del parque vehicular eléctrico e híbrido en Colombia.  
- Relacionar la adopción de EV/HEV con variables socioeconómicas y territoriales.  
- Visualizar los resultados mediante dashboards interactivos.  
- Publicar el análisis completo en una aplicación web accesible en línea.

---

## 🧹 Limpieza y preparación de datos

1. **Normalización de nombres** de departamentos (mayúsculas y sin tildes).  
2. **Conversión numérica** de valores (puntos decimales uniformes).  
3. **Unificación de fuentes** (merge) por código o nombre departamental.  
4. **Cálculo de indicadores derivados:**
   - `pib_per_capita = PIB / población`
   - `adopcion_ev_hev_por_1000hab = (EV + HEV) / población * 1000`
   - `densidad_hab_km2 = población / área`

---

## 📈 Visualizaciones

El archivo `graficos.py` genera las siguientes figuras interactivas (Plotly):

- Evolución nacional EV/HEV (2019–2025).  
- Top-10 departamentos con mayor adopción.  
- Dispersión PIB per cápita vs adopción.  
- Dispersión densidad poblacional vs adopción.  
- Mapa de estaciones de carga (caso Antioquia – EPM).  
- Mapa coroplético de adopción EV/HEV por departamento.

---

## 🌐 Dashboard Web

El dashboard fue desarrollado con **Flask** y desplegado en **Render**.

🔗 **Aplicación en línea:** [https://proyecto-movilidad.onrender.com](https://proyecto-movilidad.onrender.com)  
💾 **Repositorio en GitHub:** [https://github.com/danielho13/proyecto_movilidad_electrica](https://github.com/danielho13/proyecto_movilidad_electrica)

El servidor `app.py` carga los datos limpios, genera las figuras y las envía a las plantillas HTML mediante `render_template`.  
Las gráficas se renderizan en el navegador usando **Plotly.js**, garantizando interactividad total.

---

## 🧰 Tecnologías utilizadas

| Categoría | Herramientas |
|------------|---------------|
| Lenguaje principal | Python 3.11 |
| Librerías de análisis | pandas, numpy |
| Visualización | plotly, matplotlib |
| Web | Flask, Bootstrap |
| Despliegue | Render + GitHub |
| Gestión de dependencias | pip / requirements.txt |

---

## 📑 Resultados destacados

- Crecimiento exponencial del parque EV/HEV desde 2021.  
- Fuerte concentración de adopción en Bogotá y Antioquia.  
- Correlación positiva entre PIB per cápita y tasa de adopción.  
- Infraestructura de carga concentrada en el Valle de Aburrá.  

---



# streamlit_app.py
import streamlit as st
import pandas as pd
import altair as alt
import json
from textwrap import shorten

st.set_page_config(page_title="Normativa Calidad del Aire - Perú", layout="wide")

# ---------- Utilidades ----------
@st.cache_data
def load_eca():
    try:
        with open("eca.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

@st.cache_data
def timeline_hitos():
    # Hitos principales (incluye normas generales de ambiente)
    return [
        {"year": 1990, "titulo": "Ley General del Ambiente (Ley N° 28611)", "descripcion": "Marco general para la gestión ambiental en el Perú (derecho a un ambiente sano).", "link": ""},
        {"year": 2001, "titulo": "D.S. N.º 074-2001-PCM", "descripcion": "Reglamento de Estándares Nacionales de Calidad Ambiental del Aire (norma histórica).", "link": ""},
        {"year": 2003, "titulo": "D.S. N.º 003-2008-MINAM / modificaciones", "descripcion": "Ajustes previos a los ECA vigentes.", "link": ""},
        {"year": 2013, "titulo": "D.S. N.º 006-2013-MINAM", "descripcion": "Disposiciones complementarias para la aplicación de ECA (ej. SO2).", "link": ""},
        {"year": 2017, "titulo": "D.S. N.º 003-2017-MINAM", "descripcion": "Aprobar ECA para aire (PM2.5, PM10, NO2, SO2, CO, O3, Hg, Pb, H2S, Benceno, etc.).", "link": ""},
        {"year": 2019, "titulo": "D.S. N.º 010-2019-MINAM", "descripcion": "Protocolo Nacional de Monitoreo de la Calidad Ambiental del Aire (estandarización técnica del monitoreo).", "link": ""},
        {"year": 2021, "titulo": "Ley N.º 31189", "descripcion": "Ley sobre prevención y atención de salud afectada por contaminación con metales pesados.", "link": ""},
        {"year": 2023, "titulo": "D.S. N.º 011-2023-MINAM", "descripcion": "Aprobar ECA de As, Cd y Cr en PM10 (incorpora metales a ECA del aire).", "link": ""}
    ]

def make_timeline_chart(df):
    base = alt.Chart(df).encode(x=alt.X('year:O', title='Año'))
    points = base.mark_point(filled=True, size=150).encode(
        tooltip=['year', 'titulo', 'descripcion']
    )
    rule = base.mark_rule(color='lightgray')
    text = base.mark_text(align='center', dy=-30, fontSize=11).encode(text='titulo')
    return (rule + points + text).properties(height=220)

# ---------- Cargar datos ----------
ECA = load_eca()
hitos = timeline_hitos()
df_hitos = pd.DataFrame(hitos)

# ---------- Layout ----------
st.title("🌬️ Marco Normativo y Evolución — Calidad del Aire (Perú)")
st.write("Normativa, ECA vigentes, y línea de tiempo con los hitos legales relevantes. Fuentes oficiales: MINAM (D.S. 003-2017, D.S. 011-2023), Protocolo de Monitoreo (2019), Leyes generales.") 

st.sidebar.header("Navegación")
op = st.sidebar.radio("Ir a:", ["Resumen", "Línea de tiempo", "ECA (tabla)", "Comparación / Cambios", "Fuentes oficiales"])

# ---------- Resumen ----------
if op == "Resumen":
    st.header("Resumen ejecutivo")
    st.write("""
    - Este visor presenta los Estándares de Calidad Ambiental (ECA) para aire en el Perú y su evolución normativa.  
    - Se incluyen los ECA aprobados por D.S. N.º 003-2017-MINAM y la ampliación para metales en PM10 por D.S. N.º 011-2023-MINAM.  
    - El Protocolo Nacional de Monitoreo (D.S. 010-2019-MINAM) estandariza la medición.  
    """)
    st.markdown("**Consejo práctico:** carga un CSV público con mediciones para comparar tus datos con los ECA (la app puede añadirse para leer CSVs).")

# ---------- Línea de tiempo ----------
elif op == "Línea de tiempo":
    st.header("📆 Línea de tiempo normativa")
    st.write("Hitos legales y normativos relevantes (incluye normas generales de ambiente).")
    st.altair_chart(make_timeline_chart(df_hitos), use_container_width=True)
    st.markdown("**Hitos (breve):**")
    for h in hitos:
        st.write(f"- **{h['year']}** — {h['titulo']}: {h['descripcion']}")

# ---------- ECA (tabla) ----------
elif op == "ECA (tabla)":
    st.header("Estándares de Calidad Ambiental (ECA) — Valores cargados")
    if not ECA:
        st.warning("No se encontró `eca.json` en la raíz. Sube el archivo `eca.json` con los ECA (formato JSON).")
    else:
        # transformar para tabla
        rows = []
        for param, specs in ECA.items():
            for periodo, valores in specs.items():
                if periodo == "source":
                    continue
                # periodo puede ser '24h','annual','1h', etc.
                if isinstance(valores, dict):
                    val = valores.get("value")
                    unit = valores.get("unit", "")
                    crit = valores.get("criteria", "")
                else:
                    val = valores
                    unit = ""
                    crit = ""
                rows.append({"Parámetro": param, "Periodo": periodo, "Valor": val, "Unidad": unit, "Criterio": crit, "Fuente": specs.get("source","")})
        df = pd.DataFrame(rows)
        st.dataframe(df.sort_values(["Parámetro","Periodo"]).reset_index(drop=True))

# ---------- Comparación / Cambios ----------
elif op == "Comparación / Cambios":
    st.header("Comparación de cambios normativos (qué se añadió / modificó)")
    st.write("En 2017 se aprobaron los ECA generales que reúnen la mayoría de parámetros. En 2023 se incorporaron **metales** específicos en PM10 (As, Cd, Cr).")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("ECA base (2017) — ejemplos")
        st.write("- PM2.5: 24h=50 µg/m³ / anual=25 µg/m³")
        st.write("- PM10: 24h=100 µg/m³ / anual=50 µg/m³")
        st.write("- NO2: 1h=200 µg/m³ / anual=100 µg/m³")
    with col2:
        st.subheader("Novedades 2023 (metales en PM10)")
        st.write("- Arsénico (As) en PM10: 24h=0.3 µg/m³; anual=0.023 µg/m³")
        st.write("- Cadmio (Cd) en PM10: 24h=0.09 µg/m³; anual=0.018 µg/m³")
        st.write("- Cromo (Cr) en PM10: 24h=0.5 µg/m³; anual=0.11 µg/m³")
    st.markdown("**Interpretación:** los ECA de 2017 cubren los principales contaminantes; el D.S. 011-2023 completa la regulación incorporando metales en PM10. Los instrumentos de gestión (IGA/estudios) deben adaptarse progresivamente a estos valores.")

# ---------- Fuentes oficiales ----------
elif op == "Fuentes oficiales":
    st.header("Fuentes y referencias (documentos oficiales)")
    st.markdown("""
    - Decreto Supremo N.º 003-2017-MINAM (ECA para aire).  
    - Decreto Supremo N.º 011-2023-MINAM (ECA As, Cd, Cr en PM10).  
    - Decreto Supremo N.º 010-2019-MINAM (Protocolo Nacional de Monitoreo de la Calidad Ambiental del Aire).  
    - Ley N.º 28611 (Ley General del Ambiente).  
    - Ley N.º 31189 (prevención y atención por contaminación con metales pesados).  
    """)
    st.write("Enlaces y documentos oficiales referenciados en la app (ver README del repositorio para enlaces directos).")

# pie
st.caption("Datos y ECA: D.S. 003-2017-MINAM; D.S. 011-2023-MINAM; Protocolo 010-2019-MINAM. Actualizado hasta 2023.")


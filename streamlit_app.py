# streamlit_app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from textwrap import dedent

# Intentar importar FPDF para generar PDFs
try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except Exception:
    FPDF_AVAILABLE = False

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(
    page_title="Marco Normativo - Calidad del Aire (Perú)",
    page_icon="🌬️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------
# DATOS EMBEBIDOS (ECA, LMP, TIMELINE, NORMAS)
# -------------------------
# ECA — Estándares de Calidad Ambiental para aire en Perú
ECA = {
    "PM2.5": {
        "24h": {"value": 50, "unit": "µg/m³", "source": "D.S. N° 003-2017-MINAM"},
        "anual": {"value": 25, "unit": "µg/m³", "source": "D.S. N° 003-2017-MINAM"}
    },
    "PM10": {
        "24h": {"value": 100, "unit": "µg/m³", "source": "D.S. N° 003-2017-MINAM"},
        "anual": {"value": 50, "unit": "µg/m³", "source": "D.S. N° 003-2017-MINAM"}
    },
    "SO2": {
        "1h": {"value": 350, "unit": "µg/m³", "source": "D.S. N° 003-2017-MINAM"},
        "24h": {"value": 125, "unit": "µg/m³", "source": "D.S. N° 003-2017-MINAM"},
        "anual": {"value": 50, "unit": "µg/m³", "source": "D.S. N° 003-2017-MINAM"}
    },
    "NO2": {
        "1h": {"value": 200, "unit": "µg/m³", "source": "D.S. N° 003-2017-MINAM"},
        "anual": {"value": 40, "unit": "µg/m³", "source": "D.S. N° 003-2017-MINAM"}
    },
    "CO": {
        "1h": {"value": 30, "unit": "mg/m³", "source": "D.S. N° 003-2017-MINAM"},
        "8h": {"value": 10, "unit": "mg/m³", "source": "D.S. N° 003-2017-MINAM"}
    },
    "O3": {
        "1h": {"value": 180, "unit": "µg/m³", "source": "D.S. N° 003-2017-MINAM"},
        "8h": {"value": 100, "unit": "µg/m³", "source": "D.S. N° 003-2017-MINAM"}
    },
    "Pb": {
        "anual": {"value": 0.5, "unit": "µg/m³", "source": "D.S. N° 003-2017-MINAM"}
    },
    "C6H6 (Benceno)": {
        "anual": {"value": 5, "unit": "µg/m³", "source": "D.S. N° 003-2017-MINAM"}
    },
    "As (Arsénico)": {
        "anual": {"value": 6, "unit": "ng/m³", "source": "D.S. N° 003-2017-MINAM"}
    },
    "Ni (Níquel)": {
        "anual": {"value": 20, "unit": "ng/m³", "source": "D.S. N° 003-2017-MINAM"}
    },
    "Cd (Cadmio)": {
        "anual": {"value": 5, "unit": "ng/m³", "source": "D.S. N° 003-2017-MINAM"}
    }
}


# LMP — Límites Máximos Permisibles por sector industrial (completo)
LMP = [
    # 🧱 Industria del Cemento y Cal
    {"Sector": "Cemento / Cal", "Parámetro": "Material Particulado Total (PM)", "Valor": "80 (nueva) / 120 (existente)", "Unidad": "mg/m³", "Norma": "D.S. N° 001-2020-MINAM"},
    
    # ⚡ Generación Termoeléctrica
    {"Sector": "Generación Termoeléctrica", "Parámetro": "PM, NOx, SO₂", "Valor": "Varía según tecnología y potencia instalada", "Unidad": "mg/Nm³", "Norma": "D.S. N° 030-2021-MINAM"},
    
    # 🐟 Industria Pesquera
    {"Sector": "Industria Pesquera (Harina y Aceite de Pescado)", "Parámetro": "Material Particulado Total (PM)", "Valor": "150", "Unidad": "mg/m³", "Norma": "D.S. N° 010-2008-PRODUCE"},
    {"Sector": "Industria Pesquera (Harina y Aceite de Pescado)", "Parámetro": "Compuestos orgánicos volátiles (COV)", "Valor": "20", "Unidad": "mg/m³", "Norma": "D.S. N° 010-2008-PRODUCE"},

    # 🔩 Industria Metalúrgica
    {"Sector": "Metalurgia (Fundición y Refinación)", "Parámetro": "SO₂", "Valor": "2000", "Unidad": "mg/m³", "Norma": "D.S. N° 010-2010-MINAM"},
    {"Sector": "Metalurgia (Fundición y Refinación)", "Parámetro": "Material Particulado (PM)", "Valor": "150", "Unidad": "mg/m³", "Norma": "D.S. N° 010-2010-MINAM"},
    {"Sector": "Metalurgia (Fundición y Refinación)", "Parámetro": "Metales (As, Pb, Cd, Cu, Zn)", "Valor": "Valores específicos por elemento", "Unidad": "mg/m³", "Norma": "D.S. N° 010-2010-MINAM"},

    # 🚗 Vehículos automotores
    {"Sector": "Vehículos Automotores — Gasolina", "Parámetro": "CO, HC, NOx", "Valor": "Según norma Euro IV / EPA Tier 2", "Unidad": "g/km o g/kWh", "Norma": "D.S. N° 047-2001-MTC y modificatorias"},
    {"Sector": "Vehículos Automotores — Diésel", "Parámetro": "PM, NOx, CO, HC", "Valor": "Según norma Euro IV / EPA Tier 2", "Unidad": "g/km o g/kWh", "Norma": "D.S. N° 047-2001-MTC y D.S. N° 010-2017-MINAM"},

    # 🏭 Otras industrias
    {"Sector": "Curtiembres", "Parámetro": "Material Particulado (PM)", "Valor": "150", "Unidad": "mg/m³", "Norma": "D.S. N° 003-2002-PRODUCE"},
    {"Sector": "Industria del Papel", "Parámetro": "Material Particulado (PM)", "Valor": "150", "Unidad": "mg/m³", "Norma": "D.S. N° 003-2002-PRODUCE"},
    {"Sector": "Industria Cervecera", "Parámetro": "Material Particulado (PM)", "Valor": "100", "Unidad": "mg/m³", "Norma": "D.S. N° 003-2002-PRODUCE"},

    # 🛢️ Hidrocarburos (Refinerías y Plantas de Gas)
    {"Sector": "Refinerías de Hidrocarburos", "Parámetro": "PM, SO₂, NOx, COV", "Valor": "Varía según proceso", "Unidad": "mg/Nm³", "Norma": "D.S. N° 010-2017-MINAM"},
    {"Sector": "Plantas de Gas Natural y GLP", "Parámetro": "PM, SO₂, NOx", "Valor": "100-200 según contaminante", "Unidad": "mg/Nm³", "Norma": "D.S. N° 010-2017-MINAM"},

    # ⛏️ Minería (Fundición y Plantas Concentradoras)
    {"Sector": "Fundición de Minerales", "Parámetro": "PM, SO₂, Metales pesados (As, Pb, Cd, Cu, Zn)", "Valor": "150-200 / Valores específicos por elemento", "Unidad": "mg/Nm³", "Norma": "D.S. N° 010-2010-MINAM"},
    {"Sector": "Plantas Concentradoras", "Parámetro": "Material Particulado (PM)", "Valor": "100", "Unidad": "mg/Nm³", "Norma": "D.S. N° 010-2010-MINAM"},
]


# Línea de tiempo
TIMELINE = [
    {"year": 2001, "norm": "DS N° 074-2001-PCM", "what": "Aprobación del Reglamento de Estándares Nacionales de Calidad Ambiental del Aire, estableciendo los primeros valores de referencia para contaminantes como PM10, CO, NO2, SO2, O3 y Pb."},
    {"year": 2003, "norm": "DS N° 069-2003-PCM", "what": "Modificación del valor anual de concentración de plomo, estableciendo un límite de 0.5 µg/m³."},
    {"year": 2008, "norm": "DS N° 003-2008-MINAM", "what": "Aprobación de los Estándares de Calidad Ambiental para Aire, actualizando los valores y parámetros con base en evidencia científica actualizada."},
    {"year": 2013, "norm": "DS N° 006-2013-MINAM", "what": "Aprobación de disposiciones complementarias para la aplicación de estándares de calidad ambiental para dióxido de azufre."},
    {"year": 2014, "norm": "DS N° 003-2014-MINAM", "what": "Establecimiento de procedimientos para la adecuación de los instrumentos de gestión a los nuevos ECA."},
    {"year": 2017, "norm": "DS N° 003-2017-MINAM", "what": "Aprobación de nuevos Estándares de Calidad Ambiental para Aire, derogando normas anteriores y estableciendo valores más estrictos para contaminantes como PM2.5, PM10, SO2, NO2, CO, O3 y Pb."},
    {"year": 2021, "norm": "DS N° 030-2021-MINAM", "what": "Aprobación de Límites Máximos Permisibles para emisiones de material particulado, NOx y SO2 en generación termoeléctrica, con valores diferenciados según tecnología."},
    {"year": 2023, "norm": "RM N° 205-2023-MINAM", "what": "Aprobación de Límites Máximos Permisibles para emisiones de la industria de harina y aceite de pescado, estableciendo valores específicos para cada contaminante."},
    {"year": 2025, "norm": "DS N° 045-2025-MINAM", "what": "Aprobación de nuevos Estándares de Calidad Ambiental para Aire, incorporando parámetros como benceno, arsénico, níquel y cadmio, con valores anuales establecidos para cada uno."}
]

# Resumen de normas legales relacionadas con la calidad del aire en Perú
NORMA_EXPLICACIONES = {
    "Ley N° 28611": {
        "Estado": "Vigente",
        "Fecha de Publicación": "28 de julio de 2005",
        "Resumen": (
            "Ley General del Ambiente. Constituye el marco normativo principal para la política ambiental en Perú, "
            "reconociendo el derecho a un ambiente equilibrado y adecuado para la vida, salud y bienestar humano. "
            "Establece los principios de prevención, precaución y responsabilidad ambiental, así como instrumentos "
            "de gestión ambiental y promoción de participación ciudadana y educación ambiental."
        ),
        "Objetivo": (
            "Garantizar la conservación y uso sostenible de los recursos naturales, integrar la dimensión ambiental "
            "en las políticas públicas y asegurar la sostenibilidad del desarrollo económico y social. "
            "Marco para la creación de estándares de calidad ambiental y regulación de emisiones contaminantes."
        ),
        "Antecedentes": "Primera Ley General del Ambiente en Perú, sirvió como base para normas sectoriales posteriores.",
        "Aplicación": "Aplica a todos los sectores productivos, regulando planes y programas con impacto ambiental."
    },
    "Decreto Supremo N° 074-2001-PCM": {
        "Estado": "Derogado",
        "Fecha de Publicación": "22 de junio de 2001",
        "Resumen": (
            "Establece los estándares nacionales de calidad ambiental del aire para contaminantes SO₂, PM10, CO, NO₂, O₃ y Pb. "
            "Fue la primera norma en fijar límites específicos para proteger la salud humana y el ambiente."
        ),
        "Objetivo": "Definir estándares de calidad del aire para proteger la salud y el ambiente. Fue reemplazado por DS N° 003-2017-MINAM.",
        "Derogación": "Derogado por DS N° 003-2017-MINAM en 2017",
        "Aplicación": "Principalmente aplicado a industrias, transporte y actividades urbanas antes de su derogación."
    },
    "Decreto Supremo N° 003-2017-MINAM": {
        "Estado": "Vigente",
        "Fecha de Publicación": "7 de junio de 2017",
        "Resumen": (
            "Aprueba los Estándares de Calidad Ambiental (ECA) para aire, incorporando PM2.5, metales pesados y nuevos valores "
            "más estrictos, basados en evidencia científica y recomendaciones de la OMS."
        ),
        "Objetivo": "Actualizar los estándares de calidad del aire y proteger la salud pública y el medio ambiente frente a contaminantes.",
        "Actualización": "Sustituye los límites de DS 074-2001-PCM y establece nuevos parámetros para monitoreo ambiental.",
        "Aplicación": "Industria, transporte, áreas urbanas y monitoreo ambiental en todo el país."
    },
    "Decreto Supremo N° 017-2025-MINAM": {
        "Estado": "Vigente",
        "Fecha de Publicación": "2025",
        "Resumen": "Define criterios técnicos y procedimientos para la gestión y monitoreo de la calidad del aire, incluyendo acreditación de laboratorios.",
        "Objetivo": "Fortalecer la implementación de los estándares de calidad del aire y asegurar la confiabilidad de datos de monitoreo.",
        "Aplicación": "Aplicable a laboratorios de monitoreo y autoridades ambientales regionales y locales."
    },
    "Decreto Supremo N° 010-2019-MINAM": {
        "Estado": "Vigente",
        "Fecha de Publicación": "2019",
        "Resumen": "Aprueba el Protocolo Nacional de Monitoreo de la Calidad Ambiental del Aire para estandarizar mediciones y reportes.",
        "Objetivo": "Generar información confiable y comparable sobre la calidad del aire en todo el país.",
        "Aplicación": "Para todos los laboratorios de monitoreo y estudios de calidad ambiental en Perú."
    },
    "Decreto Supremo N° 030-2021-MINAM": {
        "Estado": "Vigente",
        "Fecha de Publicación": "2021",
        "Resumen": "Aprueba los Límites Máximos Permisibles para emisiones de la generación termoeléctrica, estableciendo límites de PM, NOx y SO2.",
        "Objetivo": "Proteger la calidad del aire y la salud pública limitando emisiones contaminantes de plantas termoeléctricas.",
        "Aplicación": "Generación termoeléctrica en todo el territorio nacional."
    },
    "Decreto Supremo N° 011-2023-MINAM": {
        "Estado": "Vigente",
        "Fecha de Publicación": "2023",
        "Resumen": "Aprueba los ECA de aire para cadmio, arsénico y cromo en PM10, incorporando estándares basados en riesgo sanitario.",
        "Objetivo": "Proteger la salud humana y el medio ambiente mediante la regulación de metales pesados en el aire.",
        "Aplicación": "Industria metalúrgica, minería y sectores con emisiones de metales pesados."
    },
    "Decreto Supremo N° 002-2025-MINAM": {
        "Estado": "Vigente",
        "Fecha de Publicación": "2025",
        "Resumen": "Aprueba el Reglamento de la Ley N° 32099 sobre humedales, incluyendo su rol en la calidad del aire.",
        "Objetivo": "Implementar medidas de conservación de humedales, que contribuyen a la purificación del aire y protección ecológica.",
        "Aplicación": "Áreas naturales protegidas y humedales a nivel nacional."
    },
    "Decreto Supremo N° 0007-2024-MTC": {
        "Estado": "Vigente",
        "Fecha de Publicación": "2024",
        "Resumen": "Aprueba el Reglamento de la Ley Nº 31595 para la descontaminación ambiental mediante retiro de cableado aéreo en mal estado.",
        "Objetivo": "Reducir fuentes de contaminación y riesgos de incendios, mejorando la calidad del aire en zonas urbanas.",
        "Aplicación": "Municipalidades, empresas de servicios eléctricos y zonas urbanas densamente pobladas."
    }
}
# -------------------------
# UTILIDADES
# -------------------------
def eca_to_df(eca_dict):
    periodos = set()
    for cont, periods in eca_dict.items():
        for p in periods.keys():
            periodos.add(p)
    periodos = sorted(periodos)
    table = {}
    for p in periodos:
        row = {}
        for cont, periods in eca_dict.items():
            if p in periods:
                row[cont] = periods[p]
            else:
                row[cont] = None
        table[p] = row
    df = pd.DataFrame.from_dict(table, orient="index")
    df.index.name = "Periodo"
    return df

def format_cell(cell):
    if isinstance(cell, dict):
        return f"{cell['value']} {cell['unit']} ({cell['source']})"
    return "—"

def numeric_cell(cell):
    if isinstance(cell, dict):
        try:
            return float(cell["value"])
        except Exception:
            return None
    return None

# -------------------------
# SIDEBAR
# -------------------------
st.sidebar.markdown('<p style="color:#d62728; font-weight:bold;">🌬️ Menú</p>', unsafe_allow_html=True)
choice = st.sidebar.radio("Ir a:", [
    "Inicio",
    "Línea de tiempo",
    "ECA (Aire)",
    "LMP por sector",
    "Decretos, Reglamentos y Leyes",
    "Gráficas & Descargas"
])

st.sidebar.markdown("---")
st.sidebar.write("**Autores:** Estudiantes de la carerra profesional de Ingenieria Ambiental de la Uiversidad Nacional de Moquegua")
st.sidebar.write("**Curso:** Contaminacion y Control Atmosferica")
st.sidebar.markdown("---")

# -------------------------
# SECCIONES
# -------------------------
if choice == "Inicio":
    st.title("🌎 Marco Normativo Peruano de la Calidad del Aire")

    st.markdown(dedent("""
    ## Bienvenido

    Esta aplicación educativa tiene como propósito **difundir y facilitar el acceso** al marco normativo que regula la calidad del aire en el Perú.  
    Aquí podrás explorar los **instrumentos legales**, los **Estándares de Calidad Ambiental (ECA)** y los **Límites Máximos Permisibles (LMP)** por sector productivo, 
    junto con **visualizaciones interactivas** que te ayudarán a comprender cómo se mide, controla y protege la calidad del aire en nuestro país.
    """))

    st.markdown("---")

    st.markdown(dedent("""
    ## 🏛️ Contexto general

    El Perú cuenta con una sólida base legal para la **gestión ambiental y la protección de la salud pública**.  
    El marco normativo sobre calidad del aire se sustenta principalmente en:

    - **Ley N.º 28611** – Ley General del Ambiente  
    - **Ley N.º 28245** – Ley Marco del Sistema Nacional de Gestión Ambiental  
    - **Decreto Supremo N.º 074-2001-PCM** – Reglamento de Estándares Nacionales de Calidad Ambiental del Aire  
    - **Decreto Supremo N.º 003-2017-MINAM** – Actualiza los ECA para Aire  
    - **Decretos Supremos sectoriales** que establecen los **Límites Máximos Permisibles (LMP)** para actividades industriales, mineras, energéticas, etc.

    Estas normas establecen los **niveles máximos aceptables de contaminantes atmosféricos** y definen los mecanismos de monitoreo y fiscalización ambiental.
    """))

    st.markdown("---")

    st.markdown(dedent("""
    ## 🌬️ ¿Qué son los ECA y los LMP?

    **Estándares de Calidad Ambiental (ECA):**  
    Son los valores máximos permitidos de concentración de contaminantes en el aire, establecidos para **proteger la salud humana y el ambiente**.  
    Ejemplo: niveles de PM2.5, PM10, dióxido de azufre (SO₂), monóxido de carbono (CO), ozono (O₃), entre otros.

    **Límites Máximos Permisibles (LMP):**  
    Son los valores máximos de contaminantes que una **actividad o instalación** puede emitir al ambiente.  
    Por ejemplo, existen LMP específicos para el **sector minero, hidrocarburos, eléctrico, transporte y manufactura**.
    """))

    st.markdown("---")

    st.markdown(dedent("""
    ## 📈 Objetivo de esta aplicación

    - Difundir el marco legal vigente del **aire limpio** en el Perú.  
    - Facilitar la **consulta de los ECA y LMP** según contaminante o sector.  
    - Promover una **cultura ambiental informada** basada en datos y evidencia científica.  
    - Contribuir a la **educación ambiental** de estudiantes, profesionales y ciudadanía.

    ---
    🔗 **Fuentes oficiales:**
    - [Ministerio del Ambiente (MINAM)](https://www.gob.pe/minam)
    - [Servicio Nacional de Meteorología e Hidrología (SENAMHI)](https://www.senamhi.gob.pe)
    - [Organismo de Evaluación y Fiscalización Ambiental (OEFA)](https://www.oefa.gob.pe)
    """))

elif choice == "Línea de tiempo":
    st.header("📜 Línea de tiempo — principales hitos normativos en calidad del aire")
    for item in TIMELINE:
        st.markdown(f"**{item['year']} — {item['norm']}**  \n• {item['what']}")
    df_time = pd.DataFrame(TIMELINE)
    df_time["y"] = range(len(df_time))
    fig = px.scatter(df_time, x="year", y="y", text="norm", hover_data=["what"], height=400)
    fig.update_yaxes(visible=False, showticklabels=False)
    fig.update_layout(
        xaxis_title="Año",
        showlegend=False,
        template="plotly_white",
        margin=dict(l=20, r=20, t=30, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

elif choice == "ECA (Aire)":
    st.header("🌬️ Estándares de Calidad Ambiental (ECA) — Aire")
    eca_df = eca_to_df(ECA)
    eca_formatted = eca_df.applymap(format_cell)
    st.markdown("#### 📋 Tabla: ECA (Periodo × Contaminante)")
    st.dataframe(eca_formatted, use_container_width=True)

elif choice == "LMP por sector":
    st.header("🏭 Límites Máximos Permisibles (LMP) — Por sector")
    lmp_df = pd.DataFrame(LMP)
    st.dataframe(lmp_df, use_container_width=True)

elif choice == "Decretos, Reglamentos y Leyes":
    st.header("📚 Decretos Supremos, Reglamentos y Leyes de Calidad del Aire en Perú")

    for norma, datos in NORMA_EXPLICACIONES.items():
        st.subheader(norma)

        # Construimos el texto de cada norma
        texto = f"""
**Estado:** {datos.get('Estado', 'No disponible')}  
**Fecha de Publicación:** {datos.get('Fecha de Publicación', 'No disponible')}  
**Resumen:** {datos.get('Resumen', 'No disponible')}  
**Objetivo:** {datos.get('Objetivo', 'No disponible')}  
"""
        # Campos opcionales
        if 'Antecedentes' in datos:
            texto += f"**Antecedentes:** {datos['Antecedentes']}\n"
        if 'Derogación' in datos:
            texto += f"**Derogación:** {datos['Derogación']}\n"
        if 'Aplicación' in datos:
            texto += f"**Aplicación:** {datos['Aplicación']}\n"

        st.markdown(texto)
elif choice == "Gráficas & Descargas":
    st.header("📊 Gráficas y descargas")
    eca_df = eca_to_df(ECA)
    eca_formatted = eca_df.applymap(format_cell)
    st.dataframe(eca_formatted, use_container_width=True)
    st.download_button("📥 Descargar ECA (CSV)", eca_formatted.to_csv(index=True), file_name="eca_table.csv", mime="text/csv")

import streamlit as st
import pandas as pd

# Configuración inicial de la página
st.set_page_config(
    page_title="Catálogo de Librería Personal",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS para mantener una interfaz limpia y moderna
st.markdown("""
    <style>
    .main {
        padding-top: 1rem;
    }
    .stCard {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
        border-left: 4px solid #1E88E5;
    }
    .book-code {
        font-family: monospace;
        background-color: #e3f2fd;
        color: #0d47a1;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    .badge-tag {
        background-color: #e0e0e0;
        color: #333;
        padding: 2px 6px;
        border-radius: 3px;
        font-size: 0.8em;
    }
    </style>
""", unsafe_allow_html=True)

# Carga de la base de datos
@st.cache_data
def load_data():
    df = pd.read_csv('Catalogo_Estructurado.csv')
    df['Año_Clean'] = pd.to_numeric(df['Año'], errors='coerce')
    return df

df = load_data()

# ---------------------------------------------------------
# BARRA LATERAL: FILTROS Y SOLICITUD DE DESCARGA
# ---------------------------------------------------------
st.sidebar.title("📚 Filtros de Búsqueda")

# 1. Categoría Principal (Temática)
categorias = ["Todas"] + sorted(df['Categoria_Principal'].dropna().unique().tolist())
cat_selected = st.sidebar.selectbox("Temática / Categoría:", categorias)

# 2. Tipo de Documento
tipos = ["Todos"] + sorted(df['Tipo_Documento'].dropna().unique().tolist())
tipo_selected = st.sidebar.selectbox("Tipo de Documento:", tipos)

# 3. Rango de Años
min_year = int(df['Año_Clean'].min()) if not df['Año_Clean'].isna().all() else 1800
max_year = int(df['Año_Clean'].max()) if not df['Año_Clean'].isna().all() else 2026

year_range = st.sidebar.slider(
    "Filtrar por Año de Publicación:",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

st.sidebar.markdown("---")

# ---------------------------------------------------------
# SECCIÓN: SOLICITUD DE DESCARGA VÍA CÓDIGO SERIAL
# ---------------------------------------------------------
st.sidebar.subheader("🔑 Solicitar Descarga")
st.sidebar.caption("Ingresa el código del libro que deseas solicitar (ej. LIB-001):")

input_code = st.sidebar.text_input("Código del Libro:", placeholder="LIB-xxx").strip().upper()

if st.sidebar.button("Obtener Enlace de Descarga"):
    if input_code:
        match = df[df['ID_Libro'] == input_code]
        if not match.empty:
            book = match.iloc[0]
            st.sidebar.success(f"**{book['Titulo']}**")
            
            # Verificación de enlace de descarga disponible
            link_descarga = book['Link_Descarga']
            if pd.notna(link_descarga) and str(link_descarga).strip() != "":
                st.sidebar.markdown(f"[📥 Descargar Archivo Completo]({link_descarga})")
            else:
                st.sidebar.info("📌 Tu solicitud ha sido registrada. El enlace directo estará disponible en breve.")
        else:
            st.sidebar.error("Código de libro no encontrado. Verifica en la lista principal.")
    else:
        st.sidebar.warning("Por favor ingresa un código válido.")

# ---------------------------------------------------------
# CUERPO PRINCIPAL
# ---------------------------------------------------------
st.title("📖 Catálogo Digital de Archivo y Lectura")
st.caption("Explora, previsualiza en línea y solicita acceso a títulos en formato digital.")

# Búsqueda por Texto (Título / Autor / Etiquetas)
search_query = st.text_input("🔎 Buscar por Título, Autor o Palabra Clave:", placeholder="Ej. Bresson, Urbanismo, Foucault...")

# Aplicación de filtros al DataFrame
filtered_df = df.copy()

# Filtro por temática
if cat_selected != "Todas":
    filtered_df = filtered_df[filtered_df['Categoria_Principal'] == cat_selected]

# Filtro por tipo de documento
if tipo_selected != "Todos":
    filtered_df = filtered_df[filtered_df['Tipo_Documento'] == tipo_selected]

# Filtro por año (respetando los registros que no tienen año especificado '-')
filtered_df = filtered_df[
    (filtered_df['Año_Clean'].isna()) | 
    ((filtered_df['Año_Clean'] >= year_range[0]) & (filtered_df['Año_Clean'] <= year_range[1]))
]

# Filtro por texto de búsqueda
if search_query:
    q = search_query.lower()
    filtered_df = filtered_df[
        filtered_df['Titulo'].str.lower().str.contains(q, na=False) |
        filtered_df['Autor-a'].str.lower().str.contains(q, na=False) |
        filtered_df['Enfoque_Especifico'].str.lower().str.contains(q, na=False) |
        filtered_df['Etiquetas'].str.lower().str.contains(q, na=False)
    ]

# Métrica de Resultados
col_m1, col_m2 = st.columns([2, 8])
with col_m1:
    st.metric(label="Libros Encontrados", value=len(filtered_df))

st.markdown("---")

# Visualización de Libros en Vista Lista / Tarjetas
if filtered_df.empty:
    st.warning("No se encontraron publicaciones que coincidan con los filtros seleccionados.")
else:
    for idx, row in filtered_df.iterrows():
        with st.container():
            st.markdown(f"""
                <div class="stCard">
                    <span class="book-code">{row['ID_Libro']}</span> — <strong>{row['Categoria_Principal']}</strong> ({row['Tipo_Documento']})
                    <h3 style="margin-top: 5px; margin-bottom: 5px; color: #111;">{row['Titulo']}</h3>
                    <p style="margin-bottom: 5px;"><strong>Autor(a):</strong> {row['Autor-a']} | <strong>Año:</strong> {row['Año']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns([3, 3, 4])
            
            # Enlace a Previsualización en Drive
            preview_url = row['Link_Previsualizacion']
            if pd.notna(preview_url) and str(preview_url).strip() != "":
                c1.markdown(f"[👁️ Previsualizar en Drive]({preview_url})")
            else:
                c1.caption("👁️ Vista previa no vinculada")
                
            # Muestra etiquetas adicionales si existen
            if pd.notna(row['Etiquetas']) and str(row['Etiquetas']).strip() != "":
                c2.caption(f"🏷️ *{row['Etiquetas']}*")
                
            st.markdown("<br>", unsafe_allow_html=True)

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
    </style>
""", unsafe_allow_html=True)

# Carga de la base de datos con mapeo tolerante de columnas
@st.cache_data
def load_data():
    df = pd.read_csv('Catalogo_Estructurado.csv')
    
    # 1. Eliminar espacios accidentales en los nombres de las columnas
    df.columns = df.columns.str.strip()
    
    # 2. Diccionario de equivalencias para normalizar nombres de columnas
    mapa_columnas = {}
    for col in df.columns:
        c_low = col.lower().replace("_", "").replace("-", "").replace(" ", "")
        
        if "id" in c_low or "codigo" in c_low:
            mapa_columnas[col] = "ID_Libro"
        elif "categoria" in c_low or "tematica" in c_low:
            mapa_columnas[col] = "Categoria_Principal"
        elif "tipo" in c_low or "documento" in c_low:
            mapa_columnas[col] = "Tipo_Documento"
        elif "titulo" in c_low or "nombre" in c_low:
            mapa_columnas[col] = "Titulo"
        elif "autor" in c_low:
            mapa_columnas[col] = "Autor-a"
        elif "año" in c_low or "anio" in c_low or "date" in c_low:
            mapa_columnas[col] = "Año"
        elif "preview" in c_low or "previsualizac" in c_low or "vista" in c_low:
            mapa_columnas[col] = "Link_Previsualizacion"
        elif "descarga" in c_low or "link" in c_low or "enlace" in c_low:
            mapa_columnas[col] = "Link_Descarga"
        elif "enfoque" in c_low:
            mapa_columnas[col] = "Enfoque_Especifico"
        elif "etiqueta" in c_low or "tag" in c_low:
            mapa_columnas[col] = "Etiquetas"
            
    df = df.rename(columns=mapa_columnas)
    
    # Asegurar existencia de columnas esenciales
    columnas_base = [
        'ID_Libro', 'Categoria_Principal', 'Tipo_Documento', 'Titulo', 
        'Autor-a', 'Año', 'Link_Previsualizacion', 'Link_Descarga', 
        'Enfoque_Especifico', 'Etiquetas'
    ]
    for c in columnas_base:
        if c not in df.columns:
            df[c] = "-"
            
    # Convertir Año a numérico de forma segura
    df['Año_Clean'] = pd.to_numeric(df['Año'], errors='coerce')
    
    return df

df = load_data()

# ---------------------------------------------------------
# BARRA LATERAL: FILTROS Y SOLICITUD DE DESCARGA
# ---------------------------------------------------------
st.sidebar.title("📚 Filtros de Búsqueda")

# 1. Categoría Principal
categorias_vals = [x for x in df['Categoria_Principal'].dropna().unique().tolist() if str(x) != "-"]
categorias = ["Todas"] + sorted(categorias_vals)
cat_selected = st.sidebar.selectbox("Temática / Categoría:", categorias)

# 2. Tipo de Documento
tipos_vals = [x for x in df['Tipo_Documento'].dropna().unique().tolist() if str(x) != "-"]
tipos = ["Todos"] + sorted(tipos_vals)
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

# Solicitud de descarga mediante código
st.sidebar.subheader("🔑 Solicitar Descarga")
st.sidebar.caption("Ingresa el código del libro que deseas solicitar (ej. LIB-001):")

input_code = st.sidebar.text_input("Código del Libro:", placeholder="LIB-xxx").strip().upper()

if st.sidebar.button("Obtener Enlace de Descarga"):
    if input_code:
        match = df[df['ID_Libro'].astype(str).str.upper() == input_code]
        if not match.empty:
            book = match.iloc[0]
            st.sidebar.success(f"**{book['Titulo']}**")
            
            link_descarga = str(book['Link_Descarga']).strip()
            if pd.notna(book['Link_Descarga']) and link_descarga not in ["", "-", "nan"]:
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

# Búsqueda por Texto
search_query = st.text_input("🔎 Buscar por Título, Autor o Palabra Clave:", placeholder="Ej. Bresson, Urbanismo, Foucault...")

# Aplicación de filtros al DataFrame
filtered_df = df.copy()

if cat_selected != "Todas":
    filtered_df = filtered_df[filtered_df['Categoria_Principal'] == cat_selected]

if tipo_selected != "Todos":
    filtered_df = filtered_df[filtered_df['Tipo_Documento'] == tipo_selected]

filtered_df = filtered_df[
    (filtered_df['Año_Clean'].isna()) | 
    ((filtered_df['Año_Clean'] >= year_range[0]) & (filtered_df['Año_Clean'] <= year_range[1]))
]

if search_query:
    q = search_query.lower()
    filtered_df = filtered_df[
        filtered_df['Titulo'].astype(str).str.lower().str.contains(q, na=False) |
        filtered_df['Autor-a'].astype(str).str.lower().str.contains(q, na=False) |
        filtered_df['Enfoque_Especifico'].astype(str).str.lower().str.contains(q, na=False) |
        filtered_df['Etiquetas'].astype(str).str.lower().str.contains(q, na=False)
    ]

# Métrica de Resultados
col_m1, col_m2 = st.columns([2, 8])
with col_m1:
    st.metric(label="Libros Encontrados", value=len(filtered_df))

st.markdown("---")

# Visualización de Libros
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
            
            c1, c2 = st.columns([4, 6])
            
            # --- EVALUACIÓN Y VINCULACIÓN DEL ENLACE DE PREVISUALIZACIÓN ---
            preview_val = str(row['Link_Previsualizacion']).strip()
            
            # Comprobar si la celda contiene una URL válida (http/https) o texto de enlace
            if pd.notna(row['Link_Previsualizacion']) and preview_val not in ["", "-", "nan", "None"]:
                if preview_val.startswith("http://") or preview_val.startswith("https://"):
                    c1.markdown(f"🔗 **[👁️ Abrir Previsualización / Vista Previa]({preview_val})**")
                else:
                    # En caso de que la celda tenga un enlace sin el protocolo http://
                    c1.markdown(f"🔗 **[👁️ Abrir Previsualización / Vista Previa](http://{preview_val})**")
            else:
                c1.caption("👁️ Vista previa no vinculada")
                
            # Etiquetas adicionales
            etiquetas_val = str(row['Etiquetas']).strip()
            if pd.notna(row['Etiquetas']) and etiquetas_val not in ["", "-", "nan", "None"]:
                c2.caption(f"🏷️ *{etiquetas_val}*")
                
            st.markdown("<br>", unsafe_allow_html=True)

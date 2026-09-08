import streamlit as st
import pandas as pd

# 1. Configuración de la página
st.set_page_config(
    page_title="Biblioteca & Catálogo Digital",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados para tarjetas elegantes
st.markdown("""
<style>
    .book-card {
        background-color: #f9f9f9;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .book-title {
        color: #1E1E1E;
        font-size: 1.15rem;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .book-author {
        color: #555555;
        font-size: 0.95rem;
        font-style: italic;
        margin-bottom: 10px;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# 2. Carga y preparación de datos desde GitHub
URL_CSV_GITHUB = "https://raw.githubusercontent.com/TU_USUARIO/TU_REPOSITORIO/main/TU_ARCHIVO.csv"

@st.cache_data(ttl=300)
def cargar_datos(url):
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        
        # Intento de extracción o conversión del año si existe en el título o en alguna columna
        if 'Año' not in df.columns:
            # Busca un año de 4 dígitos dentro del título del libro si no existe una columna explícita
            col_titulo = [c for c in df.columns if 'nombre' in c.lower() or 'titulo' in c.lower() or 'libro' in c.lower()][0]
            df['Año'] = df[col_titulo].astype(str).apply(
                lambda x: int(re.search(r'\b(18|19|20)\d{2}\b', x).group(0)) if re.search(r'\b(18|19|20)\d{2}\b', x) else None
            )
        return df
    except Exception as e:
        st.error(f"Error al cargar el catálogo: {e}")
        return pd.DataFrame()

df_raw = cargar_datos(URL_CSV_GITHUB)

if not df_raw.empty:
    # Identificar nombres de columnas dinámicamente
    cols = df_raw.columns.tolist()
    col_titulo = cols[0]
    col_autor = cols[1] if len(cols) > 1 else cols[0]
    col_enlace = cols[2] if len(cols) > 2 else cols[0]

    # --- BARRA LATERAL (FILTROS) ---
    st.sidebar.header("🔍 Filtros & Búsqueda")
    
    # Buscador de texto libre
    busqueda = st.sidebar.text_input("Buscar por título o autor:", "")
    
    # Filtro por rango de años (si existen años detectados)
    anios_validos = df_raw['Año'].dropna().astype(int)
    if not anios_validos.empty and anios_validos.min() < anios_validos.max():
        min_anio, max_anio = int(anios_validos.min()), int(anios_validos.max())
        rango_anios = st.sidebar.slider(
            "Rango de años:",
            min_value=min_anio,
            max_value=max_anio,
            value=(min_anio, max_anio)
        )
    else:
        rango_anios = None

    # --- FILTRADO DE DATOS ---
    df_filtrado = df_raw.copy()
    
    if busqueda:
        condicion = df_filtrado.astype(str).apply(
            lambda x: x.str.contains(busqueda, case=False, na=False)
        ).any(axis=1)
        df_filtrado = df_filtrado[condicion]
        
    if rango_anios and 'Año' in df_filtrado.columns:
        df_filtrado = df_filtrado[
            (df_filtrado['Año'].isna()) | 
            ((df_filtrado['Año'] >= rango_anios[0]) & (df_filtrado['Año'] <= rango_anios[1]))
        ]

    # --- CONTENIDO PRINCIPAL ---
    st.title("📚 Biblioteca Digital")
    st.caption(f"Mostrando {len(df_filtrado)} de {len(df_raw)} publicaciones disponibles.")

    # Renderizado en rejilla (Grid de 2 columnas)
    col1, col2 = st.columns(2)
    
    for idx, row in df_filtrado.reset_index(drop=True).iterrows():
        # Alternar entre columna izquierda y derecha
        col_actual = col1 if idx % 2 == 0 else col2
        
        titulo = row[col_titulo]
        autor = row[col_autor]
        enlace = row[col_enlace]
        anio_str = f" ({int(row['Año'])})" if pd.notna(row.get('Año')) else ""

        with col_actual:
            with st.container():
                st.markdown(f"""
                <div class="book-card">
                    <div class="book-title">📖 {titulo}{anio_str}</div>
                    <div class="book-author">✍️ {autor}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Desplegable individual para previsualizar/solicitar
                with st.expander("👁️ Ver detalles y opciones"):
                    st.write(f"**Título:** {titulo}")
                    st.write(f"**Autor/a:** {autor}")
                    
                    if pd.notna(enlace) and str(enlace).startswith("http"):
                        st.link_button("🔗 Previsualizar / Abrir en Drive", str(enlace))
                    else:
                        st.info("Enlace de previsualización no disponible.")

                    st.divider()
                    
                    # Cuadro de solicitud con correo
                    st.subheader("📩 Solicitar descarga por correo")
                    correo_user = st.text_input(
                        "Ingresa tu correo para recibir el archivo:",
                        key=f"email_{idx}",
                        placeholder="ejemplo@correo.com"
                    )
                    
                    if st.button("Enviar solicitud", key=f"btn_{idx}"):
                        if correo_user and "@" in correo_user:
                            # Aquí se conecta con el flujo del Google Form / Apps Script si lo deseas
                            st.success(f"¡Solicitud enviada! Se compartirá el acceso a **{correo_user}**.")
                        else:
                            st.warning("Por favor introduce un correo electrónico válido.")
                st.write("") # Espaciador vertical

    # Opciones avanzadas en la barra lateral
    st.sidebar.divider()
    if st.sidebar.button("🔄 Actualizar catálogo"):
        st.cache_data.clear()
        st.rerun()

else:
    st.warning("No se pudieron cargar los libros. Revisa la URL RAW de GitHub.")

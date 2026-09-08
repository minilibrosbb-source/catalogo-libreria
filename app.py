import streamlit as st
import pandas as pd

# 1. Configuración de la página
st.set_page_config(
    page_title="Catálogo de Libros",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Catálogo y Biblioteca Digital")
st.write("Explora los libros disponibles en nuestro catálogo. Puedes previsualizar o solicitar acceso a los títulos.")

# 2. Carga de datos desde GitHub (reemplaza con tu URL RAW de GitHub)
# Ejemplo de URL RAW: "https://raw.githubusercontent.com/usuario/repositorio/main/tu_archivo.csv"
URL_CSV_GITHUB = "https://raw.githubusercontent.com/minilibrosbb-source/catalogo-libreria/refs/heads/main/Catalogo_Estructurado.csv"

@st.cache_data(ttl=300)  # Guarda en caché por 5 minutos para respuesta rápida
def cargar_datos(url):
    try:
        df = pd.read_csv(url)
        # Limpieza básica de espacios en nombres de columnas
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Error al cargar el archivo CSV desde GitHub: {e}")
        return pd.DataFrame()

# Cargar el dataframe
df_books = cargar_datos(URL_CSV_GITHUB)

if not df_books.empty:
    # 3. Buscador / Filtro interactivo en Streamlit
    busqueda = st.text_input("🔍 Buscar por título o autor:", "")

    if busqueda:
        # Filtra si la palabra buscada está en cualquier columna de texto
        condicion = df_books.astype(str).apply(
            lambda x: x.str.contains(busqueda, case=False, na=False)
        ).any(axis=1)
        df_filtrado = df_books[condicion]
    else:
        df_filtrado = df_books

    st.write(f"Mostrando **{len(df_filtrado)}** de **{len(df_books)}** libros.")

    # 4. Renderizado de la tabla con enlaces formateados
    # Asumiendo que las columnas en tu CSV son: 'Nombre del Archivo' (o Título), 'Autor' y 'Enlace al Libro'
    # Ajusta los nombres dentro de column_config si tus encabezados son ligeramente distintos.
    
    st.dataframe(
        df_filtrado,
        use_container_width=True,
        hide_index=True,
        column_config={
            # Formatea la columna de enlace para que se muestre como un botón con texto limpio
            "Enlace al Libro": st.column_config.LinkColumn(
                "Acceso",
                display_text="📖 Abrir Libro",
                help="Haz clic para ver o solicitar el libro en Google Drive"
            ),
            "Nombre del Archivo": st.column_config.TextColumn(
                "Título del Libro"
            ),
            "Autor": st.column_config.TextColumn(
                "Autor"
            )
        }
    )

    # Botón para limpiar la caché de Streamlit si acabas de actualizar el CSV en GitHub
    with st.expander("⚙️ Opciones de actualización"):
        if st.button("🔄 Forzar recarga de datos de GitHub"):
            st.cache_data.clear()
            st.rerun()
else:
    st.info("No se encontraron datos para mostrar. Verifica que la URL del CSV RAW en GitHub sea correcta.")

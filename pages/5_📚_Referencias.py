"""
Página de Referencias - Fundamentos Teóricos
"""
import streamlit as st
from modules.auth import check_authentication, require_authentication

st.set_page_config(
    page_title="Referencias - Productivity Coach",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Verificar autenticación
require_authentication()

from modules.ui_components import render_sidebar

# Header
render_sidebar()

st.title("📚 Referencias y Fundamentos Teóricos")

st.markdown("""
Esta app está fundamentada en **investigación científica** y frameworks probados
de productividad y formación de hábitos. No son "hacks" temporales, sino
**principios validados** sobre cómo funciona el cerebro y el comportamiento humano.
""")

st.divider()

# 1. Rob Dial
st.header("1. 🎙️ Rob Dial - The Mindset Mentor")

col1, col2 = st.columns([1, 2])

with col1:
    st.image("https://m.media-amazon.com/images/I/41D2vXp7CGL._SL500_.jpg", width=200)

with col2:
    st.subheader("Conceptos Aplicados")

    st.markdown("**Consistencia > Motivación**")
    st.write("📌 **Uso en App:** Dashboard de Métricas y Racha de Código.")
    st.write("📌 'La motivación es un combustible barato; la consistencia es el motor real del éxito'.")
    st.caption("Aplicación: Framework 'Sistema > Motivación'")

    st.markdown("**Mínimo No Negociable (Non-Negotiables)**")
    st.write("📌 **Uso en App:** Checkboxes del sistema diario.")
    st.write("📌 Definir una versión 'ridículamente pequeña' de la tarea para vencer la inercia.")
    st.caption("Aplicación: Código diario sin excepciones")

st.info('💬 **Cita clave:** "Motivation is the spark. Consistency is the fire that just keeps burning long after the spark has gone away."')

with st.expander("🎙️ Fuente: Video Analysis"):
    st.markdown("- **Video:** `20260117-32-Why-Consistency-Always-Wins-Power-of-Consistency.txt`")

st.divider()

# 2. Cal Newport
st.header("2. 🔥 Cal Newport - Deep Work")

col1, col2 = st.columns([1, 2])

with col1:
    st.image("https://covers.openlibrary.org/b/id/8394677-L.jpg", width=200)

with col2:
    st.subheader("Conceptos Aplicados")

    st.markdown("**Protocolo 3x60 (Trabajo Profundo)**")
    st.write("📌 **Uso en App:** Focus Timer y estructura del día.")
    st.write("📌 Las primeras 3 horas del día son biológicamente tus horas pico de atención.")
    st.caption("Aplicación: Bloques de 8:00 - 11:00 AM solo para las 3 tareas críticas.")

    st.markdown("**Estrategia Rítmica**")
    st.write("📌 **Uso en App:** Resumen Semanal.")
    st.write("📌 Horarios fijos diarios para Deep Work (la estrategia más efectiva).")
    
st.info('💬 **Cita clave:** "El trabajo profundo es cada vez más valioso en nuestra economía y al mismo tiempo cada vez más raro."')

with st.expander("📚 Fuente: Audiolibro Analysis"):
    st.markdown("- **Transcript:** `20251228-DEEP-WORK-CONCENTRATE-Cal-Newport-AUDIOLIBRO-RESUMEN-LIBRO-ESPAÑOL-FACIL.txt`")

st.divider()

# 3. Success Is Hard
st.header("3. 📹 Success Is Hard (Sistemas > Voluntad)")

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 🎥 Video Essay")
    st.write("**Sistema vs Voluntad**")
    st.caption("Análisis de hábitos de alto rendimiento")

with col2:
    st.subheader("Conceptos Aplicados")

    st.markdown("**Diseño Ambiental (Anti-Voluntad)**")
    st.write("📌 **Uso en App:** Recordatorios de Modo Avión y configuración de entorno.")
    st.write("📌 'No te elevas a tus metas, caes al nivel de tus sistemas'.")
    st.caption("Aplicación: Eliminar distracciones visibles antes de empezar.")

    st.markdown("**Regla 'Never Miss Twice'**")
    st.write("📌 **Uso en App:** Lógica de rachas y alertas en Dashboard.")
    st.write("📌 Un día perdido es un accidente. Dos días es el inicio de una nueva identidad.")

st.info('💬 **Cita clave:** "Success is hard until you build systems like this."')

with st.expander("📹 Fuente: Video Analysis"):
    st.markdown("- **Transcript:** `20260108-Success-Is-Hard-Until-You-Build-Systems-Like-This.txt`")

st.divider()

# 4. Brian Tracy
st.header("4. 🌅 Brian Tracy - Mentalidad de Ganador")

col1, col2 = st.columns([1, 2])

with col1:
    st.image("https://covers.openlibrary.org/b/id/8258957-L.jpg", width=200)

with col2:
    st.subheader("Conceptos Aplicados")

    st.markdown("**Morning Mastery (El Ritual)**")
    st.write("📌 **Uso en App:** Módulo 'Morning Mastery' activo.")
    st.write("📌 Entrenar el cerebro cada mañana antes de empezar a trabajar (5 pasos cognitivos).")

    st.markdown("**Eat That Frog**")
    st.write("📌 **Uso en App:** Indicador visual de tarea prioritaria.")
    st.write("📌 Haz lo más difícil primero y lo peor del día ya habrá pasado.")

st.info('💬 **Cita clave:** "Trágate ese sapo al empezar el día."')

with st.expander("🌅 Fuente: Video Analysis"):
    st.markdown("- **Transcript:** `20260108-Mentalidad-de-Ganador-Cómo-Entrenar-tu-Cerebro-cada-Mañana-🧠🔥-Brian-Tracy.txt`")

st.divider()

# James Clear (Mantenido como referencia base)
st.header("5. 📖 James Clear - Atomic Habits (Base Teórica)")
st.markdown("""
*Aunque los conceptos específicos anteriores vienen de los videos analizados, **Atomic Habits** provee el vocabulario base (Identidad, Sistemas) que une todo.*
""")
st.markdown("- **Identity-Based Habits:** Cada acción es un voto por la persona que quieres ser.")

st.divider()

st.header("🎯 Por Qué Estas Referencias Importan")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 🧬 Neuroplasticidad
    Los hábitos cambian la estructura
    física del cerebro mediante
    repetición consistente
    """)

with col2:
    st.markdown("""
    ### 🎯 Atención Enfocada
    La capacidad de concentración
    profunda es la ventaja competitiva
    del siglo XXI
    """)

with col3:
    st.markdown("""
    ### ⚙️ Sistemas > Voluntad
    Los sistemas bien diseñados
    eliminan la necesidad de
    fuerza de voluntad
    """)

from modules.ui_components import render_sidebar_footer
render_sidebar_footer()

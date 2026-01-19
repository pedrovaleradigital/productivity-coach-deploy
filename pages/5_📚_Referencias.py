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

# James Clear
st.header("1. 📖 James Clear - Atomic Habits")

col1, col2 = st.columns([1, 2])

with col1:
    st.image("https://covers.openlibrary.org/b/id/12644949-L.jpg", width=200)

with col2:
    st.subheader("Conceptos Aplicados")

    st.markdown("**Identity-Based Habits (Hábitos basados en Identidad)**")
    st.write("📌 Cada acción es un 'voto' por la persona que quieres ser")
    st.caption("Aplicación: Sistema de Identidad Dual (Empresario vs Profesional MarTech)")

    st.markdown("**Never Miss Twice Rule**")
    st.write("📌 Si pierdes un día está bien, pero nunca pierdas dos días seguidos")
    st.caption("Aplicación: Regla de oro para rachas de código y hábitos diarios")

    st.markdown("**Make it Easy / Make it Hard**")
    st.write("📌 Reduce la fricción para buenos hábitos, aumenta la fricción para malos hábitos")
    st.caption("Aplicación: Framework 'Sistema > Motivación' (diseño de fricción)")

st.info('💬 **Cita clave:** "Every action that you take is a vote for the person that you wish to become."')

with st.expander("📖 Más sobre Atomic Habits"):
    st.markdown("""
    **Atomic Habits** es uno de los libros de productividad más vendidos mundialmente.

    **Ideas principales:**
    - Los hábitos se forman mediante repetición, no motivación
    - El cambio real viene de cambiar tu identidad, no tus objetivos
    - Los pequeños cambios (1% mejor cada día) se componen exponencialmente

    **Dónde conseguirlo:**
    - [Amazon](https://www.amazon.com/Atomic-Habits-Proven-Build-Break/dp/0735211299)
    - Audiolibro en Audible
    - Resúmenes en YouTube
    """)

st.divider()

# Cal Newport
st.header("2. 🔥 Cal Newport - Deep Work")

col1, col2 = st.columns([1, 2])

with col1:
    st.image("https://covers.openlibrary.org/b/id/8394677-L.jpg", width=200)

with col2:
    st.subheader("Conceptos Aplicados")

    st.markdown("**Deep Work vs Shallow Work**")
    st.write("📌 **Uso en App:** Base para el 'Focus Timer' y las métricas de 'Deep Work'.")
    st.write("📌 El trabajo profundo (sin distracciones) es cada vez más valioso y raro")
    st.caption("Aplicación: Protocolo 3x60 Deep Work (bloques de 3 horas matutinas)")

    st.markdown("**Estrategia Rítmica**")
    st.write("📌 **Uso en App:** Tu 'Resumen Semanal' mide cuántos días lograste bloques de código consecutivos.")
    st.write("📌 Horarios fijos diarios para Deep Work (la estrategia más efectiva)")
    st.caption("Aplicación: Bloques inamovibles de 8:00-11:00 AM para Daily 3")

    st.markdown("**Entrenar el Aburrimiento**")
    st.write("📌 No buscar dopamina inmediata constantemente")
    st.caption("Aplicación: Modo Avión durante sesiones de enfoque")

st.info('💬 **Cita clave:** "El trabajo profundo es cada vez más valioso en nuestra economía y al mismo tiempo cada vez más raro."')

with st.expander("📖 Más sobre Deep Work"):
    st.markdown("""
    **Deep Work** explica por qué la capacidad de concentración profunda se ha convertido
    en una ventaja competitiva crucial en la economía moderna.

    **Estrategias de Deep Work:**
    1. **Monástica**: Aislamiento total (poco práctico)
    2. **Bimodal**: Periodos largos de aislamiento (ej. una semana al mes)
    3. **Rítmica**: Horarios fijos diarios ← **Recomendada** (nuestra implementación)
    4. **Periodística**: Para expertos que pueden entrar en flow rápidamente

    **Regla del 3x60:**
    - 3 horas matutinas dedicadas exclusivamente a trabajo cognitivamente exigente
    - Sin emails, sin reuniones, sin distracciones
    - Tu "tanque de gasolina" mental está al 100%

    **Dónde conseguirlo:**
    - [Amazon](https://www.amazon.com/Deep-Work-Focused-Success-Distracted/dp/1455586692)
    - Audiolibro en español disponible
    """)

st.divider()

# Rob Dial
st.header("3. 🎙️ Rob Dial - The Mindset Mentor")

col1, col2 = st.columns([1, 2])

with col1:
    st.image("https://m.media-amazon.com/images/I/41D2vXp7CGL._SL500_.jpg", width=200)
    st.markdown("### Podcast")
    st.write("Episodios semanales sobre mindset y productividad")
    st.caption("Disponible en: Spotify, Apple Podcasts")

with col2:
    st.subheader("Conceptos Aplicados")

    st.markdown("**Consistencia > Motivación**")
    st.write("📌 **Uso en App:** La métrica 'Racha de Código' en el Dashboard se basa 100% en este principio.")
    st.write("📌 La motivación es temporal, la consistencia es carácter")
    st.caption("Aplicación: Framework completo 'Sistema > Motivación'")

    st.markdown("**La Motivación Sigue a la Acción**")
    st.write("📌 No esperes sentirte motivado para actuar")
    st.caption("Aplicación: Mínimo No Negociable (actúa primero, la motivación vendrá)")

    st.markdown("**Non-Negotiables**")
    st.write("📌 **Uso en App:** Los 'Checkboxes' del sidebar son tus 'No Negociables' diarios.")
    st.write("📌 Eliminar la negociación mental sobre hábitos críticos")
    st.caption("Aplicación: Código diario sin excepciones")

st.info('💬 **Citas clave:**\\n\\n"Motivation is the spark. Consistency is the fire that just keeps burning long after the spark has gone away."\\n\\n"Motivation follows action. You need to get yourself moving to take action."')

with st.expander("🎙️ Episodios Recomendados"):
    st.markdown("""
    **Episodios clave del podcast:**
    - "Why Consistency Always Wins" (Video 32 analizado)
    - "How to Become the Best at What You Do" (Video 29 analizado)
    - "The Power of Non-Negotiables"

    **Filosofía central:**
    - Las personas consistentes siempre vencen a las personas motivadas
    - La acción genera motivación, no al revés
    - Los sistemas eliminan la necesidad de motivación

    **Escúchalo en:**
    - [Spotify](https://open.spotify.com/show/0oVM4LuMGD2p4oT9rOGQLc)
    - [Apple Podcasts](https://podcasts.apple.com/us/podcast/the-mindset-mentor/id1270663640)
    """)

st.divider()

# Brian Tracy
st.header("4. 🌅 Brian Tracy - Morning Mastery")

col1, col2 = st.columns([1, 2])

with col1:
    st.image("https://covers.openlibrary.org/b/id/8258957-L.jpg", width=200)

with col2:
    st.subheader("Conceptos Aplicados")

    st.markdown("**Morning Mastery Ritual**")
    st.write("📌 **Uso en App:** El botón 'Morning Mastery' en el Sidebar dispara este checklist.")
    st.write("📌 Rituales matutinos para establecer el tono del día")
    st.caption("Aplicación: Protocolo de 5 pasos en la app")

    st.markdown("**Tracking Sistemático**")
    st.write("📌 **Uso en App:** Dashboard de Métricas y visualización de consistencia.")
    st.write("📌 Templates y sistemas para tracking de hábitos")
    st.caption("Aplicación: Dashboard de Consistencia en Airtable")

with st.expander("🌅 El Ritual de Morning Mastery"):
    st.markdown("""
    **Los 5 pasos implementados en esta app:**

    1. **Despertar Consciente**: No agarrar el celular inmediatamente
    2. **Gratitud Activa**: 3 cosas específicas por las que agradecer
    3. **Visualización**: Visualiza el sistema funcionando, no solo el éxito
    4. **Compromiso de Acción**: Define tus Daily 3
    5. **Declaración de Identidad**: Refuerza quién eres

    **Por qué funciona:**
    - Establece estado mental positivo antes de entrar al día
    - Reduce ansiedad matutina
    - Conecta acciones del día con identidad
    """)

st.divider()

# Principios adicionales
st.header("5. 🧠 Principios de Productividad Científica")

st.markdown("**The Performance Paradox**")
st.write("📌 Para producir más, a menudo necesitas hacer menos")
st.caption("Aplicación: Descanso y planificación son productivos, no solo trabajo continuo")

st.markdown("**The Obvious Target Trap**")
st.write("📌 Evitar optimizar lo obvio (apps, herramientas) en lugar de priorizar bien")
st.caption("Aplicación: Enfoque en priorización real, no en buscar la 'herramienta perfecta'")

st.divider()

# Recursos adicionales
st.header("📖 Recursos Recomendados")

tab1, tab2, tab3 = st.tabs(["Libros", "Podcasts", "Videos"])

with tab1:
    st.markdown("""
    ### Libros Fundamentales

    1. **Atomic Habits** - James Clear
       - Hábitos e identidad
       - [Amazon](https://www.amazon.com/Atomic-Habits-Proven-Build-Break/dp/0735211299)

    2. **Deep Work** - Cal Newport
       - Concentración profunda
       - [Amazon](https://www.amazon.com/Deep-Work-Focused-Success-Distracted/dp/1455586692)

    3. **The Power of Habit** - Charles Duhigg
       - Neurociencia de hábitos
       - [Amazon](https://www.amazon.com/Power-Habit-What-Life-Business/dp/081298160X)

    4. **Tiny Habits** - BJ Fogg
       - Diseño de comportamiento
       - [Amazon](https://www.amazon.com/Tiny-Habits-Changes-Change-Everything/dp/0358003326)
    """)

with tab2:
    st.markdown("""
    ### Podcasts

    1. **The Mindset Mentor** - Rob Dial
       - Episodios sobre consistencia y disciplina
       - [Spotify](https://open.spotify.com/show/0oVM4LuMGD2p4oT9rOGQLc)

    2. **Deep Questions** - Cal Newport
       - Productividad profunda y vida enfocada
       - [Spotify](https://open.spotify.com/show/0e9lFr3AdJByoBpM6tAbxD)
    """)

with tab3:
    st.markdown("""
    ### Videos Analizados (Fuente-Conocimiento)

    Estos videos fueron analizados para crear esta estrategia:

    - **Video 32**: "Why Consistency Always Wins - Power of Consistency"
    - **Video 33**: "Success Is Hard" (Systems vs Willpower)
    - **Audiolibro**: "Deep Work - Cal Newport" (Resumen en español)

    *Todos los videos están en la carpeta Transcripts/ del proyecto*
    """)

st.divider()

# Por qué importa
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

st.success("""
**La diferencia fundamental:**

No dependes de motivación o disciplina. Diseñas un **entorno y sistema**
que hace que el comportamiento correcto sea inevitable.

Eso es lo que esta app implementa.
""")

# Footer
st.caption("💡 **Próximos pasos:** Lee al menos uno de estos libros para profundizar en los conceptos que usas a diario en esta app.")
st.caption("📚 Todas las fuentes están verificadas en los transcripts y análisis de la carpeta del proyecto.")

from modules.ui_components import render_sidebar_footer
render_sidebar_footer()

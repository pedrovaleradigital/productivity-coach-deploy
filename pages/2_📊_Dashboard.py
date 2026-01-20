"""
Dashboard de Métricas de Productividad
"""
import streamlit as st
from modules.dashboard_builder import DashboardBuilder
from modules.auth import check_authentication, require_authentication

st.set_page_config(
    page_title="Dashboard - Productivity Coach",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Verificar autenticación
require_authentication()

# Verificar que los clientes estén inicializados
if 'db' not in st.session_state:
    # Intentar recuperar si hay auth
    if 'auth' in st.session_state and st.session_state.user:
        from modules.supabase_client import SupabaseClient
        import os
        st.session_state.db = SupabaseClient(
            os.getenv('SUPABASE_URL'), 
            os.getenv('SUPABASE_KEY'),
            st.session_state.user['id']
        )
        # Inicializar timezone también aquí
        try:
            settings = st.session_state.db.get_user_settings()
            user_tz = settings.get('timezone', os.getenv('TIMEZONE', 'America/Caracas'))
            st.session_state.db.set_timezone(user_tz)
        except:
            pass
    else:
        st.warning("⚠️ Debes pasar por la página principal primero para inicializar el sistema.")
        if st.button("🏠 Ir al Inicio"):
            st.switch_page("app.py")
        st.stop()

# Inicializar dashboard builder
if 'dashboard' not in st.session_state:
    # Obtener nombres de identidad personalizados
    try:
        settings = st.session_state.db.get_user_settings()
        id1 = settings.get('identity_1_name', 'Empresario')
        id2 = settings.get('identity_2_name', 'Profesional')
    except:
        id1, id2 = "Empresario", "Profesional"
        
    st.session_state.dashboard = DashboardBuilder(st.session_state.db, id1, id2)

dashboard = st.session_state.dashboard

from modules.ui_components import render_sidebar

# Header
render_sidebar()

st.title("📊 Dashboard de Consistencia")
st.caption("Visualización de tus hábitos y progreso en ambas identidades")

# Obtener estadísticas
stats = dashboard.get_weekly_summary_stats()
# Obtener estadísticas
stats = dashboard.get_weekly_summary_stats()

# Obtener hábitos dinámicos (Fase 3)
habits = st.session_state.db.get_habits()

# Métricas principales
st.header("📈 Resumen Semanal")

cols = st.columns(len(habits) + 3) # Prioridades (AM), Prioridades (PM), Morning Mastery + Each Habit

with cols[0]:
    st.metric(
        "Prioridades (AM)",
        f"{stats['total_daily_3']}/15",
        delta=f"{(stats['total_daily_3']/15*100):.0f}%" if stats['total_daily_3'] > 0 else None
    )

with cols[1]:
    st.metric(
        "Prioridades (PM)",
        f"{stats['total_priorities']}/15",
        delta=f"{(stats['total_priorities']/15*100):.0f}%" if stats['total_priorities'] > 0 else None
    )

with cols[2]:
    st.metric(
        "Morning Mastery",
        f"{stats['morning_mastery_days']}/5",
        delta=f"{(stats['morning_mastery_days']/5*100):.0f}%" if stats['morning_mastery_days'] > 0 else None
    )

# Métricas para cada hábito dinámico
for i, habit in enumerate(habits):
    if i + 3 < len(cols):
        with cols[i + 3]:
            st.metric(
                habit['name'],
                f"{habit['streak_count']} 🔥",
                delta="Racha"
            )

st.divider()

# Gráficos
col1, col2 = st.columns(2)

with col1:
    st.subheader("🔥 Consistencia de Hábitos")
    
    if habits:
        for habit in habits:
            streak = habit['streak_count']
            # Dummy target for visual gauge (e.g. 30 days or next milestone)
            target = 30 if streak < 30 else streak + 10
            
            st.write(f"**{habit['name']}**")
            progress = min(streak / target, 1.0)
            st.progress(progress, text=f"Racha actual: {streak} días (Meta: {target})")
    else:
        st.info("No hay hábitos configurados aún.")

    # Mensaje de Regla de Oro (Solicitud Usuario)
    st.info("💡 **'Never Miss Twice Rule':** Si pierdes un día está bien, pero nunca pierdas dos días seguidos.")

    with col2:
        st.subheader("⚖️ Balance entre Identidades")
        balance_chart = dashboard.create_identity_balance_chart()
        st.plotly_chart(balance_chart, use_container_width=True, key="balance_chart")

        # Análisis de balance (Mantenido igual)
        if stats['total_daily_3'] > 0 or stats['total_priorities'] > 0:
            ratio = stats['total_daily_3'] / max(stats['total_priorities'], 1)
            if ratio > 1.2:
                st.warning("⚠️ Más enfoque en Identidad #1 (Empresario). Balancea tus prioridades de tarde.")
            elif ratio < 0.8:
                st.warning("⚠️ Más enfoque en Identidad #2 (Profesional). No descuides tu desarrollo personal.")
            else:
                st.success("✅ Balance saludable entre ambas identidades")

    st.divider()

    # Gráfico de consistencia semanal
    st.subheader("📅 Consistencia Semanal (Ejecución)")
    consistency_chart = dashboard.create_weekly_consistency_chart()
    st.plotly_chart(consistency_chart, use_container_width=True, key="consistency_chart")

    st.divider()

    # Mapa de calor
    st.subheader("🔥 Mapa de Calor - Completitud Diaria")
    heatmap = dashboard.create_habit_completion_heatmap()
    st.plotly_chart(heatmap, use_container_width=True, key="heatmap_chart")

# Insights y recomendaciones
st.divider()
st.header("💡 Insights y Recomendaciones")

insights = []

# Insights Dinámicos de Hábitos
for habit in habits:
    if habit['streak_count'] > 7:
        insights.append(f"🔥 **{habit['name']}:** ¡Excelente racha de {habit['streak_count']} días! Mantén el ritmo.")
    elif habit['streak_count'] == 0:
        insights.append(f"🎯 **{habit['name']}:** No rompas la cadena dos veces. Hoy es un buen día para retomar.")

# Insight sobre Prioridades AM
daily_3_rate = (stats['total_daily_3'] / 21) * 100 if stats['total_daily_3'] > 0 else 0
if daily_3_rate < 60:
    insights.append("🎯 **Prioridades AM:** Tu tasa de completitud es baja. Enfócate en tareas más pequeñas y alcanzables")
elif daily_3_rate >= 80:
    insights.append("✅ **Prioridades AM:** Excelente consistencia en tus tareas matutinas")

# Insight sobre Morning Mastery
if stats['morning_mastery_days'] < 3:
    insights.append("🌅 **Morning Mastery:** El ritual matutino establece el tono del día. Intenta hacerlo más seguido")
elif stats['morning_mastery_days'] >= 5:
    insights.append("✅ **Morning Mastery:** Excelente disciplina matutina")

if insights:
    for insight in insights:
        st.write(insight)
else:
    st.info("Comienza a trackear tus hábitos para ver insights personalizados")

# Footer
st.caption("💡 **Recuerda:** La consistencia importa más que la perfección. Cada día es una oportunidad para mejorar.")

from modules.ui_components import render_sidebar_footer
render_sidebar_footer()


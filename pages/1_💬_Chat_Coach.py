"""
Página de Chat con el Productivity Coach
"""
import streamlit as st
from datetime import datetime
from modules.auth import check_authentication, require_authentication

st.set_page_config(
    page_title="Chat - Productivity Coach",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Verificar autenticación
require_authentication()

# Verificar que los clientes estén inicializados
if 'agent' not in st.session_state:
    st.error("⚠️ Error: Vuelve a la página principal primero")
    st.stop()

# Obtener contexto
context = st.session_state.agent._get_current_context()

from modules.ui_components import render_sidebar

# Header
render_sidebar()

st.title("💬 Chat con tu Coach")

# Mostrar identidad activa
if context['is_weekend']:
    st.info("🌴 **Modo Fin de Semana** - Conversación relajada, sin protocolos estrictos")
else:
    identity_emoji = "🚀" if context['identity'] == "Empresario Exitoso" else "💼"
    st.success(f"{identity_emoji} **Identidad activa:** {context['identity']}")

st.divider()

# Inicializar historial de chat en session_state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Botones de acción rápida
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🌅 Saludo de Mañana", use_container_width=True):
        with st.spinner("Generando saludo..."):
            greeting = st.session_state.agent.get_morning_greeting()
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': greeting,
                'timestamp': datetime.now().strftime('%H:%M')
            })
        st.rerun()

with col2:
    if st.button("🔄 Cambio de Identidad", use_container_width=True):
        with st.spinner("Generando recordatorio..."):
            reminder = st.session_state.agent.get_identity_switch_reminder()
            if reminder:
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': reminder,
                    'timestamp': datetime.now().strftime('%H:%M')
                })
                st.rerun()
            else:
                st.warning("Este mensaje solo aplica en días laborables a las 3 PM")

with col3:
    if st.button("🌙 Resumen de Día", use_container_width=True):
        with st.spinner("Generando resumen..."):
            summary = st.session_state.agent.get_evening_summary()
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': summary,
                'timestamp': datetime.now().strftime('%H:%M')
            })
        st.rerun()

with col4:
    if st.button("🗑️ Limpiar Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.agent.memory.clear()
        st.rerun()

st.divider()

# Mostrar historial de chat
chat_container = st.container()

with chat_container:
    if not st.session_state.chat_history:
        st.info("👋 ¡Hola! Escribe un mensaje para empezar o usa los botones de arriba para acciones rápidas.")
    else:
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                with st.chat_message("user"):
                    st.write(message['content'])
                    st.caption(f"🕐 {message['timestamp']}")
            else:
                with st.chat_message("assistant", avatar="🎯"):
                    st.write(message['content'])
                    st.caption(f"🕐 {message['timestamp']}")

# Input de usuario
st.divider()

user_input = st.chat_input("Escribe tu mensaje aquí...")

if user_input:
    # Agregar mensaje del usuario
    st.session_state.chat_history.append({
        'role': 'user',
        'content': user_input,
        'timestamp': datetime.now().strftime('%H:%M')
    })

    # Generar respuesta del agente
    with st.spinner("Pensando..."):
        response = st.session_state.agent.chat(user_input)

    # Agregar respuesta del agente
    st.session_state.chat_history.append({
        'role': 'assistant',
        'content': response,
        'timestamp': datetime.now().strftime('%H:%M')
    })

    st.rerun()

# Sidebar con métricas
with st.sidebar:
    st.header("📊 Estado Actual")

    tracking = context['tracking']

    st.metric(
        "Daily 3",
        f"{tracking.get('identity_1_daily_3_completed', 0)}/3"
    )

    st.metric(
        "Prioridades Tarde",
        f"{tracking.get('identity_2_priorities_completed', 0)}/3"
    )

    code_done = tracking.get('code_commit_done', False)
    st.metric(
        "Código",
        "✅" if code_done else "❌"
    )

    st.metric(
        "Racha",
        f"{context['code_streak']} días 🔥"
    )

    st.subheader("💡 Sugerencias de preguntas")
    st.caption("• ¿Cómo voy hoy?")
    st.caption("• ¿Qué debería hacer ahora?")
    st.caption("• Necesito motivación")
    st.caption("• ¿Cómo mejorar mi racha?")
    st.caption("• Estoy atascado, ¿qué hago?")

# Footer
st.divider()
st.caption("🎯 Productivity Coach - Sistema de Productividad Personal | Desarrollado por Pedro Valera. 2026")

from modules.ui_components import render_sidebar_footer
render_sidebar_footer()

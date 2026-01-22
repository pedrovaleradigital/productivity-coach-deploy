import streamlit as st
from modules.auth import logout
from datetime import datetime
import pytz
import os

# Diccionarios para traducción de fechas a español
DIAS_ES = {
    'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
    'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
}
MESES_ES = {
    'Jan': 'Ene', 'Feb': 'Feb', 'Mar': 'Mar', 'Apr': 'Abr', 'May': 'May', 'Jun': 'Jun',
    'Jul': 'Jul', 'Aug': 'Ago', 'Sep': 'Sep', 'Oct': 'Oct', 'Nov': 'Nov', 'Dec': 'Dic'
}
MESES_FULL_ES = {
    'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo', 'April': 'Abril',
    'May': 'Mayo', 'June': 'Junio', 'July': 'Julio', 'August': 'Agosto',
    'September': 'Septiembre', 'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
}

def get_fecha_espanol(now, formato='corto'):
    """Convierte fecha a español. formato='corto' (Ene) o 'largo' (Enero)"""
    dia_en = now.strftime("%A")
    mes_en = now.strftime("%B") if formato == 'largo' else now.strftime("%b")
    dia_num = now.strftime("%d").lstrip('0')  # Sin cero inicial

    dia_es = DIAS_ES.get(dia_en, dia_en)
    mes_es = MESES_FULL_ES.get(mes_en, mes_en) if formato == 'largo' else MESES_ES.get(mes_en, mes_en)

    return dia_es, dia_num, mes_es

def render_sidebar():
    """Renderiza la barra lateral común con navegación y estado de usuario"""

    # Si no hay auth, no mostrar nada (o mostrar login si se desea, pero app.py maneja el login principal)
    # Asumimos que la página que llama a esto ya verificó auth o es el login

    with st.sidebar:
        st.header("Productivity Coach")

        # Reloj / Fecha
        if 'user' in st.session_state:
            # Obtener timezone
            tz_name = 'America/Caracas' # Default
            if 'user_settings' in st.session_state and st.session_state.user_settings:
                tz_name = st.session_state.user_settings.get('timezone', 'America/Caracas')
            elif 'db' in st.session_state:
                 # Intentar cargar si no esta en session (aunque Settings lo carga)
                 pass

            try:
                user_tz = pytz.timezone(tz_name)
                now = datetime.now(user_tz)

                # Fecha en español
                dia_es, dia_num, mes_es = get_fecha_espanol(now, formato='corto')
                date_str = f"{dia_es}, {dia_num} {mes_es}"
                time_str = now.strftime("%I:%M %p")

                st.caption(f"📅 {date_str}")
                st.caption(f"🕒 {time_str} (Hora de ingreso)")
                st.divider()
            except Exception as e:
                st.error(f"Error hora: {e}")
        
        # Navegación Principal
        st.page_link("app.py", label="Inicio", icon="🏠")
        st.page_link("pages/4_⏱️_Focus_Timer.py", label="Focus Timer", icon="⏱️")
        st.page_link("pages/1_💬_Chat_Coach.py", label="Chat Coach", icon="💬")
        st.page_link("pages/2_📊_Dashboard.py", label="Dashboard", icon="📊")
        st.page_link("pages/5_📚_Referencias.py", label="Referencias", icon="📚")
        st.page_link("pages/3_⚙️_Settings.py", label="Configuración", icon="⚙️")

        st.divider()

def render_sidebar_footer():
    """Renderiza el footer de la barra lateral con información de usuario y logout"""
    with st.sidebar:
        st.divider()
        if 'user' in st.session_state and st.session_state.user:
            user_email = st.session_state.user.get('email', 'Usuario')
            st.caption(f"👤 {user_email}")
            if st.button("🚪 Cerrar Sesión", use_container_width=True, key="sidebar_logout_footer"):
                logout()
                st.rerun()

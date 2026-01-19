import streamlit as st
from modules.auth import logout

def render_sidebar():
    """Renderiza la barra lateral común con navegación y estado de usuario"""
    
    # Si no hay auth, no mostrar nada (o mostrar login si se desea, pero app.py maneja el login principal)
    # Asumimos que la página que llama a esto ya verificó auth o es el login
    
    with st.sidebar:
        st.header("Productivity Coach")
        
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

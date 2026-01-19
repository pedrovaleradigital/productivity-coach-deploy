"""
Página de Login y Registro
"""
import streamlit as st
from modules.auth import AuthManager, check_authentication, logout
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Login - Productivity Coach",
    page_icon="🔐",
    layout="centered"
)

# Inicializar AuthManager
if 'auth' not in st.session_state:
    st.session_state.auth = AuthManager(
        url=os.getenv('SUPABASE_URL'),
        key=os.getenv('SUPABASE_KEY')
    )

# Si ya está autenticado, mostrar info del usuario
if check_authentication():
    st.title("👤 Mi Cuenta")

    user = st.session_state.user

    # Info del usuario
    st.success(f"✅ Sesión activa como: **{user.get('email')}**")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Email", user.get('email', 'N/A'))

    with col2:
        if user.get('last_sign_in_at'):
            # Convertir a UTC-5 (manualmente para evitar dependencias complejas)
            # El string suele venir en ISO: "2024-03-20T10:00:00.00000Z"
            try:
                from datetime import datetime, timedelta
                utc_time_str = user.get('last_sign_in_at').replace('Z', '+00:00')
                utc_dt = datetime.fromisoformat(utc_time_str)
                # Restar 5 horas
                local_dt = utc_dt - timedelta(hours=5)
                formatted_time = local_dt.strftime('%Y-%m-%d %H:%M:%S')
                st.metric("Último acceso (UTC-5)", formatted_time)
            except Exception:
                 st.metric("Último acceso", user.get('last_sign_in_at')[:10])
        else:
             st.metric("Último acceso", "Primer inicio")

    st.divider()

    # Botón de cerrar sesión
    if st.button("🚪 Cerrar Sesión", type="secondary", use_container_width=True):
        logout()
        st.success("Sesión cerrada exitosamente")
        st.rerun()

    st.divider()

    # Accesos rápidos
    st.subheader("🚀 Accesos Rápidos")

    # Botón principal para ir al App
    if st.button("🌟 Ir al App Principal", type="primary", use_container_width=True):
        st.switch_page("app.py")
    
    st.caption("O accesos directos específicos:")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🎯 Dashboard", use_container_width=True):
            st.switch_page("pages/2_📊_Dashboard.py")

    with col2:
        if st.button("💬 Chat Coach", use_container_width=True):
            st.switch_page("pages/1_💬_Chat_Coach.py")
    
    with col3:
        if st.button("⏱️ Focus Timer", use_container_width=True):
            st.switch_page("pages/4_⏱️_Focus_Timer.py")



else:
    # Pantalla de Login/Registro
    st.title("🔐 Acceso a Productivity Coach")

    # Tabs para Login y Registro
    tab1, tab2, tab3 = st.tabs(["🔑 Iniciar Sesión", "📝 Registrarse", "🔄 Recuperar Contraseña"])

    with tab1:
        st.subheader("Iniciar Sesión")

        with st.form("login_form"):
            email = st.text_input(
                "Email",
                placeholder="tu@email.com",
                key="login_email"
            )

            password = st.text_input(
                "Contraseña",
                type="password",
                placeholder="Tu contraseña",
                key="login_password"
            )

            submit = st.form_submit_button("🔑 Iniciar Sesión", use_container_width=True, type="primary")

            if submit:
                if not email or not password:
                    st.error("Por favor completa todos los campos")
                else:
                    with st.spinner("Verificando credenciales..."):
                        success, message, user = st.session_state.auth.sign_in(email, password)

                    if success:
                        st.session_state.user = user
                        st.success(message)
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(message)

    with tab2:
        st.subheader("Crear Cuenta")

        with st.form("register_form"):
            new_email = st.text_input(
                "Email",
                placeholder="tu@email.com",
                key="register_email"
            )

            new_password = st.text_input(
                "Contraseña",
                type="password",
                placeholder="Mínimo 6 caracteres",
                key="register_password"
            )

            confirm_password = st.text_input(
                "Confirmar Contraseña",
                type="password",
                placeholder="Repite tu contraseña",
                key="confirm_password"
            )

            submit_register = st.form_submit_button("📝 Crear Cuenta", use_container_width=True, type="primary")

            if submit_register:
                if not new_email or not new_password or not confirm_password:
                    st.error("Por favor completa todos los campos")
                elif new_password != confirm_password:
                    st.error("Las contraseñas no coinciden")
                elif len(new_password) < 6:
                    st.error("La contraseña debe tener al menos 6 caracteres")
                else:
                    with st.spinner("Creando cuenta..."):
                        success, message = st.session_state.auth.sign_up(new_email, new_password)

                    if success:
                        st.success(message)
                        st.info("💡 Revisa tu bandeja de entrada y confirma tu email para activar la cuenta")
                    else:
                        st.error(message)

    with tab3:
        st.subheader("Recuperar Contraseña")

        with st.form("reset_form"):
            reset_email = st.text_input(
                "Email de tu cuenta",
                placeholder="tu@email.com",
                key="reset_email"
            )

            submit_reset = st.form_submit_button("📧 Enviar Email de Recuperación", use_container_width=True)

            if submit_reset:
                if not reset_email:
                    st.error("Por favor ingresa tu email")
                else:
                    with st.spinner("Enviando email..."):
                        success, message = st.session_state.auth.reset_password(reset_email)

                    if success:
                        st.success(message)
                    else:
                        st.error(message)

    st.divider()

    # Info adicional
    st.caption("💡 **Nota:** La autenticación usa Supabase Auth. Tu contraseña está encriptada y segura.")

# Footer
st.divider()
st.caption("🎯 Productivity Coach - Sistema de Productividad Personal | Desarrollado por Pedro Valera. 2026")

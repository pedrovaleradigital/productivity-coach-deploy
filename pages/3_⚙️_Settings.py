"""
Página de Configuración
"""
import streamlit as st
import time
import pytz
import os
from dotenv import load_dotenv
from modules.auth import check_authentication, require_authentication

st.set_page_config(
    page_title="Settings - Productivity Coach",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_dotenv()

# Verificar autenticación
require_authentication()

from modules.ui_components import render_sidebar

# Initialize sidebar
render_sidebar()

st.title("⚙️ Configuración")

# Gestión de Identidades (Nueva Sección)
st.header("🧠 Personalizar Identidades")
st.caption("Define el nombre de tus identidades duales para que se ajusten a tus objetivos.")

# Cargar settings actuales
if 'db' in st.session_state:
    if 'user_settings' not in st.session_state:
        st.session_state.user_settings = st.session_state.db.get_user_settings()
    
    current_settings = st.session_state.user_settings
    
    with st.form("identity_settings_form"):
        col1, col2 = st.columns(2)
        with col1:
            id1 = st.text_input("Nombre Identidad #1 (Mañana)", value=current_settings.get('identity_1_name', 'Empresario Exitoso'))
            # Timezone Selector
            all_timezones = pytz.all_timezones
            current_tz = current_settings.get('timezone', 'America/Caracas')
            if current_tz not in all_timezones:
                current_tz = 'America/Caracas'
            timezone_idx = all_timezones.index(current_tz)
            selected_timezone = st.selectbox("Zona Horaria", all_timezones, index=timezone_idx)
            
        with col2:
            id2 = st.text_input("Nombre Identidad #2 (Tarde)", value=current_settings.get('identity_2_name', 'Profesional MarTech'))
            
        if st.form_submit_button("Guardar Configuración", use_container_width=True, type="primary"):
            # Detectar si cambió la timezone
            old_timezone = current_settings.get('timezone', 'America/Caracas')
            timezone_changed = (old_timezone != selected_timezone)

            success, msg = st.session_state.db.update_user_settings(id1, id2, selected_timezone)
            if success:
                st.session_state.user_settings = {'identity_1_name': id1, 'identity_2_name': id2, 'timezone': selected_timezone}

                # Si cambió la timezone, limpiar session_state para forzar recarga completa
                if timezone_changed:
                    st.session_state.db.set_timezone(selected_timezone)
                    # Limpiar datos de tracking en memoria para que se recarguen con la nueva fecha
                    if 'agent' in st.session_state:
                        del st.session_state['agent']
                    if 'db' in st.session_state:
                        del st.session_state['db']
                    st.success("✅ Zona horaria actualizada. Recargando sistema...")
                    time.sleep(1.5)
                    # Usar JavaScript para hacer refresh completo de la página
                    st.markdown(
                        """<meta http-equiv="refresh" content="0; url=/" />""",
                        unsafe_allow_html=True
                    )
                    st.stop()
                else:
                    st.success(msg)
                    time.sleep(1)
                    st.rerun()
            else:
                st.error(msg)
else:
    st.warning("⚠️ Conecta la base de datos (Login) para personalizar identidades.")

st.divider()

# --- GESTIÓN DE HÁBITOS (Fase 3) ---
st.header("🧱 Gestión de Hábitos")
st.caption("Define hasta 3 hábitos clave que quieres trackear diariamente (Ej: Código, Prospección, Lectura).")

if 'db' in st.session_state:
    # 1. Obtener hábitos actuales
    if 'habits_list' not in st.session_state:
        st.session_state.habits_list = st.session_state.db.get_habits()
    
    current_habits = st.session_state.habits_list
    
    # 2. Formulario de Nuevo Hábito (Si hay espacio)
    if len(current_habits) < 3:
        with st.expander("➕ Agregar Nuevo Hábito", expanded=False):
            with st.form("new_habit_form"):
                new_habit_name = st.text_input("Nombre del Hábito", placeholder="Ej: Prospección Diaria")
                if st.form_submit_button("Crear Hábito"):
                    if new_habit_name:
                        success, msg = st.session_state.agent.create_habit(new_habit_name)
                        if success:
                            st.success(msg)
                            # Recargar lista
                            st.session_state.habits_list = st.session_state.db.get_habits()
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.warning("El nombre no puede estar vacío")
    else:
        st.info("ℹ️ Has alcanzado el límite de 3 hábitos. Elimina uno para agregar otro.")

    # 3. Listar y Editar Hábitos Existentes
    if current_habits:
        st.subheader("Tus Hábitos Activos")
        for habit in current_habits:
            with st.container():
                c1, c2, c3 = st.columns([3, 1, 1])
                with c1:
                    st.markdown(f"**{habit['name']}** (Racha: {habit['streak_count']} 🔥)")
                with c2:
                    # Renombrar (Modal simulado o expander)
                    with st.popover("✏️ Editar"):
                        new_name = st.text_input("Nuevo nombre", value=habit['name'], key=f"edit_{habit['id']}")
                        st.warning("⚠️ Cambiar el nombre reinicia la racha a 0.")
                        if st.button("Guardar Cambios", key=f"save_{habit['id']}"):
                            st.session_state.agent.update_habit(habit['id'], new_name)
                            st.session_state.habits_list = st.session_state.db.get_habits()
                            st.rerun()
                with c3:
                    if st.button("🗑️", key=f"del_{habit['id']}", help="Eliminar hábito"):
                        st.session_state.agent.delete_habit(habit['id'])
                        st.session_state.habits_list = st.session_state.db.get_habits()
                        st.rerun()
                st.divider()

else:
    st.warning("⚠️ Conecta la base de datos para gestionar hábitos.")

# --- MORNING MASTERY EDITOR (Fase 3) ---
st.divider()
st.header("🌅 Morning Mastery")
st.caption("Personaliza los pasos de tu ritual matutino.")

if 'db' in st.session_state:
    # Cargar texto actual
    current_mm_text = st.session_state.agent.get_morning_mastery_text()
    
    with st.form("mm_editor"):
        new_mm_text = st.text_area(
            "Pasos del Ritual", 
            value=current_mm_text, 
            height=200,
            help="Este texto aparecerá cuando inicies tu Morning Mastery en el dashboard."
        )
        if st.form_submit_button("Guardar Ritual"):
            st.session_state.agent.update_morning_mastery_text(new_mm_text)
            st.success("✅ Ritual actualizado")
            time.sleep(1)

st.divider()

st.header("🔧 Variables de Entorno")

st.info("Las variables de entorno se cargan desde el archivo `.env`. Para cambiarlas, edita ese archivo y reinicia la aplicación.")

# Mostrar estado de las variables (sin mostrar los valores completos)
col1, col2 = st.columns(2)

with col1:
    st.subheader("API Keys")

    anthropic_key = os.getenv('ANTHROPIC_API_KEY', '')
    if anthropic_key:
        st.success(f"✅ Claude API Key configurada ({anthropic_key[:8]}...)")
    else:
        st.error("❌ Claude API Key no configurada")

    supabase_url = os.getenv('SUPABASE_URL', '')
    if supabase_url:
        st.success(f"✅ Supabase URL configurada ({supabase_url[:15]}...)")
    else:
        st.error("❌ Supabase URL no configurada")

    supabase_key = os.getenv('SUPABASE_KEY', '')
    if supabase_key:
        st.success(f"✅ Supabase Key configurada ({supabase_key[:5]}...)")
    else:
        st.error("❌ Supabase Key no configurada")

with col2:
    st.subheader("Configuración Adicional")

    timezone = os.getenv('TIMEZONE', 'America/Caracas')
    st.info(f"⏰ Timezone: **{timezone}**")

    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
    if telegram_token:
        st.success(f"✅ Telegram Bot configurado")
    else:
        st.warning("⚠️ Telegram Bot no configurado (opcional)")

st.divider()

st.header("📚 Guía de Configuración")

st.markdown("""
### Cómo configurar las API Keys:

1. **Claude API Key:**
   - Ve a [console.anthropic.com](https://console.anthropic.com)
   - Crea una API key
   - Cópiala en el archivo `.env` como `ANTHROPIC_API_KEY=tu-key-aqui`

2. **Supabase:**
   - La base de datos se configura automáticamente con `setup_database.sql`
   - Asegurate de tener `SUPABASE_URL` y `SUPABASE_KEY` en tu `.env`
   - Para ver la guía completa, revisa `SUPABASE_SETUP.md`

3. **Telegram (Opcional):**
   - Habla con [@BotFather](https://t.me/botfather) en Telegram
   - Crea un nuevo bot con `/newbot`
   - Copia el token que te da
   - Para obtener tu Chat ID, envía un mensaje a tu bot y ve a:
     `https://api.telegram.org/bot<TU_TOKEN>/getUpdates`
""")

st.divider()

st.header("🎨 Personalización")

st.markdown("""
### Cambiar el tema:

Edita el archivo `.streamlit/config.toml` para personalizar colores:

```toml
[theme]
primaryColor = "#00D4AA"        # Color principal
backgroundColor = "#0E1117"      # Fondo
secondaryBackgroundColor = "#262730"  # Fondo secundario
textColor = "#FAFAFA"           # Color del texto
```
""")

st.divider()

st.header("ℹ️ Información del Sistema")

if 'agent' in st.session_state:
    context = st.session_state.agent._get_current_context()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Fecha", context['date'])
        st.metric("Hora", context['time'])

    with col2:
        st.metric("Día", context['day'])
        st.metric("Identidad Activa", context['identity'] or "Fin de semana")

    with col3:
        st.metric("Racha de Código", f"{context['code_streak']} días 🔥")
        st.metric("Modo", "Fin de semana" if context['is_weekend'] else "Laboral")

st.divider()

st.header("🗑️ Acciones")

col1, col2 = st.columns(2)

with col1:
    if st.button("🔄 Reiniciar Memoria del Chat", use_container_width=True):
        if 'agent' in st.session_state:
            st.session_state.agent.memory.clear()
            st.success("✅ Memoria del chat reiniciada")
        if 'chat_history' in st.session_state:
            st.session_state.chat_history = []
            st.success("✅ Historial de chat limpiado")

with col2:
    st.button("📥 Exportar Datos (Próximamente)", disabled=True, use_container_width=True)

st.caption("💡 **Tip:** Si cambias las variables de entorno, necesitas reiniciar la aplicación para que los cambios tengan efecto.")

from modules.ui_components import render_sidebar_footer
render_sidebar_footer()

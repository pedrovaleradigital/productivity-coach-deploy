"""
Productivity Coach - App Principal
"""
import streamlit as st
import time
from modules.supabase_client import SupabaseClient
from modules.agent import ProductivityAgent
from modules.auth import AuthManager, check_authentication, logout
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de página
st.set_page_config(
    page_title="Productivity Coach",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar AuthManager (CRÍTICO: Debe ser antes del check)
if 'auth' not in st.session_state:
    st.session_state.auth = AuthManager(
        url=os.getenv('SUPABASE_URL'),
        key=os.getenv('SUPABASE_KEY')
    )
    # Pequeño hack: forzar lectura de cookies en primer render
    # st.session_state.auth.restore_session_from_cookies() 

# Verificar autenticación
if not check_authentication():
    st.title("🎯 Productivity Coach")
    st.warning("⚠️ Debes iniciar sesión para acceder a la aplicación")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("👉 Usa la página de **Login** en el menú lateral para iniciar sesión o crear una cuenta")

        if st.button("🔐 Ir a Login", type="primary", use_container_width=True):
            st.switch_page("pages/0_🔐_Login.py")

    st.stop()

# Inicializar clientes en session_state (solo si está autenticado)
if 'db' not in st.session_state:
    user_id = st.session_state.user.get('id')
    # 1. Inicializar cliente temporal
    temp_client = SupabaseClient(
        url=os.getenv('SUPABASE_URL'),
        key=os.getenv('SUPABASE_KEY'),
        user_id=user_id
    )
    
    # 2. Obtener timezone del usuario
    settings = temp_client.get_user_settings()
    user_tz = settings.get('timezone', os.getenv('TIMEZONE', 'America/Caracas'))
    
    # 3. Configurar timezone correcto
    temp_client.set_timezone(user_tz)
    
    # 4. Guardar en session_state
    st.session_state.db = temp_client

if 'agent' not in st.session_state:
    # Obtener timezone ya configurado en el cliente DB
    current_tz = str(st.session_state.db.timezone.zone)
    
    st.session_state.agent = ProductivityAgent(
        api_key=os.getenv('ANTHROPIC_API_KEY'),
        db_client=st.session_state.db,
        timezone=current_tz
    )

# Obtener contexto actual
context = st.session_state.agent._get_current_context()

# Header
st.title("🎯 Productivity Coach")

# Mostrar identidad activa
if context['is_weekend']:
    st.info("🌴 **Modo Fin de Semana** - Sin protocolo estricto")
else:
    identity_emoji = "🚀" if context['identity'] == "Empresario Exitoso" else "💼"
    st.success(f"{identity_emoji} **Identidad activa:** {context['identity']}")

from modules.ui_components import render_sidebar

# Sidebar
render_sidebar()

tracking = context['tracking']

# --- LOGICA DEL SIDEBAR (Fase 3) ---
with st.sidebar:
    # 1. MORNING MASTERY (Personalizado)
    morning_done = tracking.get('morning_mastery_done', False)
    
    if not morning_done and not context['is_weekend']:
        # Usar un popover o expander para mostrar el ritual antes de marcarlo
        with st.expander("🌅 Morning Mastery", expanded=True):
            # Obtener texto personalizado
            mm_text = st.session_state.agent.get_morning_mastery_text()
            st.markdown(mm_text)
            
            if st.button("✅ Completar Ritual", use_container_width=True, type="primary"):
                st.session_state.agent.mark_morning_mastery_done()
                st.rerun()
                
    elif morning_done:
        st.success("✨ Morning Mastery Completado")

    st.divider()

    st.header("📊 Resumen de Hoy")
    # tracking ya definido arriba

    # Calcular progreso real desde detalles JSON
    d3_prog = tracking.get('identity_1_daily_3_details', [])
    d3_count = sum(1 for t in d3_prog if t.get('done', False)) if isinstance(d3_prog, list) else tracking.get('identity_1_daily_3_completed', 0)

    st.metric("Mañana", f"{d3_count}/3", delta=None)

    p_prog = tracking.get('identity_2_priorities_details', [])
    p_count = sum(1 for t in p_prog if t.get('done', False)) if isinstance(p_prog, list) else tracking.get('identity_2_priorities_completed', 0)

    st.metric("Tarde", f"{p_count}/3", delta=None)

    # 2. HÁBITOS DINÁMICOS (Reemplaza Code Streak estático)
    st.subheader("🧱 Mis Hábitos")
    
    # Obtener hábitos del contexto
    habits = context.get('habits', [])
    
    if habits:
        for habit in habits:
            # Check si ya se completó hoy (usando last_completed_at)
            is_done_today = False
            if habit.get('last_completed_at'):
                last_date = habit['last_completed_at'].split('T')[0] # Simple date check
                if last_date == context['date']:
                    is_done_today = True
            
            c1, c2 = st.columns([3, 1])
            with c1:
                st.caption(f"{habit['name']}")
                st.write(f"🔥 {habit['streak_count']} días")
            with c2:
                if not is_done_today:
                    if st.button("✅", key=f"hab_{habit['id']}", help=f"Marcar {habit['name']} como hecho"):
                        res = st.session_state.agent.mark_habit_done(habit['id'])
                        if res['success']:
                            st.toast(f"¡Bien! {res['message']}")
                            time.sleep(0.5)
                            st.rerun()
                else:
                    st.write("✅")
            st.divider()
    else:
        st.info("No tienes hábitos configurados. Ve a Settings para agregarlos.")

# Recuperar Nombres de Identidad (Personalización)
if 'user_settings' not in st.session_state and 'db' in st.session_state:
    st.session_state.user_settings = st.session_state.db.get_user_settings()

user_settings = st.session_state.get('user_settings', {})
id1_name = user_settings.get('identity_1_name', 'Empresario Exitoso')
id2_name = user_settings.get('identity_2_name', 'Profesional MarTech')

# Contenido principal
col1, col2 = st.columns([3, 1])

with col1:
    st.header("⚡ Tracking Rápido")

    # CONTEXTO ESTRATÉGICO (Nuevo Expander)
    with st.expander("🧠 Estrategia: Protocolo 3x60 & Diseño Ambiental"):
        st.markdown("""
        ### 🧪 La Ciencia detrás del Sistema
        
        **1. Protocolo '3x60 Deep Work':**
        Las primeras 3 horas del día son biológicamente tus horas pico de atención.
        *   **Regla:** Bloquea 8:00 - 11:00 AM solo para las 3 tareas críticas.
        *   **Condición:** Modo Avión / No Slack / No Email.
        
        **2. Diseño Ambiental (Anti-Voluntad):**
        No confíes en tu disciplina, confía en tu entorno.
        *   ✅ **Facilidad:** Deja lo que necesitas listo la noche anterior (ej. VS Code abierto).
        *   ⛔ **Fricción:** Usa bloqueadores de apps para redes sociales durante de Deep Work.
        *   🐸 **Eat the Frog:** Haz lo más difícil primero.
        
        [**¿Necesitas enfocarte? Usa el Focus Timer**](pages/4_⏱️_Focus_Timer.py)
        """)

# --- SECCIÓN 1: EMPRESARIO (Identidad #1) ---
    st.subheader(f"Prioridades de Mañana (Identidad #1: {id1_name})")
    st.caption("🚀 Estrategia: Tareas que construyen el futuro y hacen crecer el negocio")

    # Definir today_tracking que faltaba
    today_tracking = context['tracking']

    # Recuperar datos guardados
    d3_details = today_tracking.get('identity_1_daily_3_details', [])
    
    # Fallback: Si no hay detalles JSON, intentar recuperar de la lista antigua
    if (not d3_details or len(d3_details) == 0):
        legacy_list = today_tracking.get('identity_1_daily_3_list', [])
        if legacy_list and isinstance(legacy_list, list):
            d3_details = [{"text": t, "done": False} for t in legacy_list]

    # Asegurar que sea una lista válida de 3 elementos
    if not isinstance(d3_details, list):
        d3_details = []
    
    # Rellenar hasta 3 si falta alguno
    while len(d3_details) < 3:
        d3_details.append({"text": "", "done": False})

    # Callback para auto-guardado de Checkboxes
    def auto_save_daily_3():
        # Reconstruir el estado actual desde los widgets
        current_data = []
        for j in range(3):
            is_done = st.session_state.get(f"d3_check_{j}", False)
            text_val = st.session_state.get(f"d3_text_{j}", "")
            current_data.append({"text": text_val, "done": is_done})
        
        st.session_state.db.update_daily_3(current_data)

    # Construir UI con desbloqueo progresivo
    d3_inputs = []
    morning_feedback = st.session_state.agent.get_task_feedback("morning")

    for i in range(3):
        c1, c2 = st.columns([0.05, 0.95])

        # Etiqueta especial para Tarea 1 (Eat the frog)
        label_prefix = "Tarea 1 (🐸 EAT THE FROG)" if i == 0 else f"Tarea {i+1}"
        placeholder_text = "Ej: Diseñar oferta... (Tarea que sea Mínimo No Negociable)"

        # Obtener valor actual del input (estado Session State o DB)
        current_text_val = d3_details[i].get('text', '')

        # Desbloqueo progresivo: Tarea i solo habilitada si tarea i-1 tiene texto guardado
        is_task_locked = False
        if i > 0:
            prev_task_text = d3_details[i-1].get('text', '').strip()
            is_task_locked = len(prev_task_text) == 0

        with c2:
            text_val = st.text_input(
                label_prefix,
                value=current_text_val,
                key=f"d3_text_{i}",
                placeholder=placeholder_text if not is_task_locked else "🔒 Completa la tarea anterior primero",
                help="[Mínimo No Negociable]: Define la versión ridículamente pequeña de la tarea para eliminar la resistencia de inicio.",
                disabled=is_task_locked
            )

        with c1:
            st.write("")
            st.write("")
            # Disable checkbox si texto vacío o tarea bloqueada
            is_disabled = len(text_val.strip()) == 0 or is_task_locked

            is_done = st.checkbox(
                "Done",
                value=d3_details[i].get('done', False),
                key=f"d3_check_{i}",
                label_visibility="collapsed",
                on_change=auto_save_daily_3,
                disabled=is_disabled
            )

        d3_inputs.append({"text": text_val, "done": is_done})

        # Mostrar feedback justo debajo de cada tarea (en orden)
        if i < len(morning_feedback) and morning_feedback[i] and current_text_val.strip():
            st.markdown(f"""<div style="background-color: #1a3a2a; padding: 10px; border-radius: 8px; margin-bottom: 10px; border-left: 3px solid #4ade80;">
<span style="color: #4ade80; font-weight: bold;">Productivity Coach [Tarea #{i+1}]:</span> <em style="color: #a7f3d0;">{morning_feedback[i]}</em>
</div>""", unsafe_allow_html=True)

    if st.button("Guardar Prioridades Mañana", use_container_width=True):
        st.session_state.db.update_daily_3(d3_inputs)
        # Generar y guardar feedback
        with st.spinner("Analizando tareas..."):
            feedbacks = st.session_state.agent.generate_task_feedback(d3_inputs, "morning")
            st.session_state.agent.save_task_feedback(feedbacks, "morning")
        st.success("✅ Prioridades guardadas")
        time.sleep(0.5)
        st.rerun()

    st.divider()

# --- SECCIÓN 2: PROFESIONAL (Identidad #2) ---
    st.subheader(f"Prioridades de Tarde (Identidad #2: {id2_name})")
    st.caption("🛠️ Operación: Tareas de mantenimiento, delivery y ejecución técnica")

    p_details = today_tracking.get('identity_2_priorities_details', [])
    if (not p_details or len(p_details) == 0):
        legacy_list = today_tracking.get('identity_2_priorities_list', [])
        if legacy_list and isinstance(legacy_list, list):
            p_details = [{"text": t, "done": False} for t in legacy_list]
    if not isinstance(p_details, list): p_details = []
    while len(p_details) < 3: p_details.append({"text": "", "done": False})

    def auto_save_priorities():
        current_data = []
        for j in range(3):
            is_done = st.session_state.get(f"p_check_{j}", False)
            text_val = st.session_state.get(f"p_text_{j}", "")
            current_data.append({"text": text_val, "done": is_done})
        st.session_state.db.update_priorities(current_data)

    # Construir UI con desbloqueo progresivo
    p_inputs = []
    afternoon_feedback = st.session_state.agent.get_task_feedback("afternoon")

    for i in range(3):
        c1, c2 = st.columns([0.05, 0.95])

        label_prefix = "Tarea 1 (🐸 EAT THE FROG)" if i == 0 else f"Tarea {i+1}"
        placeholder_text = "Ej: Configurar campaña... (Tarea que sea Mínimo No Negociable)"

        current_text_val = p_details[i].get('text', '')

        # Desbloqueo progresivo: Tarea i solo habilitada si tarea i-1 tiene texto guardado
        is_task_locked = False
        if i > 0:
            prev_task_text = p_details[i-1].get('text', '').strip()
            is_task_locked = len(prev_task_text) == 0

        with c2:
            text_val = st.text_input(
                label_prefix,
                value=current_text_val,
                key=f"p_text_{i}",
                placeholder=placeholder_text if not is_task_locked else "🔒 Completa la tarea anterior primero",
                help="[Mínimo No Negociable]: Define la versión ridículamente pequeña de la tarea.",
                disabled=is_task_locked
            )

        with c1:
            st.write("")
            st.write("")
            # Disable checkbox si texto vacío o tarea bloqueada
            is_disabled = len(text_val.strip()) == 0 or is_task_locked

            is_done = st.checkbox(
                "Done",
                value=p_details[i].get('done', False),
                key=f"p_check_{i}",
                label_visibility="collapsed",
                on_change=auto_save_priorities,
                disabled=is_disabled
            )

        p_inputs.append({"text": text_val, "done": is_done})

        # Mostrar feedback justo debajo de cada tarea (en orden)
        if i < len(afternoon_feedback) and afternoon_feedback[i] and current_text_val.strip():
            st.markdown(f"""<div style="background-color: #1a3a2a; padding: 10px; border-radius: 8px; margin-bottom: 10px; border-left: 3px solid #4ade80;">
<span style="color: #4ade80; font-weight: bold;">Productivity Coach [Tarea #{i+1}]:</span> <em style="color: #a7f3d0;">{afternoon_feedback[i]}</em>
</div>""", unsafe_allow_html=True)

    if st.button("Guardar Prioridades Tarde", use_container_width=True):
        st.session_state.db.update_priorities(p_inputs)
        # Generar y guardar feedback
        with st.spinner("Analizando tareas..."):
            feedbacks = st.session_state.agent.generate_task_feedback(p_inputs, "afternoon")
            st.session_state.agent.save_task_feedback(feedbacks, "afternoon")
        st.success("✅ Prioridades guardadas")
        time.sleep(0.5)
        st.rerun()

    st.divider()

    # LEGACY: Código movido a Sidebar como hábito dinámico
    # Mantenemos esto oculto por ahora o lo quitamos para limpiar la UI
    # Se eliminó la sección "Código del Día" del main body en favor del Sidebar Habit List

with col2:
    st.header("💬 Consulta aquí")
    st.markdown("[Ve a la página de **Chat Coach** para una conversación completa](pages/1_💬_Chat_Coach.py)")

    quick_message = st.text_area(
        "Mensaje rápido",
        placeholder="¿Cómo voy hoy? ¿Qué debería hacer ahora?",
        height=100
    )

    if st.button("Enviar", use_container_width=True):
        if quick_message:
            with st.spinner("Pensando..."):
                response = st.session_state.agent.chat(quick_message)
            st.write(response)

# Footer con instrucciones
st.divider()
st.caption("💡 **Tip:** Usa la página de Chat para conversaciones más profundas y la de Dashboard para ver tus estadísticas semanales")
st.caption("🎯 Productivity Coach - Sistema de Productividad Personal | Desarrollado por Pedro Valera. 2026")

from modules.ui_components import render_sidebar_footer
render_sidebar_footer()

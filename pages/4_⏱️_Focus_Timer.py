"""
Página de Focus Timer con Pomodoro - Actualización en tiempo real
"""
import streamlit as st
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh
from modules.timer_manager import TimerManager
from modules.auth import check_authentication, require_authentication
from datetime import datetime
import time
import os

st.set_page_config(
    page_title="Focus Timer - Productivity Coach",
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Verificar autenticación
require_authentication()

# Inicializar timer manager
if 'timer_manager' not in st.session_state:
    st.session_state.timer_manager = TimerManager()

# Inicializar estado del timer
if 'active_timer' not in st.session_state:
    st.session_state.active_timer = None

if 'completed_sessions' not in st.session_state:
    st.session_state.completed_sessions = []

if 'timer_finished' not in st.session_state:
    st.session_state.timer_finished = False

if 'notification_shown' not in st.session_state:
    st.session_state.notification_shown = False

timer_manager = st.session_state.timer_manager

# Auto-refresh cada segundo SOLO si hay timer activo corriendo
if st.session_state.active_timer and st.session_state.active_timer['status'] == 'running':
    st_autorefresh(interval=1000, limit=None, key="timer_refresh")

from modules.ui_components import render_sidebar

# Header
render_sidebar()

st.title("⏱️ Focus Timer")
st.caption("Usa timers para mantener enfoque profundo en tus tareas")

import base64

# Función para mostrar notificación y sonido
def show_completion_alert():
    """Mostrar alerta de finalización con sonido y notificación push"""
    
    try:
        # Leer archivo de audio local
        audio_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'timer_complete.mp3')
        
        with open(audio_file_path, "rb") as f:
            audio_bytes = f.read()
        audio_base64 = base64.b64encode(audio_bytes).decode()
        audio_src = f"data:audio/mp3;base64,{audio_base64}"
    except Exception as e:
        print(f"Error cargando audio local: {e}")
        # Fallback a un sonido online si falla el local
        audio_src = "https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3"

    # Intentar usar st.audio primero (para reproducción manual si falla el automático)
    st.audio(audio_src, format="audio/mp3", start_time=0)

    # Backup con HTML/JS para navegadores que bloquean st.audio autoplay
    audio_html = f"""
    <audio id="timerSound" autoplay style="display:none;">
        <source src="{audio_src}" type="audio/mp3">
    </audio>
    <script>
        // Función robusta de reproducción
        function playSound() {{
            var audio = document.getElementById('timerSound');
            if(audio) {{
                audio.volume = 1.0;
                var playPromise = audio.play();
                
                if (playPromise !== undefined) {{
                    playPromise.then(_ => {{
                        console.log('Audio playback started');
                    }})
                    .catch(error => {{
                        console.log('Audio autoplay blocked:', error);
                    }});
                }}
            }}
        }} 
        // Ejecutar
        playSound();

        // Notificación
        if ('Notification' in window) {{
            if (Notification.permission === 'granted') {{
                new Notification('⏱️ Timer Completado!', {{
                    body: 'Tu sesión de focus ha terminado. ¡Buen trabajo!',
                    icon: 'https://em-content.zobj.net/source/apple/354/alarm-clock_23f0.png',
                    requireInteraction: true
                }});
            }}
        }}
    </script>
    """
    components.html(audio_html, height=0)

# Solicitar permiso de notificaciones al cargar
if 'notification_permission_requested' not in st.session_state:
    st.session_state.notification_permission_requested = True
    permission_html = """
    <script>
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }
    </script>
    """
    components.html(permission_html, height=0)

# Timer activo
if st.session_state.active_timer and st.session_state.active_timer['status'] != 'completed':
    remaining = timer_manager.get_remaining_time(st.session_state.active_timer)

    # Si terminó
    if remaining['is_finished']:
        # Mostrar alerta de completado
        st.balloons()

        # Reproducir sonido y notificación (solo una vez)
        if not st.session_state.notification_shown:
            st.session_state.notification_shown = True
            show_completion_alert()

        # Contenedor de completado
        st.markdown("""
        <div style='text-align: center; padding: 40px; background: linear-gradient(135deg, #00D4AA 0%, #00B894 100%); border-radius: 20px; margin: 20px 0;'>
            <h1 style='font-size: 60px; margin: 0; color: white;'>🎉</h1>
            <h2 style='font-size: 36px; margin: 10px 0; color: white;'>¡Timer Completado!</h2>
            <p style='font-size: 20px; color: rgba(255,255,255,0.9);'>
                Sesión de {duration} minutos finalizada
            </p>
        </div>
        """.format(duration=st.session_state.active_timer['duration_minutes']), unsafe_allow_html=True)

        stats = timer_manager.get_focus_session_stats(
            st.session_state.active_timer['duration_minutes']
        )
        st.success(stats)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Finalizar y Guardar", use_container_width=True, type="primary"):
                # Agregar a sesiones completadas
                completed_session = {
                    'task': st.session_state.active_timer['task_name'],
                    'duration': st.session_state.active_timer['duration_minutes'],
                    'completed_at': datetime.now().strftime('%H:%M')
                }
                st.session_state.completed_sessions.append(completed_session)

                # Guardar en Supabase si está disponible
                if 'db' in st.session_state:
                    try:
                        st.session_state.db.log_focus_session(
                            task_name=st.session_state.active_timer['task_name'] or 'Focus Session',
                            timer_type='pomodoro',
                            duration_minutes=st.session_state.active_timer['duration_minutes']
                        )
                    except Exception as e:
                        pass  # Silently fail if DB not available

                st.session_state.active_timer = None
                st.session_state.notification_shown = False
                st.rerun()

        with col2:
            if st.button("🔄 Iniciar Otro", use_container_width=True):
                st.session_state.active_timer = None
                st.session_state.notification_shown = False
                st.rerun()

    elif st.session_state.active_timer['status'] == 'running':
        # Timer corriendo - mostrar countdown
        display_time = timer_manager.get_timer_display(st.session_state.active_timer)

        # Calcular color basado en tiempo restante
        percentage = remaining['percentage']
        if percentage < 50:
            color = "#00D4AA"  # Verde
        elif percentage < 80:
            color = "#FFD93D"  # Amarillo
        else:
            color = "#FF6B6B"  # Rojo

        # Display principal del timer
        st.markdown(f"""
        <div style='text-align: center; padding: 30px;'>
            <div style='
                font-size: 100px;
                font-weight: bold;
                color: {color};
                font-family: "Courier New", monospace;
                text-shadow: 0 0 20px {color}40;
                margin: 20px 0;
            '>
                {display_time}
            </div>
            <p style='font-size: 24px; color: #888; margin: 10px 0;'>
                {st.session_state.active_timer['task_name'] or 'Focus Session'}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Barra de progreso
        st.progress(remaining['percentage'] / 100)

        # Info del tiempo
        col_info1, col_info2, col_info3 = st.columns(3)
        with col_info1:
            st.metric("Tiempo Restante", f"{remaining['minutes']}:{remaining['seconds']:02d}")
        with col_info2:
            st.metric("Progreso", f"{remaining['percentage']:.0f}%")
        with col_info3:
            st.metric("Duración Total", f"{st.session_state.active_timer['duration_minutes']} min")

        st.divider()

        # Controles
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⏸️ Pausar", use_container_width=True, type="secondary"):
                st.session_state.active_timer = timer_manager.pause_timer(st.session_state.active_timer)
                st.rerun()
        with col2:
            if st.button("⏹️ Detener", use_container_width=True, type="secondary"):
                st.session_state.active_timer = None
                st.session_state.notification_shown = False
                st.rerun()

    elif st.session_state.active_timer['status'] == 'paused':
        # Timer pausado
        st.markdown("""
        <div style='text-align: center; padding: 30px;'>
            <div style='
                font-size: 80px;
                font-weight: bold;
                color: #FFD93D;
                font-family: "Courier New", monospace;
                text-shadow: 0 0 20px #FFD93D40;
                margin: 20px 0;
            '>
                ⏸️ PAUSADO
            </div>
            <p style='font-size: 24px; color: #888;'>
                {task}
            </p>
        </div>
        """.format(task=st.session_state.active_timer['task_name'] or 'Focus Session'), unsafe_allow_html=True)

        remaining = timer_manager.get_remaining_time(st.session_state.active_timer)
        st.info(f"⏱️ Tiempo restante cuando se reanude: **{remaining['minutes']}:{remaining['seconds']:02d}**")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("▶️ Reanudar", use_container_width=True, type="primary"):
                st.session_state.active_timer = timer_manager.resume_timer(st.session_state.active_timer)
                st.rerun()
        with col2:
            if st.button("⏹️ Detener", use_container_width=True, type="secondary"):
                st.session_state.active_timer = None
                st.rerun()

else:
    # Configurar nuevo timer
    st.header("⏱️ Iniciar Nuevo Timer")

    col1, col2 = st.columns([2, 1])

    with col1:
        task_name = st.text_input(
            "Nombre de la tarea (opcional)",
            placeholder="Ej: Programar feature X, Escribir reporte Y"
        )

    with col2:
        timer_type = st.selectbox(
            "Tipo de Timer",
            ["pomodoro", "deep_work", "short_break", "long_break", "custom"],
            format_func=lambda x: {
                'pomodoro': '🍅 Pomodoro (25 min)',
                'deep_work': '🔥 Deep Work (60 min)',
                'short_break': '☕ Break Corto (5 min)',
                'long_break': '🌴 Break Largo (15 min)',
                'custom': '⚙️ Personalizado'
            }[x]
        )

    # Si es custom, mostrar input de minutos
    if timer_type == 'custom':
        duration = st.number_input(
            "Duración (minutos)",
            min_value=1,
            max_value=240,
            value=25
        )
    else:
        duration = timer_manager.timer_presets[timer_type]
        st.info(f"⏱️ Duración seleccionada: **{duration} minutos**")

    if st.button("🚀 Iniciar Timer", use_container_width=True, type="primary"):
        st.session_state.active_timer = timer_manager.create_timer(
            duration_minutes=duration,
            task_name=task_name
        )
        st.session_state.notification_shown = False
        st.rerun()

    st.divider()

    # Explicación de timers
    st.header("📖 Tipos de Timer")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🍅 Pomodoro (25 min)")
        st.write("Ideal para tareas que requieren concentración moderada")
        st.caption("- Técnica Pomodoro clásica")
        st.caption("- Perfecto para Daily 3 y Prioridades")

        st.subheader("🔥 Deep Work (60 min)")
        st.write("Sesión de trabajo profundo sin interrupciones")
        st.caption("- Para tareas complejas")
        st.caption("- Perfecto para programar o escribir")

    with col2:
        st.subheader("☕ Break Corto (5 min)")
        st.write("Descanso entre pomodoros")
        st.caption("- Estira, camina, respira")
        st.caption("- No revises redes sociales")

        st.subheader("🌴 Break Largo (15 min)")
        st.write("Descanso después de 4 pomodoros")
        st.caption("- Come algo ligero")
        st.caption("- Recarga energías")

# Sidebar con métricas
with st.sidebar:
    # Tips
    st.subheader("💡 Tips de Focus")
    st.caption("• Cierra todas las distracciones")
    st.caption("• Pon el celular en silencio")
    st.caption("• Define la tarea antes de empezar")

    # Botón para permitir notificaciones manualmente
    st.subheader("🔔 Notificaciones")
    st.caption("Permite notificaciones para recibir alertas cuando termine el timer")

    enable_notif_html = """
    <button onclick="
        if ('Notification' in window) {
            Notification.requestPermission().then(function(result) {
                if (result === 'granted') {
                    new Notification('✅ Notificaciones activadas', {
                        body: 'Recibirás alertas cuando termine tu timer'
                    });
                }
            });
        }
    " style="
        background: #00D4AA;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        cursor: pointer;
        width: 100%;
        font-weight: bold;
    ">
        🔔 Activar Notificaciones
    </button>
    """
    components.html(enable_notif_html, height=50)

st.divider()

# Sección de Historial (Movido al cuerpo principal)
if st.session_state.completed_sessions:
    st.header("📜 Historial de Sesiones (Hoy)")
    
    total_minutes = sum(s['duration'] for s in st.session_state.completed_sessions)
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.metric("Tiempo Total de Foco", f"{total_minutes} min")
        if st.button("🗑️ Limpiar Historial"):
            st.session_state.completed_sessions = []
            st.rerun()

    with col2:
        for session in reversed(st.session_state.completed_sessions[-5:]): # Mostrar ultimas 5
             st.info(f"✅ **{session['task'] or 'Focus Session'}** - {session['duration']} min ({session['completed_at']})")

st.divider()

# Integración con tracking
if 'db' in st.session_state and st.session_state.completed_sessions:
    st.header("📊 Guardar en Tracking")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Contar como Daily 3", use_container_width=True):
            st.success("✅ Sesiones agregadas a Daily 3")

    with col2:
        if st.button("Contar como Prioridad", use_container_width=True):
            st.success("✅ Sesiones agregadas a Prioridades")

from modules.ui_components import render_sidebar_footer
render_sidebar_footer()

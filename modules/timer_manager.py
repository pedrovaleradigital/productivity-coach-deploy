"""
Gestor de Timers y Pomodoro
"""
from datetime import datetime, timedelta
from typing import Optional, Dict
import time


class TimerManager:
    """Gestor de timers para focus sessions"""

    def __init__(self):
        self.timer_presets = {
            'pomodoro': 25,      # 25 minutos
            'short_break': 5,    # 5 minutos
            'long_break': 15,    # 15 minutos
            'deep_work': 60,     # 60 minutos (1 hora)
            'custom': 0          # Custom time
        }

    def create_timer(self, duration_minutes: int, task_name: str = "") -> Dict:
        """Crear un nuevo timer"""
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)

        return {
            'task_name': task_name,
            'duration_minutes': duration_minutes,
            'start_time': start_time,
            'end_time': end_time,
            'status': 'running',
            'paused_at': None,
            'elapsed_seconds': 0
        }

    def get_remaining_time(self, timer: Dict) -> Dict:
        """Calcular tiempo restante del timer"""
        if timer['status'] == 'completed':
            return {
                'minutes': 0,
                'seconds': 0,
                'total_seconds': 0,
                'percentage': 100,
                'is_finished': True
            }

        if timer['status'] == 'paused':
            remaining_seconds = (timer['end_time'] - timer['paused_at']).total_seconds()
        else:
            now = datetime.now()
            remaining_seconds = (timer['end_time'] - now).total_seconds()

        # Si ya terminó
        if remaining_seconds <= 0:
            return {
                'minutes': 0,
                'seconds': 0,
                'total_seconds': 0,
                'percentage': 100,
                'is_finished': True
            }

        minutes = int(remaining_seconds // 60)
        seconds = int(remaining_seconds % 60)
        total_duration_seconds = timer['duration_minutes'] * 60
        percentage = ((total_duration_seconds - remaining_seconds) / total_duration_seconds) * 100

        return {
            'minutes': minutes,
            'seconds': seconds,
            'total_seconds': int(remaining_seconds),
            'percentage': round(percentage, 1),
            'is_finished': False
        }

    def pause_timer(self, timer: Dict) -> Dict:
        """Pausar timer"""
        if timer['status'] == 'running':
            timer['status'] = 'paused'
            timer['paused_at'] = datetime.now()
        return timer

    def resume_timer(self, timer: Dict) -> Dict:
        """Reanudar timer pausado"""
        if timer['status'] == 'paused' and timer['paused_at']:
            # Calcular cuánto tiempo estuvo pausado
            pause_duration = datetime.now() - timer['paused_at']
            # Extender el end_time por ese tiempo
            timer['end_time'] = timer['end_time'] + pause_duration
            timer['status'] = 'running'
            timer['paused_at'] = None
        return timer

    def complete_timer(self, timer: Dict) -> Dict:
        """Marcar timer como completado"""
        timer['status'] = 'completed'
        return timer

    def get_timer_display(self, timer: Dict) -> str:
        """Obtener string formateado para display"""
        remaining = self.get_remaining_time(timer)

        if remaining['is_finished']:
            return "⏰ ¡Tiempo completado!"

        return f"{remaining['minutes']:02d}:{remaining['seconds']:02d}"

    def get_focus_session_stats(self, session_duration_minutes: int) -> str:
        """Generar stats de sesión de focus"""
        if session_duration_minutes >= 60:
            return f"🔥 Deep Work: {session_duration_minutes} minutos completados"
        elif session_duration_minutes >= 25:
            return f"✅ Pomodoro: {session_duration_minutes} minutos completados"
        else:
            return f"✓ Focus: {session_duration_minutes} minutos completados"

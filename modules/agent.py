"""
Agente de Productividad con Anthropic Claude (sin LangChain legacy)
"""
from anthropic import Anthropic
from datetime import datetime
import pytz
from typing import Dict, Optional, List
import os


class ProductivityAgent:
    """Agente de productividad con sistema de identidad dual"""

    def __init__(self, api_key: str, db_client, timezone: str = "America/Caracas"):
        self.db = db_client  # Supabase client
        self.timezone = pytz.timezone(timezone)

        # Inicializar cliente de Anthropic directamente
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"

        # Historial de conversación en memoria
        self.conversation_history = []

        # Cargar historial previo
        self._rehydrate_memory()

        # Cargar prompt del sistema
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        """Cargar el prompt del sistema desde productivity-coach.md"""
        prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            '.agent',
            'workflows',
            'productivity-coach.md'
        )

        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            # Prompt de respaldo básico
            return """Eres un coach de productividad que ayuda a mantener consistencia en hábitos.
            Usa un tono directo, práctico y motivador. Ayuda al usuario a cumplir sus metas diarias."""

    def _rehydrate_memory(self):
        """Cargar historial previo en la memoria del agente"""
        try:
            recent_messages = self.db.get_recent_conversations(limit=5)

            if not recent_messages:
                return

            for msg in recent_messages:
                role = msg.get('role')
                content = msg.get('content')

                if role and content:
                    self.conversation_history.append({
                        "role": role,
                        "content": content
                    })

            print(f"Memoria rehidratada con {len(recent_messages)} mensajes previos.")

        except Exception as e:
            print(f"Error al rehidratar memoria: {e}")

    def _get_current_context(self) -> Dict:
        """Obtener contexto actual (hora, día, identidad activa)"""
        now = datetime.now(self.timezone)

        # Determinar identidad activa
        is_weekend = now.weekday() >= 5  # 5=Sábado, 6=Domingo
        is_morning = now.hour < 15  # Antes de 3 PM

        if is_weekend:
            identity = None  # Modo fin de semana
        elif is_morning:
            identity = "Empresario Exitoso"
        else:
            identity = "Profesional MarTech"

        # Obtener tracking del día
        tracking = self.db.get_today_tracking()

        # Obtener racha de código (LEGACY - Mantener por compatibilidad si es necesario o eliminar)
        code_streak = self.db.get_code_streak()

        # Obtener nuevos hábitos (Fase 3)
        habits = self.db.get_habits()

        return {
            'now': now,
            'time': now.strftime('%H:%M'),
            'day': now.strftime('%A'),
            'date': now.strftime('%Y-%m-%d'),
            'is_weekend': is_weekend,
            'identity': identity,
            'tracking': tracking,
            'code_streak': code_streak,
            'habits': habits
        }

    def _build_context_prompt(self, context: Dict) -> str:
        """Construir prompt de contexto para el agente"""
        tracking = context['tracking']

        prompt = f"""
CONTEXTO ACTUAL:
- Fecha: {context['date']}
- Día: {context['day']}
- Hora: {context['time']}
- Identidad activa: {context['identity'] if context['identity'] else 'Fin de semana - Sin protocolo estricto'}

TRACKING DE HOY:
- Daily 3 completadas: {tracking.get('identity_1_daily_3_completed', 0)}/3
- Prioridades tarde completadas: {tracking.get('identity_2_priorities_completed', 0)}/3
- Código hecho: {'Sí' if tracking.get('code_commit_done') else 'No'}
- Morning Mastery: {'Sí' if tracking.get('morning_mastery_done') else 'No'}

RACHA DE CÓDIGO: {context['code_streak']} días

---
"""
        return prompt

    def chat(self, user_message: str) -> str:
        """Procesar mensaje del usuario y generar respuesta"""
        # Obtener contexto actual
        context = self._get_current_context()

        # Construir prompt completo del sistema
        context_prompt = self._build_context_prompt(context)
        full_system = f"{self.system_prompt}\n\n{context_prompt}"

        # Agregar mensaje del usuario al historial
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Limitar historial a últimos 20 mensajes para no exceder tokens
        messages_to_send = self.conversation_history[-20:]

        try:
            # Llamar a Claude
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                system=full_system,
                messages=messages_to_send
            )

            assistant_message = response.content[0].text

            # Agregar respuesta al historial
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })

            # Guardar conversación en Supabase
            self.db.log_conversation(
                identity=context['identity'],
                messages=[
                    {'role': 'user', 'content': user_message},
                    {'role': 'assistant', 'content': assistant_message}
                ]
            )

            return assistant_message

        except Exception as e:
            return f"Error al generar respuesta: {e}"

    def get_morning_greeting(self) -> str:
        """Generar saludo de mañana automático"""
        context = self._get_current_context()

        if context['is_weekend']:
            prompt = "Saluda al usuario para un día de fin de semana. Recuérdale que puede descansar pero también puede hacer cosas que disfrute."
        else:
            prompt = f"""Genera el saludo de inicio de jornada.
            Es {context['day']} a las {context['time']}.
            Identidad activa: {context['identity']}.
            Recuerda al usuario su Mínimo No Negociable para hoy y pregunta cómo va a empezar."""

        return self.chat(prompt)

    def get_identity_switch_reminder(self) -> str:
        """Recordatorio de cambio de identidad (3 PM)"""
        context = self._get_current_context()

        if context['is_weekend']:
            return ""

        tracking = context['tracking']
        daily_3_done = tracking.get('identity_1_daily_3_completed', 0)

        prompt = f"""Es hora del cambio de identidad (3 PM).
        El usuario completó {daily_3_done}/3 tareas del Daily 3 en la mañana.
        Genera un mensaje de transición hacia la identidad de "Profesional MarTech" y pregunta cuáles son las 3 prioridades de la tarde."""

        return self.chat(prompt)

    def get_evening_summary(self) -> str:
        """Generar resumen de cierre de día"""
        context = self._get_current_context()
        tracking = context['tracking']

        prompt = f"""Genera un resumen de cierre de día.

        Resultados de hoy:
        - Daily 3: {tracking.get('identity_1_daily_3_completed', 0)}/3
        - Prioridades tarde: {tracking.get('identity_2_priorities_completed', 0)}/3
        - Código: {'Hecho' if tracking.get('code_commit_done') else 'Pendiente'}
        - Racha actual: {context['code_streak']} días

        Celebra lo logrado y motiva para mañana."""

        return self.chat(prompt)

    def mark_daily_3(self, tasks: List[str]):
        """Marcar Daily 3 como completadas"""
        completed = len([t for t in tasks if t.strip()])
        self.db.update_daily_3(completed, tasks)

    def mark_priorities(self, priorities: List[str]):
        """Marcar prioridades de tarde como completadas"""
        completed = len([p for p in priorities if p.strip()])
        self.db.update_priorities(completed, priorities)

    def mark_code_done(self, commit_time: Optional[str] = None):
        """Marcar código como completado"""
        self.db.mark_code_done(commit_time)

    def mark_morning_mastery_done(self):
        """Marcar Morning Mastery como completado"""
        self.db.mark_morning_mastery_done()

    # --- WRAPPERS GENÉRICOS DE HÁBITOS (Fase 3) ---
    def get_habits(self) -> List[Dict]:
        return self.db.get_habits()

    def create_habit(self, name: str):
        return self.db.create_habit(name)

    def update_habit(self, habit_id: str, name: str):
        return self.db.update_habit(habit_id, name)

    def delete_habit(self, habit_id: str):
        return self.db.delete_habit(habit_id)

    def mark_habit_done(self, habit_id: str):
        return self.db.mark_habit_done(habit_id)

    def get_morning_mastery_text(self) -> str:
        return self.db.get_morning_mastery_text()

    def update_morning_mastery_text(self, text: str):
        return self.db.update_morning_mastery_text(text)

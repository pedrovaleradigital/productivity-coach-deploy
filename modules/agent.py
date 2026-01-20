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
            os.path.dirname(os.path.dirname(__file__)), # Root del proyecto
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

        # Obtener tareas y feedback
        morning_tasks = tracking.get('identity_1_daily_3_details', [])
        afternoon_tasks = tracking.get('identity_2_priorities_details', [])
        morning_feedback = self.db.get_task_feedback("morning")
        afternoon_feedback = self.db.get_task_feedback("afternoon")

        # Construir sección de tareas con feedback
        morning_tasks_text = ""
        if morning_tasks:
            for i, task in enumerate(morning_tasks):
                task_text = task.get('text', '') if isinstance(task, dict) else ''
                if task_text:
                    fb = morning_feedback[i] if i < len(morning_feedback) else ''
                    done = '✅' if task.get('done', False) else '⬜'
                    morning_tasks_text += f"  {done} Tarea {i+1}: {task_text}\n"
                    if fb:
                        morning_tasks_text += f"     Feedback: {fb}\n"

        afternoon_tasks_text = ""
        if afternoon_tasks:
            for i, task in enumerate(afternoon_tasks):
                task_text = task.get('text', '') if isinstance(task, dict) else ''
                if task_text:
                    fb = afternoon_feedback[i] if i < len(afternoon_feedback) else ''
                    done = '✅' if task.get('done', False) else '⬜'
                    afternoon_tasks_text += f"  {done} Tarea {i+1}: {task_text}\n"
                    if fb:
                        afternoon_tasks_text += f"     Feedback: {fb}\n"

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

TAREAS DE MAÑANA (Identidad Empresario):
{morning_tasks_text if morning_tasks_text else '  Sin tareas definidas'}

TAREAS DE TARDE (Identidad Profesional):
{afternoon_tasks_text if afternoon_tasks_text else '  Sin tareas definidas'}

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

    def generate_task_feedback(self, tasks: List[Dict], period: str = "morning") -> List[str]:
        """
        Generar feedback personalizado para cada tarea.
        period: 'morning' o 'afternoon'
        Retorna lista de strings con feedback para cada tarea.
        """
        feedbacks = []

        for i, task in enumerate(tasks):
            task_text = task.get('text', '').strip()
            if not task_text:
                feedbacks.append("")
                continue

            # Construir prompt para analizar la tarea usando la misma filosofía del sistema
            analysis_prompt = f"""Analiza esta tarea según el concepto de "Mínimo No Negociable" (Rob Dial):

Tarea: "{task_text}"

## Concepto Clave:
El "Mínimo No Negociable" es la versión RIDÍCULAMENTE PEQUEÑA de una tarea, diseñada para eliminar la resistencia inicial. Debe cumplir estos criterios:
- Tomar máximo 2-5 minutos
- Estar 100% bajo tu control (no depender de terceros, horarios externos, etc.)
- Ser algo que puedas hacer AHORA MISMO sin preparación

## Ejemplos:
- ✅ "Abrir el documento y escribir el título" (ridículamente pequeña)
- ✅ "Hacer 1 llamada de prospección" (acción concreta bajo tu control)
- ❌ "Ir a cita médica" (compromiso externo, no está bajo tu control total)
- ❌ "Diseñar toda la oferta" (demasiado grande, genera resistencia)

## Tu Feedback:
1. Si la tarea ES ridículamente pequeña y bajo control del usuario: felicita brevemente.
2. Si la tarea es una acción concreta pero podría ser más pequeña: sugiere la versión mini.
3. Si la tarea es un compromiso externo (citas, reuniones, etc.): indica que es un "compromiso agendado", no un Mínimo No Negociable, y está bien tenerlo pero no confundirlo con el concepto.
4. Si la tarea es muy grande: sugiere dividirla y di cuál sería el primer micro-paso.

IMPORTANTE:
- Responde SOLO con el feedback, sin prefijos ni etiquetas
- Usa máximo 2 oraciones
- Incluye 1 emoji relevante
- Sé específico y honesto"""

            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=250,
                    system="Eres Productivity Coach, un coach de productividad directo y pragmático. Tu filosofía: Sistemas > Fuerza de Voluntad. Aplica el concepto de Mínimo No Negociable con precisión.",
                    messages=[{"role": "user", "content": analysis_prompt}]
                )
                feedback = response.content[0].text.strip()
                feedbacks.append(feedback)
            except Exception as e:
                feedbacks.append(f"No se pudo generar feedback: {e}")

        return feedbacks

    def save_task_feedback(self, feedbacks: List[str], period: str = "morning"):
        """Guardar feedback en Supabase"""
        return self.db.save_task_feedback(feedbacks, period)

    def get_task_feedback(self, period: str = "morning") -> List[str]:
        """Obtener feedback guardado"""
        return self.db.get_task_feedback(period)

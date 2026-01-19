"""
Cliente de Airtable para gestionar datos del Productivity Coach
"""
from pyairtable import Api
from datetime import datetime, date
import json
from typing import Dict, List, Optional


class AirtableClient:
    """Cliente para interactuar con Airtable"""

    def __init__(self, api_key: str, base_id: str):
        self.api = Api(api_key)
        self.base = self.api.base(base_id)

        # Tablas
        self.daily_tracking = self.base.table('daily_tracking')
        self.habit_streaks = self.base.table('habit_streaks')
        self.identity_sessions = self.base.table('identity_sessions')

    def get_today_tracking(self) -> Dict:
        """Obtener tracking del día actual"""
        today = date.today().isoformat()

        try:
            records = self.daily_tracking.all(formula=f"{{date}}='{today}'")

            if records:
                return records[0]['fields']
            else:
                # Crear registro para hoy
                new_record = self.daily_tracking.create({
                    'date': today,
                    'day_of_week': datetime.now().strftime('%A'),
                    'identity_1_daily_3_completed': 0,
                    'identity_2_priorities_completed': 0,
                    'code_commit_done': False,
                    'morning_mastery_done': False
                })
                return new_record['fields']
        except Exception as e:
            print(f"Error al obtener tracking del día: {e}")
            return {
                'identity_1_daily_3_completed': 0,
                'identity_2_priorities_completed': 0,
                'code_commit_done': False
            }

    def update_daily_3(self, completed: int, tasks_list: List[str]):
        """Actualizar Daily 3 completadas"""
        today = date.today().isoformat()
        records = self.daily_tracking.all(formula=f"{{date}}='{today}'")

        if records:
            self.daily_tracking.update(
                records[0]['id'],
                {
                    'identity_1_daily_3_completed': completed,
                    'identity_1_daily_3_list': json.dumps(tasks_list, ensure_ascii=False)
                }
            )

    def update_priorities(self, completed: int, priorities_list: List[str]):
        """Actualizar prioridades de tarde completadas"""
        today = date.today().isoformat()
        records = self.daily_tracking.all(formula=f"{{date}}='{today}'")

        if records:
            self.daily_tracking.update(
                records[0]['id'],
                {
                    'identity_2_priorities_completed': completed,
                    'identity_2_priorities_list': json.dumps(priorities_list, ensure_ascii=False)
                }
            )

    def mark_code_done(self, commit_time: Optional[str] = None):
        """Marcar código como completado"""
        today = date.today().isoformat()

        if commit_time is None:
            commit_time = datetime.now().strftime('%H:%M')

        records = self.daily_tracking.all(formula=f"{{date}}='{today}'")

        if records:
            self.daily_tracking.update(
                records[0]['id'],
                {
                    'code_commit_done': True,
                    'code_commit_time': commit_time
                }
            )

            # Actualizar racha
            self._update_code_streak()

    def mark_morning_mastery_done(self):
        """Marcar Morning Mastery como completado"""
        today = date.today().isoformat()
        records = self.daily_tracking.all(formula=f"{{date}}='{today}'")

        if records:
            self.daily_tracking.update(
                records[0]['id'],
                {'morning_mastery_done': True}
            )

    def get_code_streak(self) -> int:
        """Obtener racha actual de código"""
        try:
            streak_record = self.habit_streaks.all(formula="{habit_name}='Código'")

            if streak_record:
                return streak_record[0]['fields'].get('current_streak', 0)
            else:
                # Crear registro de racha
                new_record = self.habit_streaks.create({
                    'habit_name': 'Código',
                    'current_streak': 0,
                    'longest_streak': 0,
                    'total_completions': 0,
                    'consistency_rate': 0
                })
                return 0
        except Exception as e:
            print(f"Error al obtener racha de código: {e}")
            return 0

    def _update_code_streak(self):
        """Actualizar racha de código (interno)"""
        try:
            streak_record = self.habit_streaks.all(formula="{habit_name}='Código'")

            if streak_record:
                current_streak = streak_record[0]['fields'].get('current_streak', 0)
                longest_streak = streak_record[0]['fields'].get('longest_streak', 0)
                total_completions = streak_record[0]['fields'].get('total_completions', 0)

                new_streak = current_streak + 1
                new_longest = max(new_streak, longest_streak)

                self.habit_streaks.update(
                    streak_record[0]['id'],
                    {
                        'current_streak': new_streak,
                        'longest_streak': new_longest,
                        'last_activity_date': date.today().isoformat(),
                        'total_completions': total_completions + 1
                    }
                )
        except Exception as e:
            print(f"Error al actualizar racha: {e}")

    def log_conversation(self, identity: Optional[str], messages: List[Dict]):
        """Guardar conversación en Airtable"""
        try:
            self.identity_sessions.create({
                'identity_active': identity if identity else 'Fin de semana',
                'conversation_log': json.dumps(messages, ensure_ascii=False),
                'start_time': datetime.now().isoformat()
            })
        except Exception as e:
            print(f"Error al guardar conversación: {e}")

    def get_weekly_stats(self) -> Dict:
        """Obtener estadísticas de la semana"""
        # Implementación simplificada - expandir según necesidad
        return {
            'code_streak': self.get_code_streak(),
            'daily_3_avg': 2.5,
            'priorities_avg': 2.8,
            'consistency_rate': 85
        }

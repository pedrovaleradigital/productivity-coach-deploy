"""
Cliente de Supabase para gestionar datos del Productivity Coach
"""
from supabase import create_client, Client
from datetime import datetime, date, timedelta
import json
import pytz
from typing import Dict, List, Optional


class SupabaseClient:
    """Cliente para interactuar con Supabase"""

    def __init__(self, url: str, key: str, user_id: str, timezone: str = 'America/Caracas'):
        self.client: Client = create_client(url, key)
        self.user_id = user_id
        try:
            self.timezone = pytz.timezone(timezone)
        except:
            self.timezone = pytz.timezone('America/Caracas')

    def set_timezone(self, timezone: str):
        """Actualizar timezone del cliente"""
        try:
            self.timezone = pytz.timezone(timezone)
        except:
            pass # Mantener anterior si falla

    def _get_today_iso(self) -> str:
        """Obtener fecha actual en formato ISO respetando timezone"""
        return datetime.now(self.timezone).date().isoformat()


    def get_today_tracking(self) -> Dict:
        """Obtener tracking del día actual"""
        today = self._get_today_iso()


        try:
            # Buscar registro de hoy para este usuario
            response = self.client.table('daily_tracking').select('*')\
                .eq('date', today)\
                .eq('user_id', self.user_id)\
                .execute()

            if response.data and len(response.data) > 0:
                return response.data[0]
            else:
                # Crear registro para hoy
                new_record = {
                    'user_id': self.user_id,
                    'date': today,
                    'day_of_week': datetime.now().strftime('%A'),
                    'identity_1_daily_3_completed': 0,
                    'identity_2_priorities_completed': 0,
                    'code_commit_done': False,
                    'morning_mastery_done': False
                }

                response = self.client.table('daily_tracking').insert(new_record).execute()
                return response.data[0] if response.data else new_record

        except Exception as e:
            print(f"Error al obtener tracking del día: {e}")
            return {
                'identity_1_daily_3_completed': 0,
                'identity_2_priorities_completed': 0,
                'code_commit_done': False,
                'morning_mastery_done': False
            }

    def update_daily_3(self, tasks_data: List[Dict]):
        """
        Actualizar Daily 3 (Texto + Estado)
        tasks_data: Lista de dicts [{'text': str, 'done': bool}]
        """
        today = self._get_today_iso()
        
        # Calcular derivadas para mantener compatibilidad
        completed_count = sum(1 for t in tasks_data if t.get('done', False))
        text_list = [t.get('text', '') for t in tasks_data]

        try:
            # Asegurar que existe el registro
            self.get_today_tracking()

            # Actualizar columnas nuevas (JSON) y viejas (Legacy para dashboard)
            self.client.table('daily_tracking').update({
                'identity_1_daily_3_details': tasks_data,     # Nueva Logica
                'identity_1_daily_3_completed': completed_count, # Legacy Compat
                'identity_1_daily_3_list': text_list          # Legacy Compat
            }).eq('date', today).eq('user_id', self.user_id).execute()

        except Exception as e:
            print(f"Error al actualizar Daily 3: {e}")

    def update_priorities(self, priorities_data: List[Dict]):
        """
        Actualizar Prioridades (Texto + Estado)
        priorities_data: Lista de dicts [{'text': str, 'done': bool}]
        """
        today = self._get_today_iso()
        
        # Calcular derivadas
        completed_count = sum(1 for p in priorities_data if p.get('done', False))
        text_list = [p.get('text', '') for p in priorities_data]

        try:
            # Asegurar que existe el registro
            self.get_today_tracking()

            # Actualizar
            self.client.table('daily_tracking').update({
                'identity_2_priorities_details': priorities_data,       # Nueva Logica
                'identity_2_priorities_completed': completed_count,     # Legacy Compat
                'identity_2_priorities_list': text_list                 # Legacy Compat
            }).eq('date', today).eq('user_id', self.user_id).execute()

        except Exception as e:
            print(f"Error al actualizar prioridades: {e}")

    def mark_code_done(self, commit_time: Optional[str] = None):
        """Marcar código como completado"""
        today = self._get_today_iso()


        if commit_time is None:
            commit_time = datetime.now().strftime('%H:%M')

        try:
            # Asegurar que existe el registro
            self.get_today_tracking()

            # Actualizar
            self.client.table('daily_tracking').update({
                'code_commit_done': True,
                'code_commit_time': commit_time
            }).eq('date', today).eq('user_id', self.user_id).execute()

            # Actualizar racha
            self._update_code_streak()

        except Exception as e:
            print(f"Error al marcar código: {e}")

    def mark_morning_mastery_done(self):
        """Marcar Morning Mastery como completado"""
        today = self._get_today_iso()


        try:
            # Asegurar que existe el registro
            self.get_today_tracking()

            # Actualizar
            self.client.table('daily_tracking').update({
                'morning_mastery_done': True
            }).eq('date', today).eq('user_id', self.user_id).execute()

        except Exception as e:
            print(f"Error al marcar Morning Mastery: {e}")

    def get_code_streak(self) -> int:
        """Obtener racha actual de código"""
        try:
            response = self.client.table('habit_streaks').select('*')\
                .eq('habit_name', 'Código')\
                .eq('user_id', self.user_id)\
                .execute()

            if response.data and len(response.data) > 0:
                return response.data[0].get('current_streak', 0)
            else:
                # Crear registro de racha
                new_record = {
                    'user_id': self.user_id,
                    'habit_name': 'Código',
                    'current_streak': 0,
                    'longest_streak': 0,
                    'total_completions': 0,
                    'consistency_rate': 0.0
                }
                self.client.table('habit_streaks').insert(new_record).execute()
                return 0

        except Exception as e:
            print(f"Error al obtener racha de código: {e}")
            return 0

    def _update_code_streak(self):
        """Actualizar racha de código (interno)"""
        try:
            response = self.client.table('habit_streaks').select('*')\
                .eq('habit_name', 'Código')\
                .eq('user_id', self.user_id)\
                .execute()

            if response.data and len(response.data) > 0:
                streak_data = response.data[0]
                current_streak = streak_data.get('current_streak', 0)
                longest_streak = streak_data.get('longest_streak', 0)
                total_completions = streak_data.get('total_completions', 0)

                new_streak = current_streak + 1
                new_longest = max(new_streak, longest_streak)

                self.client.table('habit_streaks').update({
                    'current_streak': new_streak,
                    'longest_streak': new_longest,
                    'last_activity_date': self._get_today_iso(),
                    'total_completions': total_completions + 1

                }).eq('habit_name', 'Código').eq('user_id', self.user_id).execute()
            else:
                # Si no existe, crear registro inicial (Racha = 1 porque acabamos de cumplir)
                self.client.table('habit_streaks').insert({
                    'user_id': self.user_id,
                    'habit_name': 'Código',
                    'current_streak': 1,
                    'longest_streak': 1,
                    'last_activity_date': self._get_today_iso(),
                    'total_completions': 1,

                    'consistency_rate': 100.0
                }).execute()

        except Exception as e:
            print(f"Error al actualizar racha: {e}")

    def log_conversation(self, identity: Optional[str], messages: List[Dict]):
        """Guardar conversación en Supabase"""
        try:
            self.client.table('identity_sessions').insert({
                'user_id': self.user_id,
                'identity_active': identity if identity else 'Fin de semana',
                'conversation_log': messages,
                'start_time': datetime.now().isoformat()
            }).execute()

        except Exception as e:
            print(f"Error al guardar conversación: {e}")

    def log_focus_session(self, task_name: str, timer_type: str, duration_minutes: int):
        """Guardar sesión de focus timer"""
        try:
            self.client.table('focus_sessions').insert({
                'user_id': self.user_id,
                'task_name': task_name,
                'timer_type': timer_type,
                'duration_minutes': duration_minutes,
                'duration_minutes': duration_minutes,
                'completed_at': datetime.now(self.timezone).isoformat(),
                'date': self._get_today_iso()
            }).execute()


        except Exception as e:
            print(f"Error al guardar focus session: {e}")

    def get_focus_sessions_today(self) -> List[Dict]:
        """Obtener sesiones de focus del día"""
        today = self._get_today_iso()


        try:
            response = self.client.table('focus_sessions').select('*')\
                .eq('date', today)\
                .eq('user_id', self.user_id)\
                .order('completed_at', desc=True)\
                .execute()
            return response.data if response.data else []

        except Exception as e:
            print(f"Error al obtener focus sessions: {e}")
            return []

    def get_weekly_stats(self) -> Dict:
        """Obtener estadísticas de la semana"""
        # Nota: La función RPC podría no filtrar por usuario si no está configurada,
        # así que usaremos el cálculo manual por seguridad en esta versión
        return self._calculate_weekly_stats_manually()

    def _calculate_weekly_stats_manually(self) -> Dict:
        """Calcular stats semanales manualmente (fallback con filtro de usuario)"""
        try:
            # Obtener últimos 7 días
            today_date = datetime.now(self.timezone).date()
            start_date = (today_date - timedelta(days=6)).isoformat()


            response = self.client.table('daily_tracking').select('*')\
                .gte('date', start_date)\
                .eq('user_id', self.user_id)\
                .execute()

            if not response.data:
                return {
                    'total_daily_3': 0,
                    'total_priorities': 0,
                    'code_days': 0,
                    'morning_mastery_days': 0,
                    'avg_completion_rate': 0.0
                }

            data = response.data
            total_daily_3 = sum(d.get('identity_1_daily_3_completed', 0) for d in data)
            total_priorities = sum(d.get('identity_2_priorities_completed', 0) for d in data)
            code_days = sum(1 for d in data if d.get('code_commit_done'))
            morning_days = sum(1 for d in data if d.get('morning_mastery_done'))

            # Tasa basada en 3 tareas daily y 3 prioridades por día (6 total)
            avg_rate = ((total_daily_3 + total_priorities) / (len(data) * 6) * 100) if len(data) > 0 else 0

            return {
                'total_daily_3': total_daily_3,
                'total_priorities': total_priorities,
                'code_days': code_days,
                'morning_mastery_days': morning_days,
                'avg_completion_rate': round(avg_rate, 2)
            }

        except Exception as e:
            print(f"Error en cálculo manual: {e}")
            return {
                'total_daily_3': 0,
                'total_priorities': 0,
                'code_days': 0,
                'morning_mastery_days': 0,
                'avg_completion_rate': 0.0
            }

    def get_last_n_days_tracking(self, days: int = 7) -> List[Dict]:
        """Obtener tracking de los últimos N días"""
        try:
            today_date = datetime.now(self.timezone).date()
            start_date = (today_date - timedelta(days=days-1)).isoformat()


            response = self.client.table('daily_tracking').select('*')\
                .gte('date', start_date)\
                .eq('user_id', self.user_id)\
                .order('date', desc=False)\
                .execute()

            return response.data if response.data else []

        except Exception as e:
            print(f"Error al obtener tracking histórico: {e}")
            return []

    def get_recent_conversations(self, limit: int = 10) -> List[Dict]:
        """Obtener conversaciones recientes para rehidratar memoria"""
        try:
            # Traer las últimas N sesiones
            response = self.client.table('identity_sessions')\
                .select('conversation_log')\
                .eq('user_id', self.user_id)\
                .order('start_time', desc=True)\
                .limit(limit)\
                .execute()
            
            if not response.data:
                return []
                
            # Las sesiones vienen de la más reciente a la más antigua
            # Queremos rehidratar en orden cronológico (antigua -> reciente)
            sessions = reversed(response.data)
            
            all_messages = []
            for session in sessions:
                logs = session.get('conversation_log', [])
                if isinstance(logs, list):
                    all_messages.extend(logs)
                    
            return all_messages
            
        except Exception as e:
            print(f"Error al obtener conversaciones recientes: {e}")
            return []

    def get_user_settings(self) -> Dict:
        """Obtener configuración de identidades del usuario"""
        try:
            response = self.client.table('user_settings').select('*')\
                .eq('user_id', self.user_id)\
                .execute()
            
            default_settings = {
                'identity_1_name': 'Empresario Exitoso',
                'identity_2_name': 'Profesional MarTech'
            }

            if response.data and len(response.data) > 0:
                data = response.data[0]
                # Merge con defaults por si acaso faltan campos
                return {**default_settings, **{k: v for k, v in data.items() if v}}
            else:
                return default_settings
        except Exception as e:
            print(f"Error obteniendo user_settings: {e}")
            return {
                'identity_1_name': 'Empresario Exitoso',
                'identity_2_name': 'Profesional MarTech',
                'timezone': 'America/Caracas'
            }

    def update_user_settings(self, identity_1: str, identity_2: str, timezone: str = None):
        """Actualizar nombres de identidades y timezone"""
        try:
            # Prepare update data
            data = {
                'user_id': self.user_id,
                'identity_1_name': identity_1,
                'identity_2_name': identity_2,
                'updated_at': datetime.now().isoformat()
            }
            
            if timezone:
                data['timezone'] = timezone

            # Upsert (Insert or Update)
            self.client.table('user_settings').upsert(data).execute()
            return True, "Configuración guardada"
        except Exception as e:
            print(f"Error actualizando settings: {e}")
            return False, str(e)

    # --- MÉTODOS DE HÁBITOS GENÉRICOS (Fase 3) ---

    def create_habit(self, name: str) -> bool:
        """Crear un nuevo hábito"""
        try:
            # Validar límite de 3 hábitos
            current_habits = self.get_habits()
            if len(current_habits) >= 3:
                return False, "Límite de 3 hábitos alcanzado"

            self.client.table('habits').insert({
                'user_id': self.user_id,
                'name': name,
                'streak_count': 0,
                'active': True
            }).execute()
            return True, "Hábito creado"
        except Exception as e:
            print(f"Error creando hábito: {e}")
            return False, str(e)

    def get_habits(self) -> List[Dict]:
        """Obtener todos los hábitos activos del usuario"""
        try:
            response = self.client.table('habits').select('*')\
                .eq('user_id', self.user_id)\
                .eq('active', True)\
                .order('created_at', desc=False)\
                .execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error obteniendo hábitos: {e}")
            return []

    def update_habit(self, habit_id: str, name: str) -> bool:
        """Actualizar nombre de hábito (reinicia racha si cambia significado?? No, solo nombre aquí)"""
        try:
            # Nota: El usuario pidió que si cambia el hábito, se reinicie el contador.
            # En esta implementación asumiremos que cambiar el nombre ES cambiar el hábito.
            self.client.table('habits').update({
                'name': name,
                'streak_count': 0, # Reset forzado por cambio de contexto
                'last_completed_at': None 
            }).eq('id', habit_id).eq('user_id', self.user_id).execute()
            return True
        except Exception as e:
            print(f"Error actualizando hábito: {e}")
            return False

    def delete_habit(self, habit_id: str) -> bool:
        """Eliminar hábito (soft delete o hard delete)"""
        try:
            self.client.table('habits').delete().eq('id', habit_id).eq('user_id', self.user_id).execute()
            return True
        except Exception as e:
            print(f"Error eliminando hábito: {e}")
            return False

    def mark_habit_done(self, habit_id: str) -> Dict:
        """Marcar hábito como hecho hoy y actualizar racha"""
        try:
            habit_response = self.client.table('habits').select('*').eq('id', habit_id).single().execute()
            habit = habit_response.data
            
            if not habit:
                return {'success': False, 'message': 'Hábito no encontrado'}

            today = datetime.now(self.timezone).date()
            last_completed_str = habit.get('last_completed_at')
            
            if last_completed_str:
                # Truncar zona horaria si viene en formato Z simple o manejarlo mejor
                # Simplificación: Convertir la fecha string a fecha (ignorando hora exacta para calculo de dias)
                try:
                    last_date_dt = datetime.fromisoformat(last_completed_str.replace('Z', '+00:00'))
                    # Ajustar a zona horaria del usuario si fuera necesario, pero la fecha simple basta
                    last_date = last_date_dt.date()
                except:
                    last_date = datetime.fromisoformat(last_completed_str).date()

                delta_days = (today - last_date).days

                
                if delta_days == 0:
                    return {'success': True, 'message': 'Ya completado hoy', 'streak': habit['streak_count']}
                elif delta_days == 1:
                    new_streak = habit['streak_count'] + 1
                else:
                    new_streak = 1 # Rota la cadena (>1 día perdido)
            else:
                new_streak = 1 # Primer día

            # Actualizar hábito
            now_iso = datetime.now(self.timezone).isoformat()
            self.client.table('habits').update({

                'streak_count': new_streak,
                'last_completed_at': now_iso
            }).eq('id', habit_id).execute()

            # Loggear historial (opcional pero recomendado)
            self.client.table('habit_logs').insert({
                'habit_id': habit_id,
                'user_id': self.user_id,
                'completed_at': now_iso,
                'date_logged': self._get_today_iso()

            }).execute()

            return {'success': True, 'streak': new_streak, 'message': f'¡Racha: {new_streak} días!'}

            return {'success': True, 'streak': new_streak, 'message': f'¡Racha: {new_streak} días!'}

        except Exception as e:
            print(f"Error marcando hábito: {e}")
            return {'success': False, 'message': str(e)}

    def get_habit_logs_last_n_days(self, days: int = 7) -> List[Dict]:
        """Obtener logs de hábitos de los últimos N días para el heatmap"""
        try:
            today_date = datetime.now(self.timezone).date()
            start_date = (today_date - timedelta(days=days-1)).isoformat()
            
            # Ajuste de query, asegurando formato de fecha sin hora si es 'date_logged' es date
            # Ojo: date_logged se guarda con _get_today_iso() que es string YYYY-MM-DD
            response = self.client.table('habit_logs').select('*')\
                .gte('date_logged', start_date)\
                .eq('user_id', self.user_id)\
                .execute()
                
            return response.data if response.data else []
        except Exception as e:
            print(f"Error obteniendo logs de hábitos: {e}")
            return []

    # --- MORNING MASTERY SETTINGS ---

    def get_morning_mastery_text(self) -> str:
        """Obtener texto personalizado de Morning Mastery"""
        settings = self.get_user_settings()
        return settings.get('morning_mastery_text', '')

    def update_morning_mastery_text(self, text: str) -> bool:
        """Actualizar texto de Morning Mastery"""
        try:
            self.client.table('user_settings').upsert({
                'user_id': self.user_id,
                'morning_mastery_text': text,
                'updated_at': datetime.now().isoformat()
            }).execute()
            return True
        except Exception as e:
            print(f"Error actualizando Morning Mastery: {e}")
            return False

    # --- TASK FEEDBACK METHODS ---

    def save_task_feedback(self, feedbacks: List[str], period: str = "morning") -> bool:
        """Guardar feedback de tareas en daily_tracking"""
        today = self._get_today_iso()
        column_name = 'identity_1_feedback' if period == 'morning' else 'identity_2_feedback'

        try:
            self.get_today_tracking()  # Asegurar que existe el registro
            self.client.table('daily_tracking').update({
                column_name: feedbacks
            }).eq('date', today).eq('user_id', self.user_id).execute()
            return True
        except Exception as e:
            print(f"Error guardando feedback: {e}")
            return False

    def get_task_feedback(self, period: str = "morning") -> List[str]:
        """Obtener feedback guardado de tareas"""
        today = self._get_today_iso()
        column_name = 'identity_1_feedback' if period == 'morning' else 'identity_2_feedback'

        try:
            response = self.client.table('daily_tracking').select(column_name)\
                .eq('date', today)\
                .eq('user_id', self.user_id)\
                .execute()

            if response.data and len(response.data) > 0:
                feedback = response.data[0].get(column_name)
                return feedback if feedback else ["", "", ""]
            return ["", "", ""]
        except Exception as e:
            print(f"Error obteniendo feedback: {e}")
            return ["", "", ""]

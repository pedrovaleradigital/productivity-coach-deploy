"""
Constructor de Dashboard con visualizaciones de consistencia
"""
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta, date
import pandas as pd
from typing import Dict, List


class DashboardBuilder:
    """Constructor de gráficos para el dashboard de productividad"""

    def __init__(self, db_client):
        self.db = db_client  # Supabase client

    def get_last_7_days_data(self) -> pd.DataFrame:
        """Obtener datos de los últimos 7 días"""
        try:
            # Obtener registros de los últimos 7 días desde Supabase
            records = self.db.get_last_n_days_tracking(days=7)

            # Convertir a DataFrame
            data = []
            for record in records:
                data.append({
                    'date': record.get('date'),
                    'day': record.get('day_of_week', ''),
                    'daily_3': record.get('identity_1_daily_3_completed', 0),
                    'priorities': record.get('identity_2_priorities_completed', 0),
                    'code_done': 1 if record.get('code_commit_done', False) else 0,
                    'morning_mastery': 1 if record.get('morning_mastery_done', False) else 0
                })

            if not data:
                df = pd.DataFrame(columns=['date', 'day', 'daily_3', 'priorities', 'code_done', 'morning_mastery'])
            else:
                df = pd.DataFrame(data)

            # Asegurar que tenemos todos los 7 días (Timezone Aware)
            # Usar datetime.now(tz) para obtener la fecha correcta del usuario
            today_tz = datetime.now(self.db.timezone).date()
            start_date = today_tz - timedelta(days=6)
            
            all_dates = pd.date_range(start=start_date, end=today_tz, freq='D')
            df_complete = pd.DataFrame({'date': all_dates.strftime('%Y-%m-%d')})
            
            # Merge y fillna
            df_complete = df_complete.merge(df, on='date', how='left')
            
            # Rellenar valores nulos con 0 para métricas numéricas
            cols_to_fill = ['daily_3', 'priorities', 'code_done', 'morning_mastery']
            df_complete[cols_to_fill] = df_complete[cols_to_fill].fillna(0)
            
            return df_complete

        except Exception as e:
            print(f"Error al obtener datos: {e}")
            # Retornar DataFrame vacío
            return pd.DataFrame()

    def create_weekly_consistency_chart(self) -> go.Figure:
        """Crear gráfico de consistencia semanal"""
        df = self.get_last_7_days_data()

        if df.empty:
            # Gráfico vacío
            fig = go.Figure()
            fig.add_annotation(
                text="No hay datos disponibles",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig

        # Crear gráfico de barras agrupadas
        fig = go.Figure()

        # Daily 3
        fig.add_trace(go.Bar(
            name='Prioridades (AM)',
            x=df['date'],
            y=df['daily_3'],
            marker_color='#00D4AA',
            text=df['daily_3'],
            textposition='auto',
        ))

        # Prioridades
        fig.add_trace(go.Bar(
            name='Prioridades',
            x=df['date'],
            y=df['priorities'],
            marker_color='#FF6B6B',
            text=df['priorities'],
            textposition='auto',
        ))

        fig.update_layout(
            title='Consistencia Semanal',
            xaxis_title='Fecha',
            yaxis_title='Completadas',
            barmode='group',
            yaxis=dict(range=[0, 3]),
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )

        return fig

    def create_code_streak_gauge(self, current_streak: int, longest_streak: int) -> go.Figure:
        """Crear gauge de racha de código"""
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=current_streak,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Racha de Código 🔥", 'font': {'size': 24}},
            delta={'reference': longest_streak, 'increasing': {'color': "#00D4AA"}},
            gauge={
                'axis': {'range': [None, max(longest_streak + 5, 30)], 'tickwidth': 1, 'tickcolor': "darkgray"},
                'bar': {'color': "#00D4AA"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 7], 'color': '#FFE5E5'},
                    {'range': [7, 21], 'color': '#FFF5E5'},
                    {'range': [21, max(longest_streak + 5, 30)], 'color': '#E5FFE5'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': longest_streak
                }
            }
        ))

        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            height=300
        )

        return fig

    def create_habit_completion_heatmap(self) -> go.Figure:
        """Crear heatmap de completitud de hábitos"""
        df = self.get_last_7_days_data()

        if df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No hay datos disponibles",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig

        # Calcular porcentaje de completitud por día
        df['completion_rate'] = ((df['daily_3'] + df['priorities'] + df['code_done'] * 3 + df['morning_mastery']) / 10) * 100

        # Crear heatmap
        fig = go.Figure(data=go.Heatmap(
            z=[df['completion_rate'].values],
            x=df['date'],
            y=['Completitud'],
            colorscale=[
                [0, '#FF6B6B'],      # Rojo para baja completitud
                [0.5, '#FFD93D'],    # Amarillo para media
                [1, '#00D4AA']       # Verde para alta completitud
            ],
            text=[[f"{val:.0f}%" for val in df['completion_rate'].values]],
            texttemplate="%{text}",
            textfont={"size": 14},
            colorbar=dict(title="% Completado"),
            hovertemplate='%{x}<br>Completitud: %{z:.0f}%<extra></extra>'
        ))

        fig.update_layout(
            title='Mapa de Calor - Completitud Diaria',
            xaxis_title='Fecha',
            height=200,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )

        return fig

    def create_identity_balance_chart(self) -> go.Figure:
        """Crear gráfico de balance entre identidades"""
        df = self.get_last_7_days_data()

        if df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No hay datos disponibles",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig

        # Calcular totales
        total_daily_3 = df['daily_3'].sum()
        total_priorities = df['priorities'].sum()

        # Crear gráfico de dona
        fig = go.Figure(data=[go.Pie(
            labels=['Identidad #1: Empresario', 'Identidad #2: Profesional'],
            values=[total_daily_3, total_priorities],
            hole=.4,
            marker_colors=['#00D4AA', '#FF6B6B']
        )])

        fig.update_layout(
            title='Balance entre Identidades (Última Semana)',
            annotations=[dict(text='Balance', x=0.5, y=0.5, font_size=20, showarrow=False)],
            height=300,
            paper_bgcolor='rgba(0,0,0,0)',
        )

        return fig

    def get_weekly_summary_stats(self) -> Dict:
        """Obtener estadísticas resumidas de la semana"""
        df = self.get_last_7_days_data()

        if df.empty:
            return {
                'total_daily_3': 0,
                'total_priorities': 0,
                'code_days': 0,
                'morning_mastery_days': 0,
                'avg_completion_rate': 0
            }

        return {
            'total_daily_3': int(df['daily_3'].sum()),
            'total_priorities': int(df['priorities'].sum()),
            'code_days': int(df['code_done'].sum()),
            'morning_mastery_days': int(df['morning_mastery'].sum()),
            'avg_completion_rate': ((df['daily_3'].sum() + df['priorities'].sum()) / (len(df) * 6)) * 100
        }

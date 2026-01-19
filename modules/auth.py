"""
Módulo de Autenticación con Supabase
Utiliza el sistema de auth integrado de Supabase (no requiere tabla de usuarios adicional)
"""
import streamlit as st
from supabase import create_client, Client
from typing import Optional, Dict, Tuple
import os
import extra_streamlit_components as stx
import time
from datetime import datetime, timedelta
import json


class AuthManager:
    """Gestor de autenticación usando Supabase Auth"""

    def __init__(self, url: str, key: str):
        self.client: Client = create_client(url, key)
        self.cookie_manager = stx.CookieManager()

    def save_session(self, access_token: str, refresh_token: str):
        """Guardar sesión en una sola cookie JSON (dura 30 días)"""
        print(f"DEBUG: Saving combined session.") # DEBUG
        expires_at = datetime.now() + timedelta(days=30)
        
        # Guardar todo en un objeto JSON para evitar condiciones de carrera con múltiples cookies
        session_data = {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
        
        # Un solo 'set' para asegurar atomicidad
        self.cookie_manager.set(
            'productivity_session', 
            json.dumps(session_data), 
            expires_at=expires_at, 
            key="set_session"
        )
        # CRÍTICO: Esperar a que la cookie se escriba realmente
        time.sleep(1) 
    
    def clear_session(self):
        """Limpiar sesión de cookies"""
        try:
            self.cookie_manager.delete('productivity_session', key="del_session")
        except:
            pass 

    # ... (sign_up, sign_in, sign_out se mantienen igual, usando estos métodos internos) ...

    def restore_session_from_cookies(self) -> Optional[Dict]:
        """Intentar restaurar sesión desde cookie JSON"""
        try:
            cookies = self.cookie_manager.get_all()
            print(f"DEBUG: Cookies retrieved: {cookies.keys()}") # DEBUG - Solo mostrar keys por seguridad
            
            session_cookie = cookies.get('productivity_session')
            
            if session_cookie:
                try:
                    # Decodificar JSON
                    # A veces la cookie viene como urllib.parse.unquote si tiene caracteres especiales,
                    # pero json.loads suele manejarlo bien si es string standard.
                    import urllib.parse
                    
                    # Manejo robusto de decodificación
                    try:
                        data = json.load(session_cookie) if hasattr(session_cookie, 'read') else json.loads(session_cookie)
                    except:
                        # Fallback por si está URL encoded
                        data = json.loads(urllib.parse.unquote(session_cookie))
                        
                    access_token = data.get('access_token')
                    refresh_token = data.get('refresh_token')
                    
                    if access_token and refresh_token:
                        print("DEBUG: Tokens found in cookie, attempting restore...")
                        response = self.client.auth.set_session(access_token, refresh_token)
                        if response.user:
                            return {
                                "id": response.user.id,
                                "email": response.user.email,
                                "created_at": str(response.user.created_at) if response.user.created_at else None,
                                "last_sign_in": str(response.user.last_sign_in_at) if response.user.last_sign_in_at else None
                            }
                except Exception as e:
                    print(f"DEBUG: Error parsing session cookie: {e}")
                    
            return None
        except Exception as e:
            print(f"DEBUG: Error restoring session: {e}")
            return None

    def _is_whitelisted(self, email: str) -> bool:
        """Verificar si el email está en la whitelist (si está configurada)"""
        whitelist_env = os.getenv('WHITELISTED_EMAILS')
        if not whitelist_env:
            return True # Si no hay whitelist configurada, permitir todos
            
        allowed_emails = [e.strip().lower() for e in whitelist_env.split(',')]
        return email.strip().lower() in allowed_emails

    def sign_up(self, email: str, password: str) -> Tuple[bool, str]:
        """
        Registrar un nuevo usuario
        Returns: (success: bool, message: str)
        """
        if not self._is_whitelisted(email):
             return False, "⚠️ Acceso restringido: Este email no está en la lista de permitidos."

        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password
            })

            if response.user:
                return True, "Usuario registrado exitosamente. Revisa tu email para confirmar la cuenta."
            else:
                return False, "Error al registrar usuario"

        except Exception as e:
            error_msg = str(e)
            if "already registered" in error_msg.lower():
                return False, "Este email ya está registrado"
            elif "password" in error_msg.lower():
                return False, "La contraseña debe tener al menos 6 caracteres"
            elif "email" in error_msg.lower():
                return False, "Email inválido"
            return False, f"Error: {error_msg}"

    def sign_in(self, email: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Iniciar sesión
        Returns: (success: bool, message: str, user: Optional[Dict])
        """
        if not self._is_whitelisted(email):
             return False, "⚠️ Acceso restringido: Este email no está autorizado.", None

        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if response.user:
                user_data = {
                    "id": response.user.id,
                    "email": response.user.email,
                    "created_at": str(response.user.created_at) if response.user.created_at else None,
                    "last_sign_in": str(response.user.last_sign_in_at) if response.user.last_sign_in_at else None
                }
                
                # Guardar tokens en cookies
                if response.session:
                    self.save_session(response.session.access_token, response.session.refresh_token)
                
                return True, "Inicio de sesión exitoso", user_data
            else:
                return False, "Credenciales inválidas", None

        except Exception as e:
            error_msg = str(e)
            if "invalid" in error_msg.lower() or "credentials" in error_msg.lower():
                return False, "Email o contraseña incorrectos", None
            elif "email not confirmed" in error_msg.lower():
                return False, "Por favor confirma tu email antes de iniciar sesión", None
            return False, f"Error: {error_msg}", None

    def sign_out(self) -> Tuple[bool, str]:
        """
        Cerrar sesión
        Returns: (success: bool, message: str)
        """
        try:
            self.client.auth.sign_out()
            self.clear_session()
            return True, "Sesión cerrada exitosamente"
        except Exception as e:
            return False, f"Error al cerrar sesión: {str(e)}"

    def get_current_user(self) -> Optional[Dict]:
        """
        Obtener el usuario actual (si hay sesión activa)
        Returns: user dict or None
        """
        try:
            response = self.client.auth.get_user()
            if response and response.user:
                return {
                    "id": response.user.id,
                    "email": response.user.email,
                    "created_at": str(response.user.created_at) if response.user.created_at else None
                }
            return None
        except Exception:
            return None

    def reset_password(self, email: str) -> Tuple[bool, str]:
        """
        Enviar email de recuperación de contraseña
        Returns: (success: bool, message: str)
        """
        try:
            self.client.auth.reset_password_email(email)
            return True, "Se ha enviado un email con instrucciones para restablecer tu contraseña"
        except Exception as e:
            return False, f"Error: {str(e)}"




def init_auth() -> AuthManager:
    """Inicializar el AuthManager con las variables de entorno"""
    return AuthManager(
        url=os.getenv('SUPABASE_URL'),
        key=os.getenv('SUPABASE_KEY')
    )


def check_authentication() -> bool:
    """
    Verificar si el usuario está autenticado
    Usar en cada página para proteger el contenido
    Returns: True si está autenticado, False si no
    """
    # 1. Si ya está en memoria, todo bien
    if 'user' in st.session_state and st.session_state.user is not None:
        return True
    
    # 2. Si no, intentar restaurar desde cookies (si el auth manager existe)
    if 'auth' in st.session_state:
        # Importante: Esto puede causar un rerun si las cookies no están listas
        restored_user = st.session_state.auth.restore_session_from_cookies()
        if restored_user:
            st.session_state.user = restored_user
            st.rerun() # Recargar para aplicar el estado logueado
            return True
            
    return False


def require_authentication():
    """
    Requerir autenticación para acceder a una página
    Si no está autenticado, muestra un mensaje y detiene la ejecución
    """
    if not check_authentication():
        st.warning("⚠️ Debes iniciar sesión para acceder a esta página")
        st.info("👉 Ve a la página de **Login** en el menú lateral")

        # Mostrar botón para ir a login
        if st.button("🔐 Ir a Login", type="primary"):
            st.switch_page("pages/0_🔐_Login.py")

        st.stop()


def get_current_user_email() -> Optional[str]:
    """Obtener el email del usuario actual"""
    if check_authentication():
        return st.session_state.user.get('email')
    return None


def logout():
    """Cerrar sesión y limpiar estado"""
    if 'auth' in st.session_state:
        st.session_state.auth.sign_out()

    # Limpiar session state relacionado con auth
    keys_to_remove = ['user', 'auth']
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]

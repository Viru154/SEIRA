"""
Script para verificar el modelo User y los roles
"""
from utils.database import db_manager
from models.user import User

def check_users():
    with db_manager.session_scope() as session:
        users = session.query(User).all()
        
        print("📋 Usuarios en la base de datos:\n")
        for user in users:
            print(f"ID: {user.id}")
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"Rol: {user.rol} (tipo: {type(user.rol).__name__})")
            print(f"Activo: {user.activo}")
            print(f"Password hash: {user.password_hash[:20]}...")
            print("-" * 50)

if __name__ == '__main__':
    check_users()
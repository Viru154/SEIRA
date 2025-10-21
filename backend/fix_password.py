"""
Script para rehashear contraseñas de usuarios existentes
Ejecutar: python fix_passwords.py
"""
from werkzeug.security import generate_password_hash
from utils.database import db_manager
from models.user import User

def fix_passwords():
    """Rehashear todas las contraseñas"""
    
    # Contraseñas por defecto para cada usuario
    passwords = {
        'admin': 'Admin123',
        'analista1': 'Analista123',
        'operador1': 'Operador123',
        'cliente1': 'Cliente123'
    }
    
    print("🔧 Iniciando corrección de contraseñas...")
    
    with db_manager.session_scope() as session:
        usuarios = session.query(User).all()
        
        for usuario in usuarios:
            # Si existe una contraseña por defecto para este usuario
            if usuario.username in passwords:
                nueva_password = passwords[usuario.username]
                usuario.password_hash = generate_password_hash(nueva_password)
                print(f"✅ Contraseña actualizada para: {usuario.username}")
            else:
                # Para otros usuarios, usar una contraseña genérica
                usuario.password_hash = generate_password_hash('Password123')
                print(f"✅ Contraseña genérica asignada a: {usuario.username}")
        
        session.commit()
        print("\n🎉 ¡Todas las contraseñas han sido actualizadas!")
        print("\nCredenciales actualizadas:")
        print("- admin / Admin123")
        print("- analista1 / Analista123")
        print("- operador1 / Operador123")
        print("- cliente1 / Cliente123")

if __name__ == '__main__':
    try:
        fix_passwords()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
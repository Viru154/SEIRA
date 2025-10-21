"""
Script para convertir roles de Enum a String
"""
from utils.database import db_manager
from models.user import User, RolUsuario
from sqlalchemy import text

def convert_roles():
    print("🔧 Convirtiendo roles de Enum a String...\n")
    
    with db_manager.session_scope() as session:
        # Mapeo de Enum a String
        rol_map = {
            'RolUsuario.ADMIN': 'admin',
            'RolUsuario.ANALISTA': 'analista',
            'RolUsuario.OPERADOR': 'operador',
            'RolUsuario.CLIENTE': 'cliente'
        }
        
        users = session.query(User).all()
        
        for user in users:
            rol_actual = str(user.rol)
            
            if rol_actual in rol_map:
                nuevo_rol = rol_map[rol_actual]
                print(f"Usuario: {user.username}")
                print(f"  Rol actual: {rol_actual}")
                print(f"  Nuevo rol: {nuevo_rol}")
                
                # Actualizar directamente con SQL para evitar problemas con el Enum
                session.execute(
                    text("UPDATE users SET rol = :nuevo_rol WHERE id = :user_id"),
                    {"nuevo_rol": nuevo_rol, "user_id": user.id}
                )
                print("  ✅ Actualizado\n")
            else:
                print(f"⚠️  Usuario {user.username} tiene rol desconocido: {rol_actual}\n")
        
        session.commit()
        print("🎉 ¡Todos los roles convertidos exitosamente!")
        
        # Verificar cambios
        print("\n📋 Verificación:")
        session.expire_all()
        users = session.query(User).all()
        for user in users:
            print(f"  {user.username}: {user.rol}")

if __name__ == '__main__':
    try:
        convert_roles()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
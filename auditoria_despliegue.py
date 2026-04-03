"""
AUDITORÍA PRE-DESPLIEGUE - SICADFOC 2026
Verificación de archivos y configuración para despliegue a Render
"""
import os

def auditoria_despliegue():
    """Realizar auditoría completa de despliegue"""
    
    print("AUDITORIA PRE-DESPLIEGUE - SICADFOC 2026")
    print("=" * 60)
    
    # 1. Verificar archivos esenciales
    archivos_esenciales = ['requirements.txt', 'runtime.txt', 'Procfile', 'main.py']
    print("ARCHIVOS ESENCIALES:")
    
    archivos_ok = 0
    for archivo in archivos_esenciales:
        existe = os.path.exists(archivo)
        if existe:
            archivos_ok += 1
        print(f"  {'✅' if existe else '❌'} {archivo}")
    
    # 2. Verificar contenido de requirements.txt
    if os.path.exists('requirements.txt'):
        with open('requirements.txt', 'r') as f:
            paquetes = len([line for line in f if line.strip() and not line.startswith('#')])
            print(f"  📦 requirements.txt: {paquetes} paquetes")
    
    # 3. Verificar Procfile
    if os.path.exists('Procfile'):
        with open('Procfile', 'r') as f:
            contenido = f.read().strip()
            print(f"  🚀 Procfile: {contenido}")
    
    # 4. Verificar runtime.txt
    if os.path.exists('runtime.txt'):
        with open('runtime.txt', 'r') as f:
            contenido = f.read().strip()
            print(f"  🐍 runtime.txt: {contenido}")
    
    # 5. Verificar configuración de BD
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        print(f"  🔗 DATABASE_URL: Configurada")
        if 'render.com' in database_url:
            print("    ✅ URL de Render detectada")
        else:
            print("    ⚠️ URL no parece ser de Render")
    else:
        print(f"  🔗 DATABASE_URL: No configurada (local)")
    
    # 6. Verificar estructura de directorios
    dirs_esenciales = ['database', 'auth', 'modules', 'ui']
    print("  📁 ESTRUCTURA DE DIRECTORIOS:")
    
    dirs_ok = 0
    for directorio in dirs_esenciales:
        existe = os.path.exists(directorio)
        if existe:
            dirs_ok += 1
        print(f"    {'✅' if existe else '❌'} {directorio}/")
    
    # 7. Verificar archivos de configuración
    config_files = [
        'database/connection.py',
        'database/__init__.py',
        'auth/decorators.py',
        'modules/modulos_protegidos.py',
        'ui/ui_components.py'
    ]
    
    print("  📄 ARCHIVOS DE CONFIGURACIÓN:")
    config_ok = 0
    for archivo in config_files:
        existe = os.path.exists(archivo)
        if existe:
            config_ok += 1
        print(f"    {'✅' if existe else '❌'} {archivo}")
    
    # 8. Verificar archivos de producción
    prod_files = [
        'config/production_config.py',
        'static_config.py'
    ]
    
    print("  🌐 ARCHIVOS DE PRODUCCIÓN:")
    prod_ok = 0
    for archivo in prod_files:
        existe = os.path.exists(archivo)
        if existe:
            prod_ok += 1
        print(f"    {'✅' if existe else '❌'} {archivo}")
    
    # Resumen final
    print("\nRESUMEN DE AUDITORÍA:")
    print("=" * 30)
    
    total_checks = 4  # archivos, dirs, config, prod
    passed_checks = 0
    
    if archivos_ok == len(archivos_esenciales):
        passed_checks += 1
        print("✅ Archivos esenciales: Completos")
    else:
        print(f"❌ Archivos esenciales: {archivos_ok}/{len(archivos_esenciales)}")
    
    if dirs_ok == len(dirs_esenciales):
        passed_checks += 1
        print("✅ Directorios: Completos")
    else:
        print(f"❌ Directorios: {dirs_ok}/{len(dirs_esenciales)}")
    
    if config_ok == len(config_files):
        passed_checks += 1
        print("✅ Configuración: Completa")
    else:
        print(f"❌ Configuración: {config_ok}/{len(config_files)}")
    
    if prod_ok >= 1:  # Al menos uno de producción
        passed_checks += 1
        print("✅ Producción: Configurada")
    else:
        print("❌ Producción: No configurada")
    
    # Veredicto final
    print(f"\nVEREDICTO: {passed_checks}/{total_checks} chequeos pasados")
    
    if passed_checks == total_checks:
        print("🎉 SISTEMA LISTO PARA DESPLIEGUE A RENDER")
        return True
    else:
        print("⚠️ REVISE LOS ERRORES ANTES DEL DESPLIEGUE")
        return False

def mostrar_instrucciones_despliegue():
    """Mostrar instrucciones para despliegue"""
    
    print("\nINSTRUCCIONES DE DESPLIEGUE A RENDER:")
    print("=" * 50)
    
    print("1. 📤 SUBIR A GITHUB:")
    print("   git add .")
    print("   git commit -m 'Ready for Render deployment'")
    print("   git push origin main")
    
    print("\n2. 🚀 DESPLEGAR EN RENDER:")
    print("   - Ir a https://render.com")
    print("   - Conectar cuenta GitHub")
    print("   - Crear 'New Web Service'")
    print("   - Seleccionar repositorio")
    print("   - Configurar:")
    print("     * Runtime: Python 3")
    print("     * Build Command: pip install -r requirements.txt")
    print("     * Start Command: streamlit run main.py --server.port $PORT --server.address 0.0.0.0")
    
    print("\n3. 🔗 CONFIGURAR BASE DE DATOS:")
    print("   - Crear PostgreSQL en Render")
    print("   - Copiar DATABASE_URL")
    print("   - Agregar variable de entorno en Render")
    
    print("\n4. ✅ VERIFICAR DESPLIEGUE:")
    print("   - Esperar despliegue completo")
    print("   - Probar acceso con URL proporcionada")
    print("   - Verificar conexión a base de datos")

if __name__ == "__main__":
    listo = auditoria_despliegue()
    mostrar_instrucciones_despliegue()
    
    if listo:
        print(f"\n🎯 ACCESO INMEDIATO:")
        print(f"   📱 http://localhost:8523")
        print(f"   📧 angel_hernandez@hotmail.com")
        print(f"   🔑 14300385")
        print(f"   🎭 Rol: Administrador")

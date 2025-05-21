
# Script para empaquetar el Sistema Experto en un ejecutable independiente.
# Ejecuta este script para crear un archivo .exe con PyInstaller.


import os
import sys
import platform
import shutil
import PyInstaller.__main__
from datetime import datetime

# Archivo de registro para guardar información del proceso
log_file = f"build_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

def log(message):
    """Escribe mensaje tanto en consola como en el archivo de registro"""
    print(message)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"{message}\\n")

log(f"=== Inicio del proceso de empaquetado: {datetime.now()} ===")

# Determina el sistema operativo
sistema = platform.system()
log(f"Sistema operativo detectado: {sistema}")

# Nombre de la aplicación
app_name = "AsesorEstadistico"

# Ruta a SWI-Prolog según sistema operativo (ajusta según tu instalación)
swi_prolog_path = ""
if sistema == "Windows":
    swi_paths = [
        "C:\\\\Program Files\\\\swipl\\\\bin",
        "C:\\\\Program Files (x86)\\\\swipl\\\\bin",
        os.path.expanduser("~\\\\swipl\\\\bin")
    ]
    
    # Agrega la ruta de la variable de entorno PATH si existe
    if 'PATH' in os.environ:
        for p in os.environ['PATH'].split(os.pathsep):
            if 'swipl' in p.lower() and os.path.isdir(p):
                swi_paths.insert(0, p) # Añadir al principio para que tenga prioridad
    
    for path in swi_paths:
        if os.path.exists(path):
            swi_prolog_path = path
            log(f"SWI-Prolog binario encontrado en: {swi_prolog_path}")
            break
    
    if not swi_prolog_path:
        log("ADVERTENCIA: No se encontró la ruta binaria de SWI-Prolog automáticamente.")
        log("Por favor, verifica que SWI-Prolog esté instalado y en tu PATH,")
        log("o actualiza la variable 'swi_prolog_path' en este script 'build.py' manualmente.")
        # Opcional: Puedes descomentar y configurar una ruta manual aquí si sabes dónde está SWI-Prolog
        # swi_prolog_path = "C:\\Tu\\Ruta\\Manual\\A\\swipl\\bin"

elif sistema == "Linux" or sistema == "Darwin": # macOS
    # En Linux/macOS, SWI-Prolog generalmente está en el PATH del sistema
    # o instalado en /usr/local/bin, /usr/bin, etc.
    # PyInstaller debería encontrar las libs dinámicas si PySwip funciona normalmente.
    log("Asumiendo que SWI-Prolog está correctamente instalado y en el PATH para Linux/macOS.")

# Limpiar directorios de compilación anteriores
if os.path.exists("build"):
    shutil.rmtree("build")
    log("Directorio 'build' anterior eliminado.")
if os.path.exists("dist"):
    shutil.rmtree("dist")
    log("Directorio 'dist' anterior eliminado.")
if os.path.exists(f"{app_name}.spec"):
    os.remove(f"{app_name}.spec")
    log(f"Archivo '{app_name}.spec' anterior eliminado.")

# Argumentos de PyInstaller
pyinstaller_args = [
    'main.py',
    '--noconfirm',        # Sobrescribir sin pedir confirmación
    '--onefile',          # Crear un solo archivo ejecutable
    '--windowed',         # No mostrar la consola (para aplicaciones GUI)
    f'--name={app_name}', # Nombre del ejecutable
    f'--add-data=knowledge_base.pl{os.pathsep}.', # Añadir la base de conocimiento
]

# Añadir icono si existe
if os.path.exists("icon.ico"):
    pyinstaller_args.append(f'--icon=icon.ico')
    log("Icono 'icon.ico' añadido.")
else:
    log("Advertencia: No se encontró 'icon.ico'. El ejecutable no tendrá un icono personalizado.")


# Añadir las DLLs de SWI-Prolog si estamos en Windows y se encontró la ruta
if sistema == "Windows" and swi_prolog_path:
    # Intenta añadir las DLLs más comunes para PySwip
    # AÑADIMOS 'swipl.dll', 'pthreadVC2.dll', y 'libwinpthread-1.dll' explícitamente.
    dlls_to_add = [
        "libswipl.dll",
        "swipl.dll",          # Aseguramos que se intente añadir esta también
        "pthreadVC2.dll",     # DLL de hilos común en distribuciones de SWI-Prolog
        "libwinpthread-1.dll" # Otra DLL de hilos común
    ]
    
    # Verifica si cada DLL existe antes de intentar añadirla
    for dll_name in dlls_to_add:
        full_dll_path = os.path.join(swi_prolog_path, dll_name)
        if os.path.exists(full_dll_path):
            # Formato de PyInstaller: SRC;DST (SRC = path completo a la DLL, DST = . para el directorio raíz del ejecutable)
            pyinstaller_args.append(f'--add-binary={full_dll_path}{os.pathsep}.')
            log(f"Añadiendo DLL de SWI-Prolog: {full_dll_path}")
        else:
            log(f"ADVERTENCIA: La DLL '{dll_name}' no se encontró en '{swi_prolog_path}'.")
            log("Esto podría causar problemas de ejecución si es necesaria por PySwip.")
else:
    log("No se añadirán DLLs de SWI-Prolog (no es Windows o no se encontró la ruta).")


log("Ejecutando PyInstaller con los siguientes argumentos:")
log(str(pyinstaller_args))

try:
    PyInstaller.__main__.run(pyinstaller_args)
    log("PyInstaller completó la compilación exitosamente.")
except Exception as e:
    log(f"ERROR durante la compilación: {e}")
    sys.exit(1)

# Verificar si se creó el ejecutable
executable_path = os.path.join("dist", f"{app_name}{'.exe' if sistema == 'Windows' else ''}")
if os.path.exists(executable_path):
    log(f"¡Ejecutable creado exitosamente en: {executable_path}!")
    
    # Crear un archivo README básico para distribución
    readme_content = f"""
# {app_name}
 
Sistema Experto para la selección de pruebas estadísticas.
 
## Requisitos
- SWI-Prolog debe estar instalado en el sistema.
  Descárgalo desde: https://www.swi-prolog.org/download/stable
 
## Instrucciones
1. Asegúrate de tener SWI-Prolog instalado.
2. Ejecuta {app_name}.exe
3. Responde las preguntas para obtener recomendaciones de pruebas estadísticas
 
Creado con Python, Tkinter y PySwip.
"""
    
    with open(os.path.join("dist", "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)
    log("README.md creado en el directorio 'dist'.")
else:
    log(f"ERROR: No se pudo encontrar el ejecutable en {executable_path} después de la compilación.")
    sys.exit(1)

log(f"=== Proceso de empaquetado finalizado: {datetime.now()} ===")
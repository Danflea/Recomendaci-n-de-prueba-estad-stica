# Script modificado para empaquetar el Sistema Experto en un ejecutable independiente.
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
        f.write(f"{message}\n")

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
        "C:\\Program Files\\swipl\\bin",
        "C:\\Program Files (x86)\\swipl\\bin",
        os.path.expanduser("~\\swipl\\bin")
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

elif sistema == "Linux" or sistema == "Darwin": # macOS
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

# ---- MODIFICACIÓN EN EL MAIN.PY ----
# Crear una copia modificada de main.py que maneje mejor las rutas
with open("main.py", "r", encoding="utf-8") as f:
    main_content = f.read()

# Vamos a crear un temporal main_fixed.py que use normalizacion de rutas
main_fixed_content = """
# Esta es una versión modificada del archivo main.py que maneja mejor las rutas al cargar archivos
import os
import sys

# Código para normalizar rutas - añadido por el script de compilación
def get_path_to_resource(relative_path):
    """Obtiene la ruta absoluta a un recurso, funciona en desarrollo y cuando está empaquetado"""
    try:
        # PyInstaller crea un directorio temporal y guarda la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
        
    path = os.path.join(base_path, relative_path)
    # Convertir a ruta con barras diagonales normales (no barras invertidas)
    return path.replace("\\\\", "/")

""" + main_content

# Guardar la versión modificada de main.py
with open("main_fixed.py", "w", encoding="utf-8") as f:
    f.write(main_fixed_content)

log("Creado main_fixed.py con soporte mejorado para rutas")

# Ahora vamos a buscar y modificar la parte del código que carga knowledge_base.pl
with open("main_fixed.py", "r", encoding="utf-8") as f:
    fixed_content = f.read()

# Buscar y reemplazar instancias donde se carga knowledge_base.pl
# Nota: Esto es una aproximación y puede necesitar ajustes según tu código específico
if "knowledge_base.pl" in fixed_content:
    # Intentamos detectar diferentes patrones comunes de carga del archivo
    patterns_to_replace = [
        # Patrón 1: prolog.consult("knowledge_base.pl")
        'prolog.consult("knowledge_base.pl")', 
        'prolog.consult(\'knowledge_base.pl\')',
        # Patrón 2: prolog.consult(os.path.join(..., "knowledge_base.pl"))
        'prolog.consult(os.path.join(', 
        # Patrón 3: pyswip.Prolog().consult("knowledge_base.pl")
        '.consult("knowledge_base.pl")',
        '.consult(\'knowledge_base.pl\')'
    ]
    
    for pattern in patterns_to_replace:
        if pattern in fixed_content:
            if pattern == 'prolog.consult("knowledge_base.pl")':
                fixed_content = fixed_content.replace(
                    pattern, 
                    'prolog.consult(get_path_to_resource("knowledge_base.pl"))'
                )
            elif pattern == 'prolog.consult(\'knowledge_base.pl\')':
                fixed_content = fixed_content.replace(
                    pattern, 
                    'prolog.consult(get_path_to_resource("knowledge_base.pl"))'
                )
            elif pattern == '.consult("knowledge_base.pl")':
                fixed_content = fixed_content.replace(
                    pattern, 
                    '.consult(get_path_to_resource("knowledge_base.pl"))'
                )
            elif pattern == '.consult(\'knowledge_base.pl\')':
                fixed_content = fixed_content.replace(
                    pattern, 
                    '.consult(get_path_to_resource("knowledge_base.pl"))'
                )
            elif pattern == 'prolog.consult(os.path.join(':
                # Este es más complejo, necesitaríamos ver el código real
                log("ADVERTENCIA: Se detectó un patrón de carga con os.path.join. Revisa manualmente main_fixed.py")
                log("Busca líneas con 'prolog.consult(os.path.join(' y modifícalas para usar get_path_to_resource")
            
            log(f"Patrón de carga de knowledge_base.pl modificado: {pattern}")

    # Guardar los cambios
    with open("main_fixed.py", "w", encoding="utf-8") as f:
        f.write(fixed_content)
else:
    log("ADVERTENCIA: No se encontró 'knowledge_base.pl' en el código. Verifica manualmente main_fixed.py")

# Argumentos de PyInstaller, ahora usando main_fixed.py en lugar de main.py
pyinstaller_args = [
    'main_fixed.py',  # Usamos la versión modificada
    '--noconfirm',        # Sobrescribir sin pedir confirmación
    '--onefile',          # Crear un solo archivo ejecutable
    '--windowed',         # No mostrar la consola (para aplicaciones GUI)
    f'--name={app_name}', # Nombre del ejecutable
    '--add-data=knowledge_base.pl{};.'.format(os.pathsep),  # Añadir la base de conocimiento
    '--hidden-import=pyswip',  # Añadir importación oculta de pyswip
]

# Añadir icono si existe
if os.path.exists("icon.ico"):
    pyinstaller_args.append('--icon=icon.ico')
    log("Icono 'icon.ico' añadido.")
else:
    log("Advertencia: No se encontró 'icon.ico'. El ejecutable no tendrá un icono personalizado.")

# Añadir todas las DLLs necesarias del directorio bin de SWI-Prolog
if sistema == "Windows" and swi_prolog_path:
    # En lugar de intentar adivinar las DLLs específicas, vamos a añadir todas las DLLs
    # del directorio bin de SWI-Prolog
    dll_count = 0
    for file in os.listdir(swi_prolog_path):
        if file.lower().endswith('.dll'):
            full_dll_path = os.path.join(swi_prolog_path, file)
            pyinstaller_args.append('--add-binary={}{}.'
                                   .format(full_dll_path, os.pathsep))
            dll_count += 1
            log(f"Añadiendo DLL de SWI-Prolog: {full_dll_path}")
    
    log(f"Total de {dll_count} DLLs añadidas de {swi_prolog_path}")
    
    # También añadiremos el directorio de SWI-Prolog al PATH durante la ejecución
    # agregando código para hacer esto en el ejecutable final
    # Crear un archivo temporal con código de inicialización para configurar PATH
    hook_content = """
# Código hook de PyInstaller para configurar PATH para SWI-Prolog
import os
import sys

def _setup_swipl_path():
    # Obtener la ruta base del ejecutable
    try:
        base_path = sys._MEIPASS  # PyInstaller temp dir
    except Exception:
        base_path = os.path.abspath(".")
    
    # Añadir al PATH de Windows
    if os.name == 'nt':  # Windows
        os.environ['PATH'] = base_path + os.pathsep + os.environ.get('PATH', '')
        # Configurar variables de entorno para SWI-Prolog (opcional)
        os.environ['SWI_HOME_DIR'] = base_path

_setup_swipl_path()
"""
    
    with open("swipl_hook.py", "w", encoding="utf-8") as f:
        f.write(hook_content)
    
    # Añadir el hook a PyInstaller
    pyinstaller_args.append('--additional-hooks-dir=.')
    log("Hook de inicialización para PATH de SWI-Prolog añadido")
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
    
    # Eliminar archivos temporales creados durante el proceso
    if os.path.exists("main_fixed.py"):
        os.remove("main_fixed.py")
        log("Archivo temporal main_fixed.py eliminado")
    if os.path.exists("swipl_hook.py"):
        os.remove("swipl_hook.py")
        log("Archivo temporal swipl_hook.py eliminado")
else:
    log(f"ERROR: No se pudo encontrar el ejecutable en {executable_path} después de la compilación.")
    sys.exit(1)

log(f"=== Proceso de empaquetado finalizado: {datetime.now()} ===")
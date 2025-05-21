## Resumen del Proyecto: Sistema Experto para la Selección de Pruebas Estadísticas

Este proyecto implementa un sistema experto interactivo diseñado para guiar a los usuarios en la selección de la prueba estadística más adecuada para su análisis de datos. Utiliza una base de conocimiento en Prolog para la toma de decisiones y una interfaz gráfica de usuario (GUI) desarrollada con Tkinter en Python para la interacción.

### Objetivos Clave

El objetivo principal del sistema es simplificar el proceso de elección de pruebas estadísticas, especialmente para aquellos usuarios que no son expertos en estadística, proporcionando una recomendación basada en las características de sus datos y objetivos de investigación.

### Componentes Principales

El proyecto se divide en dos componentes fundamentales que trabajan en conjunto:

1.  **Base de Conocimiento (`knowledge_base.pl` - Desarrollada en Prolog):**
    * **Representación del Conocimiento:** Almacena las reglas y hechos que rigen la lógica de decisión para la selección de pruebas estadísticas. Cada prueba es un predicado que define las condiciones necesarias para su recomendación.
    * **Preguntas Dinámicas:** Define las preguntas que el sistema debe hacer al usuario, junto con sus posibles opciones de respuesta. Estas preguntas están estructuradas para capturar las características clave de los datos (objetivo, tipo de variable, número de grupos, normalidad, homogeneidad de varianzas, etc.).
    * **Explicaciones de Pruebas:** Contiene descripciones concisas de cada prueba estadística recomendada, ayudando al usuario a entender su propósito.
    * **Gestión de Respuestas:** Utiliza predicados dinámicos (`respuesta/2`) para almacenar las respuestas del usuario a medida que avanza en el cuestionario.
    * **Funcionalidad de Reinicio:** Incluye un predicado (`reiniciar/0`) que permite borrar todas las respuestas almacenadas, preparando el sistema para una nueva sesión.

2.  **Interfaz de Usuario (`main.py` - Desarrollada en Python con Tkinter y `pyswip`):**
    * **Conexión con Prolog:** Utiliza la librería `pyswip` para establecer una comunicación bidireccional con el motor de Prolog, permitiendo consultar la base de conocimiento y afirmar hechos (respuestas del usuario).
    * **Interacción Guiada:** Presenta las preguntas definidas en `knowledge_base.pl` de forma secuencial, mostrando las opciones de respuesta como botones de radio.
    * **Manejo de Respuestas:** Captura la selección del usuario y la afirma como un hecho en la base de conocimiento de Prolog, lo que permite que el motor de inferencia de Prolog determine la siguiente pregunta relevante o la prueba final.
    * **Asistencia Inteligente ("No lo sé"):**
        * Para preguntas críticas como la **normalidad de los datos** y la **homogeneidad de varianzas**, se ha añadido la opción **"No lo sé"**.
        * Cuando el usuario selecciona esta opción, el sistema no avanza a la siguiente pregunta, sino que proporciona una **guía práctica en R** con las funciones específicas (`shapiro.test()`, `car::leveneTest()`, `var.test()`) y la interpretación de sus p-valores para ayudar al usuario a determinar la característica de sus datos.
        * La misma pregunta se mantiene en pantalla, permitiendo al usuario volver a responder una vez haya realizado el análisis sugerido en R.
    * **Botón "Rehacer Pregunta Actual":**
        * Este botón se hace visible solo en las preguntas donde la opción "No lo sé" está disponible (normalidad y homogeneidad de varianzas).
        * Permite al usuario retractar su última respuesta para la pregunta actual y volver a seleccionarla, útil si se equivocó o si desea cambiar su decisión después de usar la guía de R.
    * **Botón "Reiniciar Tanda de Preguntas":**
        * Siempre visible, este botón permite al usuario borrar todas las respuestas previamente dadas.
        * Al hacer clic, el sistema invoca el predicado `reiniciar` en Prolog y vuelve a la primera pregunta del cuestionario, iniciando una nueva sesión desde cero.
    * **Visualización de Resultados:** Una vez que el sistema ha recopilado suficiente información para determinar una prueba, muestra la prueba estadística recomendada y una breve explicación de su uso en un área de texto dedicada.

### Cómo Funciona

1.  El usuario inicia la aplicación Python.
2.  La aplicación carga la base de conocimiento Prolog.
3.  El sistema presenta la primera pregunta no respondida definida en Prolog.
4.  El usuario selecciona una opción y hace clic en "Responder".
5.  La respuesta es enviada a Prolog y afirmada como un hecho.
6.  Prolog usa sus reglas para determinar la siguiente pregunta relevante o la prueba final.
7.  Si se selecciona "No lo sé", se muestra la guía en R y la pregunta se repite.
8.  Este ciclo continúa hasta que se puede inferir una prueba estadística.
9.  La prueba sugerida y su explicación son mostradas al usuario.
10. El usuario puede "Rehacer Pregunta Actual" o "Reiniciar Tanda de Preguntas" en cualquier momento.

Este sistema ofrece una herramienta práctica y fácil de usar para la selección de pruebas estadísticas, combinando el poder de la lógica de Prolog con una interfaz de usuario intuitiva.

Problemas y Soluciones Intentadas para la Generación del Ejecutable (Rama dev)
Esta sección detalla los desafíos encontrados y las aproximaciones de solución durante el proceso de empaquetado del sistema experto en un archivo ejecutable (.exe) utilizando PyInstaller. La rama main contiene una versión funcional que no está optimizada para ser empaquetada fácilmente, mientras que la rama dev busca lograr un ejecutable autónomo.

Objetivo: Crear un único archivo ejecutable (.exe) de la aplicación Python/Tkinter que integre PySwip y la base de conocimiento de Prolog, de modo que los usuarios puedan ejecutarla sin necesidad de instalar Python o PySwip directamente.

Desafíos Principales:

Errores de Ruta de Archivos (illegal \u or \U sequence y FileNotFoundError):

Problema: Al empaquetar una aplicación Python con PyInstaller, los archivos de soporte (como knowledge_base.pl) se colocan en un directorio temporal (_MEIPASS) durante la ejecución del .exe. El código original no sabía cómo acceder a estos archivos en ese entorno. Además, las rutas de archivo en Windows usan barras invertidas (\), que Python interpreta como secuencias de escape, causando errores si no se manejan correctamente.
Solución Intentada y Exitosa:
Implementación de la función resource_path() en main.py. Esta función detecta si la aplicación se ejecuta desde un entorno de PyInstaller (sys._MEIPASS) o desde el script original, y construye la ruta correcta al archivo.
Normalización de las rutas de archivo (.replace('\\', '/')) antes de pasarlas a PySwip, ya que SWI-Prolog y PySwip prefieren las barras diagonales (/) para las rutas, especialmente en la función prolog.consult().
Dependencias de SWI-Prolog (Errores de Carga del .exe):

Problema: PySwip es un binding (una interfaz) a la librería de SWI-Prolog. Para que la aplicación empaquetada funcione, no solo necesita PySwip en sí, sino también las librerías dinámicas (DLLs en Windows) de SWI-Prolog. PyInstaller no siempre las detecta automáticamente o no incluye todas las necesarias. Esto se manifestaba con ventanas de error genéricas de Windows al intentar abrir el .exe (ej., image_7b0110.png), sin un mensaje de error claro de Python.
Solución Intentada y en Progreso (Resolución Parcial/Total):
Asegurar la instalación de SWI-Prolog: La solución actual depende de que SWI-Prolog esté instalado en el sistema del usuario final y sea accesible a través de la variable de entorno PATH.
Configuración Explícita en build.py: Se ha modificado el script build.py para:
Mejorar la detección automática de la ruta de instalación de SWI-Prolog, incluyendo la búsqueda en el PATH del sistema.
Añadir explícitamente las DLLs críticas de SWI-Prolog (libswipl.dll, swipl.dll, pthreadVC2.dll, libwinpthread-1.dll) al empaquetado de PyInstaller usando la opción --add-binary. Esto garantiza que estas librerías esenciales estén presentes en el ejecutable.
Problemas Persistentes / Diagnóstico: La persistencia de errores a pesar de añadir DLLs puede indicar:
Falta de alguna DLL adicional específica para la versión de SWI-Prolog del desarrollador.
Incompatibilidad entre la versión de SWI-Prolog (32-bit vs. 64-bit) y la versión de Python/PySwip.
Problemas con la variable de entorno PATH o permisos en el sistema del usuario final.
Desincronización de la Base de Conocimiento (Lógica del Sistema Experto):

Problema: Durante las iteraciones, la lógica en main.py (cómo se formulan las preguntas, se manejan las respuestas) y la estructura de knowledge_base.pl (uso de IDs numéricos vs. IDs simbólicos, opciones de respuesta) se desincronizaron, causando que la aplicación no funcionara lógicamente incluso en modo de desarrollo.
Solución Implementada:
Refactorización de main.py para usar los IDs simbólicos de las preguntas (ej., objetivo, normalidad) tal como se definen en la última versión de knowledge_base.pl.
Implementación de una lista orden_preguntas en main.py para asegurar un flujo de preguntas lineal y predecible.
Modificación de main.py para consultar directamente las opciones de cada pregunta desde Prolog (pregunta_completa/3), eliminando la necesidad de diccionarios de opciones codificados rígidamente en Python.
Ajuste del manejo de la opción "no_se" para que sea consistente entre main.py y knowledge_base.pl.
Estado Actual en dev:

Con las últimas actualizaciones, la rama dev debería ser capaz de generar un ejecutable que:

Cargue knowledge_base.pl correctamente.
Presente las preguntas en el orden deseado.
Maneje las respuestas y derive la prueba sugerida.
Reinicie el sistema apropiadamente.
El principal punto de depuración restante es asegurar que PyInstaller empaquete todas las DLLs necesarias de SWI-Prolog para que el .exe funcione en cualquier máquina Windows que tenga SWI-Prolog instalado.

## Requisitos Previos

- Python 3.8 o superior
- SWI-Prolog (https://www.swi-prolog.org/)
- pyswip: Conector entre Python y Prolog

### Instalación de `pyswip`

```bash
pip install pyswip

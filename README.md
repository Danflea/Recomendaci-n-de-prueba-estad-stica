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

## Requisitos Previos

- Python 3.8 o superior
- SWI-Prolog (https://www.swi-prolog.org/)
- pyswip: Conector entre Python y Prolog

### Instalación de `pyswip`

```bash
pip install pyswip

# Interfaz gráfica con Tkinter para sistema experto

# main.py

import tkinter as tk
from tkinter import messagebox
from pyswip import Prolog
import os
import sys
import platform # Para el DPI Awarenes en Windows


# --- Función para manejar las rutas en modo desarrollo y en modo empaquetado ---
def resource_path(relative_path):
    """
    Obtiene la ruta absoluta del recurso, ya sea en modo de desarrollo o
    cuando el programa está empaquetado por PyInstaller.
    """
    try:
        # PyInstaller crea una carpeta temporal _MEIPASS para los recursos
        base_path = sys._MEIPASS
    except Exception:
        # En modo de desarrollo, la ruta base es el directorio actual del script
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- Clase del Sistema Experto GUI ---
class SistemaExpertoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Asesor de Prueba Estadística")

        # --- Ajustes de ventana ---
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        try:
            # Intenta cargar un icono si existe y estamos en Windows
            if platform.system() == "Windows" and os.path.exists(resource_path("icon.ico")):
                self.root.iconbitmap(resource_path("icon.ico"))
        except Exception as e:
            print(f"Advertencia: No se pudo cargar el icono: {e}")

        self.prolog = Prolog()
        try:
            # Usa resource_path para cargar knowledge_base.pl
            prolog_file_path = resource_path("knowledge_base.pl")
            if not os.path.exists(prolog_file_path):
                raise FileNotFoundError(f"El archivo knowledge_base.pl no se encontró en: {prolog_file_path}")
            
            # CRÍTICO: Reemplaza las barras invertidas por barras diagonales para PySwip/Prolog en Windows
            # Esto es lo que faltaba en tu última versión de main.py para la robustez.
            self.prolog.consult(prolog_file_path.replace('\\', '/')) 

        except Exception as e:
            messagebox.showerror("Error de Carga", f"No se pudo cargar knowledge_base.pl o conectar con SWI-Prolog: {e}\n"
                                                  "Asegúrate de que SWI-Prolog esté instalado y el archivo exista en el mismo directorio.")
            self.root.destroy()
            return

        # Definir el orden de las preguntas para el flujo del sistema experto
        self.orden_preguntas = [
            'objetivo', 'tipo_variable', 'numero_grupos', 'relacion_grupos', 
            'normalidad', 'varianzas_iguales', 'tipo_comparacion_proporcion', 
            'tipo_vd_categorica_prediccion'
        ]
        self.pregunta_actual_id = None # Para almacenar el ID simbólico de la pregunta actual

        self.label_pregunta = tk.Label(root, text="", wraplength=600, justify="left", font=("Arial", 12))
        self.label_pregunta.pack(pady=10, padx=20) # Añadimos padx

        self.opciones_var = tk.StringVar()
        self.frame_opciones = tk.Frame(root)
        self.frame_opciones.pack(pady=5, padx=20) # Añadimos padx

        self.boton_siguiente = tk.Button(root, text="Responder", command=self.enviar_respuesta)
        self.boton_siguiente.pack(pady=10)

        self.boton_rehacer = tk.Button(root, text="Rehacer Pregunta Actual", command=self.rehacer_pregunta_actual)
        self.boton_rehacer.pack_forget() # Inicialmente oculto

        self.resultado_texto = tk.Text(root, height=15, width=80, wrap="word", font=("Arial", 11))
        self.resultado_texto.pack(pady=10, padx=20) # Añadimos padx

        self.boton_reiniciar = tk.Button(root, text="Reiniciar Tanda de Preguntas", command=self.reiniciar)
        self.boton_reiniciar.pack(pady=5)

        self.obtener_siguiente_pregunta()

    def mostrar_pregunta(self, texto, opciones):
        self.label_pregunta.config(text=texto)
        
        for widget in self.frame_opciones.winfo_children():
            widget.destroy()

        self.opciones_var.set("") # Limpiar selección previa
        
        if not opciones:
            messagebox.showwarning("Advertencia", f"La pregunta '{texto}' no tiene opciones definidas. Revise knowledge_base.pl")
            return

        for opcion in opciones:
            opcion_display = str(opcion).replace('_', ' ').capitalize()
            rb = tk.Radiobutton(self.frame_opciones, text=opcion_display, variable=self.opciones_var, value=opcion, font=("Arial", 10))
            rb.pack(anchor="w", padx=5) # Añadimos padx para mejor espaciado
        
        # Lógica para mostrar/ocultar el botón "Rehacer Pregunta Actual"
        if self.pregunta_actual_id in ['normalidad', 'varianzas_iguales']: 
            self.boton_rehacer.pack(pady=5)
        else:
            self.boton_rehacer.pack_forget()

    def enviar_respuesta(self):
        respuesta_seleccionada = self.opciones_var.get()
        if not respuesta_seleccionada:
            messagebox.showwarning("Advertencia", "Por favor selecciona una opción antes de continuar.")
            return

        self.resultado_texto.delete(1.0, tk.END)

        # Manejo de la opción "no_se" (que es lo que usa tu knowledge_base.pl actual)
        if respuesta_seleccionada == "no_se":
            self.resultado_texto.insert(tk.END, "\n\nSugerencia para analizar tus datos en R:\n")
            if self.pregunta_actual_id == "normalidad":
                self.resultado_texto.insert(tk.END, (
                    "\"Shapiro-Wilk normality test\": `shapiro.test(variable)`\n\n"
                    "- Si el p-valor es mayor a alfa (0.05), la variable presenta un comportamiento normal.\n"
                    "- Si el p-valor es menor o igual a alfa (0.05), la variable NO presenta un comportamiento normal.\n"
                ))
            elif self.pregunta_actual_id == "varianzas_iguales":
                self.resultado_texto.insert(tk.END, (
                    "\"studentized Breusch-Pagan test\" (para regresión) o `var.test()` / `leveneTest()` (para comparar grupos):\n"
                    "`car::leveneTest(y ~ grupo, data = tu_dataframe)`\n"
                    "`var.test(variable_grupo1, variable_grupo2)`\n\n"
                    "- Si el p-valor es mayor a alfa (0.05), las muestras presentan varianzas iguales (Homocedasticidad).\n"
                    "- Si el p-valor es menor o igual a alfa (0.05), las muestras NO presentan varianzas iguales (Heterocedasticidad).\n"
                ))
            # Volver a mostrar la misma pregunta para que el usuario pueda rehacerla después de obtener la guía
            self.obtener_siguiente_pregunta(pregunta_especifica_id=self.pregunta_actual_id)
        else:
            # Afirmar la respuesta en Prolog usando el ID de la pregunta
            self.prolog.assertz(f"respuesta({self.pregunta_actual_id}, {respuesta_seleccionada})")
            self.obtener_siguiente_pregunta()

    def obtener_siguiente_pregunta(self, pregunta_especifica_id=None):
        self.resultado_texto.delete(1.0, tk.END) # Limpiar texto de resultado/guía

        if pregunta_especifica_id:
            # Si se pide una pregunta específica (ej. después de "no_se" o "rehacer")
            query_result = list(self.prolog.query(f"pregunta_completa({pregunta_especifica_id}, Texto, Opciones)"))
            if query_result:
                p_info = query_result[0]
                self.pregunta_actual_id = pregunta_especifica_id
                self.mostrar_pregunta(p_info['Texto'], p_info['Opciones'])
                return
            else:
                messagebox.showerror("Error de lógica", f"La pregunta '{pregunta_especifica_id}' no pudo ser encontrada en la base de conocimiento.")
                return

        # Si no se pide una pregunta específica, buscar la siguiente no respondida
        for pregunta_id_en_orden in self.orden_preguntas:
            # Verifica si esta pregunta ya tiene una respuesta afirmada en Prolog
            respuesta_existente = list(self.prolog.query(f"respuesta({pregunta_id_en_orden}, Respuesta)"))
            
            if not respuesta_existente:
                # Si no tiene respuesta, busca la información completa de la pregunta
                query_result = list(self.prolog.query(f"pregunta_completa({pregunta_id_en_orden}, Texto, Opciones)"))
                if query_result:
                    p_info = query_result[0]
                    self.pregunta_actual_id = pregunta_id_en_orden
                    self.mostrar_pregunta(p_info['Texto'], p_info['Opciones'])
                    return # Pregunta encontrada y mostrada
                else:
                    messagebox.showerror("Error", f"La pregunta '{pregunta_id_en_orden}' definida en el orden no se encontró en knowledge_base.pl.")
                    return # Detener si hay un error en el KB

        # Si todas las preguntas han sido respondidas o no se encontraron más preguntas
        self.mostrar_resultado()

    def rehacer_pregunta_actual(self):
        if self.pregunta_actual_id:
            # Retracta la respuesta actual de Prolog
            list(self.prolog.query(f"retractall(respuesta({self.pregunta_actual_id}, _))"))
            self.resultado_texto.delete(1.0, tk.END) # Limpiar el área de texto
            # Vuelve a mostrar la pregunta actual
            self.obtener_siguiente_pregunta(pregunta_especifica_id=self.pregunta_actual_id)
        else:
            messagebox.showinfo("Información", "No hay una pregunta actual para rehacer.")

    def mostrar_resultado(self):
        self.resultado_texto.delete(1.0, tk.END)
        resultados = list(self.prolog.query("seleccionar_prueba(Prueba)"))

        if resultados:
            prueba_sugerida = resultados[0]['Prueba']
            explicaciones = list(self.prolog.query(f"explicacion_prueba({prueba_sugerida}, Explicacion)"))

            texto_prueba = str(prueba_sugerida).replace('_', ' ').upper()
            self.resultado_texto.insert(tk.END, f"\n\nPrueba sugerida: {texto_prueba}\n")

            if explicaciones:
                self.resultado_texto.insert(tk.END, f"\n{explicaciones[0]['Explicacion']}\n")
            else:
                self.resultado_texto.insert(tk.END, "\nNo se encontró una explicación detallada para esta prueba.")
        else:
            # Si no se encontró ninguna prueba, intentar con la regla por defecto
            default_result = list(self.prolog.query("seleccionar_prueba(no_recomendada)"))
            if default_result:
                explicacion_default = list(self.prolog.query("explicacion_prueba(no_recomendada, Explicacion)"))
                if explicacion_default:
                    self.resultado_texto.insert(tk.END, f"\n\n{explicacion_default[0]['Explicacion']}\n")
                else:
                    self.resultado_texto.insert(tk.END, "\n\nNo se pudo determinar una prueba estadística con la información proporcionada.\n")
            else:
                self.resultado_texto.insert(tk.END, "\n\nNo se pudo determinar una prueba estadística con la información proporcionada.\n")
        
        # Ocultar el botón de rehacer una vez que se muestra el resultado final
        self.boton_rehacer.pack_forget()

    def reiniciar(self):
        # Limpiar la interfaz
        self.resultado_texto.delete(1.0, tk.END)
        self.opciones_var.set("")
        
        # Llama al predicado reiniciar en Prolog para borrar todas las respuestas
        list(self.prolog.query("reiniciar.")) 
        
        # Iniciar desde la primera pregunta en el orden definido
        self.pregunta_actual_id = None # Reset el id actual
        self.obtener_siguiente_pregunta(pregunta_especifica_id=self.orden_preguntas[0])
        
        # Asegurarse de que el botón de rehacer se oculte al reiniciar
        self.boton_rehacer.pack_forget()
        
        # Mensaje de confirmación
        messagebox.showinfo("Reinicio", "El sistema ha sido reiniciado exitosamente.")

if __name__ == "__main__":
    if platform.system() == "Windows":
        try:
            # Configurar la interfaz para verse mejor en alta DPI en Windows
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass  # Ignorar si no es Windows o hay otro problema

    root = tk.Tk()
    app = SistemaExpertoGUI(root)
    root.mainloop()
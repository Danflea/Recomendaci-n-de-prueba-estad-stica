
# Interfaz gráfica con Tkinter para sistema experto

# main.py

import tkinter as tk
from tkinter import messagebox
from pyswip import Prolog

class SistemaExpertoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Asesor de Prueba Estadística")

        self.prolog = Prolog()
        try:
            self.prolog.consult("knowledge_base.pl")
        except Exception as e:
            messagebox.showerror("Error de Carga", f"No se pudo cargar knowledge_base.pl: {e}\nAsegúrate de que SWI-Prolog esté instalado y el archivo exista en el mismo directorio.")
            self.root.destroy()
            return

        self.pregunta_actual_id = None # Para almacenar el ID de la pregunta actual

        self.label_pregunta = tk.Label(root, text="", wraplength=500, justify="left", font=("Arial", 12))
        self.label_pregunta.pack(pady=10)

        self.opciones_var = tk.StringVar()
        self.frame_opciones = tk.Frame(root)
        self.frame_opciones.pack()

        self.boton_siguiente = tk.Button(root, text="Responder", command=self.enviar_respuesta)
        self.boton_siguiente.pack(pady=10)

        # Botón para rehacer la pregunta actual
        self.boton_rehacer = tk.Button(root, text="Rehacer Pregunta Actual", command=self.rehacer_pregunta_actual)
        # Lo empaquetamos/desempaquetamos dinámicamente en mostrar_pregunta

        self.resultado_texto = tk.Text(root, height=15, width=80, wrap="word", font=("Arial", 11))
        self.resultado_texto.pack(pady=10)

        self.boton_reiniciar = tk.Button(root, text="Reiniciar Tanda de Preguntas", command=self.reiniciar)
        self.boton_reiniciar.pack(pady=5)

        # Iniciar el flujo de preguntas
        self.obtener_siguiente_pregunta()

    def mostrar_pregunta(self, texto, opciones):
        self.label_pregunta.config(text=texto)
        
        # Destruir botones de opción anteriores
        for widget in self.frame_opciones.winfo_children():
            widget.destroy()

        self.opciones_var.set("") # Limpiar la selección actual
        
        if not opciones:
            messagebox.showwarning("Advertencia", f"La pregunta '{texto}' no tiene opciones definidas. Revise knowledge_base.pl")
            return

        for opcion in opciones:
            opcion_display = str(opcion).replace('_', ' ').capitalize()
            rb = tk.Radiobutton(self.frame_opciones, text=opcion_display, variable=self.opciones_var, value=opcion)
            rb.pack(anchor="w")
        
        # Mostrar u ocultar el botón "Rehacer Pregunta Actual"
        # Solo mostrarlo si la pregunta actual es normalidad o varianzas_iguales
        if self.pregunta_actual_id in ['normalidad', 'varianzas_iguales']:
             # Si no está ya empaquetado, lo empaquetamos
             if self.boton_rehacer.winfo_ismapped() == 0: # Check if it's currently hidden
                self.boton_rehacer.pack(pady=5)
        else:
            # Si está empaquetado y no es una de las preguntas relevantes, lo desempaquetamos
            if self.boton_rehacer.winfo_ismapped() == 1:
                self.boton_rehacer.pack_forget()

    def enviar_respuesta(self):
        respuesta_seleccionada = self.opciones_var.get()
        if not respuesta_seleccionada:
            messagebox.showwarning("Advertencia", "Por favor selecciona una opción antes de continuar.")
            return

        self.resultado_texto.delete(1.0, tk.END) # Limpiar cualquier mensaje anterior en el área de texto

        if respuesta_seleccionada == "no_se":
             self.resultado_texto.insert(tk.END, "\n\n")
             if self.pregunta_actual_id == "normalidad":
                 self.resultado_texto.insert(tk.END, (
                     "Para saber si tu muestra es normal usa la siguiente función de R:\n"
                     "\"Shapiro-Wilk normality test\"\n"
                     "`shapiro.test(variable)`\n\n"
                     "- Si el p-valor es mayor a alfa (0.05), la variable presenta un comportamiento normal.\n"
                     "- Si el p-valor es menor o igual a alfa (0.05), la variable NO presenta un comportamiento normal.\n"
                 ))
             elif self.pregunta_actual_id == "varianzas_iguales":
                 self.resultado_texto.insert(tk.END, (
                     "Para saber si las muestras tienen varianzas homogéneas puedes usar la siguiente función de R:\n"
                     "\"studentized Breusch-Pagan test\" (para regresión) o `var.test()` / `leveneTest()` (para comparar grupos).\n"
                     "`car::leveneTest(y ~ grupo, data = tu_dataframe)`\n"
                     "`var.test(variable_grupo1, variable_grupo2)`\n\n"
                     "- Si el p-valor es mayor a alfa (0.05), las muestras presentan varianzas iguales (Homocedasticidad).\n"
                     "- Si el p-valor es menor o igual a alfa (0.05), las muestras NO presentan varianzas iguales (Heterocedasticidad).\n"
                 ))
             # Al seleccionar "no_se", simplemente volvemos a mostrar la misma pregunta para que el usuario pueda verificar
             self.obtener_siguiente_pregunta(pregunta_especifica=self.pregunta_actual_id)
        else:
            # Afirmar la respuesta en Prolog si no es "no_se"
            self.prolog.assertz(f"respuesta({self.pregunta_actual_id}, {respuesta_seleccionada})")
            self.obtener_siguiente_pregunta() # Avanzar a la siguiente pregunta

    # Modificamos obtener_siguiente_pregunta para que pueda recibir un ID específico
    def obtener_siguiente_pregunta(self, pregunta_especifica=None):
        if pregunta_especifica:
            # Si se pide una pregunta específica (ej. después de "no_se" o "rehacer")
            query_result = list(self.prolog.query(f"pregunta({pregunta_especifica}, Texto, Opciones)"))
            if query_result:
                p_info = query_result[0]
                self.pregunta_actual_id = p_info['Id']
                self.mostrar_pregunta(p_info['Texto'], p_info['Opciones'])
                return
            else:
                # Esto no debería pasar si el ID es válido en knowledge_base.pl
                messagebox.showerror("Error", f"Pregunta específica '{pregunta_especifica}' no encontrada.")
                return

        # Si no se pide una pregunta específica, buscamos la siguiente no respondida
        preguntas_definidas = list(self.prolog.query("pregunta(Id, Texto, Opciones)")) # Consulta correcta

        pregunta_encontrada = False
        for p_info in preguntas_definidas:
            pregunta_id = p_info['Id']
            respuesta_existente = list(self.prolog.query(f"respuesta({pregunta_id}, Respuesta)"))
            if not respuesta_existente:
                self.pregunta_actual_id = pregunta_id
                self.mostrar_pregunta(p_info['Texto'], p_info['Opciones'])
                pregunta_encontrada = True
                break

        if not pregunta_encontrada:
            self.mostrar_resultado()

    def rehacer_pregunta_actual(self):
        if self.pregunta_actual_id:
            # Retracta la respuesta actual de Prolog
            list(self.prolog.query(f"retractall(respuesta({self.pregunta_actual_id}, _))"))
            self.resultado_texto.delete(1.0, tk.END) # Limpiar el área de texto
            # Vuelve a mostrar la pregunta actual
            self.obtener_siguiente_pregunta(pregunta_especifica=self.pregunta_actual_id)
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
            self.resultado_texto.insert(tk.END, "\n\nNo se pudo determinar una prueba estadística con la información proporcionada.\n")
            self.resultado_texto.insert(tk.END, "Por favor, revise sus respuestas o la base de conocimiento.")
        
        # Ocultar el botón de rehacer una vez que se muestra el resultado final
        self.boton_rehacer.pack_forget()

    def reiniciar(self):
        self.resultado_texto.delete(1.0, tk.END)
        self.opciones_var.set("")
        # Llama al predicado reiniciar en Prolog para limpiar todos los hechos dinámicos `respuesta/2`
        self.prolog.query("reiniciar.")
        # Reinicia el flujo de preguntas desde el principio
        self.obtener_siguiente_pregunta()
        # Asegurarse de que el botón de rehacer se oculte al reiniciar
        self.boton_rehacer.pack_forget()

if __name__ == "__main__":
    root = tk.Tk()
    app = SistemaExpertoGUI(root)
    root.mainloop()
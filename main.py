
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

        # Botón para rehacer la pregunta actual (se hará visible solo cuando sea relevante)
        self.boton_rehacer = tk.Button(root, text="Rehacer Pregunta Actual", command=self.rehacer_pregunta_actual)
        # Inicialmente oculto
        # self.boton_rehacer.pack(pady=5) # Lo mostraremos/ocultaremos dinámicamente

        self.resultado_texto = tk.Text(root, height=15, width=80, wrap="word", font=("Arial", 11))
        self.resultado_texto.pack(pady=10)

        self.boton_reiniciar = tk.Button(root, text="Reiniciar Tanda de Preguntas", command=self.reiniciar) # Texto más claro
        self.boton_reiniciar.pack(pady=5)

        self.obtener_siguiente_pregunta()

    def mostrar_pregunta(self, texto, opciones):
        self.label_pregunta.config(text=texto)
        for widget in self.frame_opciones.winfo_children():
            widget.destroy()

        self.opciones_var.set("")
        if not opciones:
            messagebox.showwarning("Advertencia", f"La pregunta '{texto}' no tiene opciones definidas. Revise knowledge_base.pl")
            return

        for opcion in opciones:
            opcion_display = str(opcion).replace('_', ' ').capitalize()
            rb = tk.Radiobutton(self.frame_opciones, text=opcion_display, variable=self.opciones_var, value=opcion)
            rb.pack(anchor="w")
        
        # Mostrar u ocultar el botón "Rehacer Pregunta Actual"
        if self.pregunta_actual_id in ['normalidad', 'varianzas_iguales']:
             if self.boton_rehacer not in self.root.winfo_children(): # Evitar añadirlo si ya está
                self.boton_rehacer.pack(pady=5)
        else:
            self.boton_rehacer.pack_forget() # Ocultar si no es relevante

    def enviar_respuesta(self):
        respuesta_seleccionada = self.opciones_var.get()
        if not respuesta_seleccionada:
            messagebox.showwarning("Advertencia", "Por favor selecciona una opción antes de continuar.")
            return

        # Si el usuario selecciona "no_se", no se afirma la respuesta en Prolog,
        # solo se da la sugerencia y se vuelve a mostrar la misma pregunta.
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
                     "Para saber si las muestras tienen varianzas homogéneas puedes usar el siguiente función de R:\n"
                     "\"studentized Breusch-Pagan test\" (para regresión) o `var.test()` / `leveneTest()` (para comparar grupos)\n"
                     "`car::leveneTest(y ~ grupo, data = tu_dataframe)`\n"
                     "`var.test(variable_grupo1, variable_grupo2)`\n\n"
                     "- Si el p-valor es mayor a alfa (0.05), las muestras presentan varianzas iguales (Homocedasticidad).\n"
                     "- Si el p-valor es menor o igual a alfa (0.05), las muestras NO presentan varianzas iguales (Heterocedasticidad).\n"
                 ))
             # Volver a mostrar la misma pregunta para que el usuario pueda intentar de nuevo después de verificar
             self.obtener_siguiente_pregunta(pregunta_anterior_id=self.pregunta_actual_id)
        else:
            # Afirmar la respuesta en Prolog si no es "no_se"
            self.prolog.assertz(f"respuesta({self.pregunta_actual_id}, {respuesta_seleccionada})")
            self.obtener_siguiente_pregunta()

    def obtener_siguiente_pregunta(self, pregunta_anterior_id=None):
        self.resultado_texto.delete(1.0, tk.END) # Limpiar el texto al avanzar de pregunta

        # Si viene de "no_se", volver a mostrar la misma pregunta
        if pregunta_anterior_id:
            for p_info in list(self.prolog.query(f"pregunta({pregunta_anterior_id}, Texto, Opciones)")):
                self.pregunta_actual_id = p_info['Id']
                self.mostrar_pregunta(p_info['Texto'], p_info['Opciones'])
                return

        # Lógica original para obtener la siguiente pregunta no respondida
        preguntas_definidas = list(self.prolog.query("pregunta(Id, Texto, Opciones)"))

        pregunta_encontrada = False
        for p_info in preguntas_definidas:
            pregunta_id = p_info['Id']
            # Para las preguntas que tienen 'n_a' como opción y no son de comparar/predecir,
            # podríamos omitirlas si las condiciones anteriores ya definen la prueba.
            # Sin embargo, para seguir la tabla tal cual, preguntaremos todas.

            # Verifica si esta pregunta ya tiene una respuesta afirmada en Prolog
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
            # Retracta la respuesta actual de Prolog si existe
            list(self.prolog.query(f"retractall(respuesta({self.pregunta_actual_id}, _))"))
            self.resultado_texto.delete(1.0, tk.END) # Limpiar cualquier mensaje de R
            # Vuelve a mostrar la pregunta actual
            self.obtener_siguiente_pregunta(pregunta_anterior_id=self.pregunta_actual_id)
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
        self.prolog.query("reiniciar.") # Llama al predicado reiniciar en Prolog para limpiar los hechos dinámicos
        self.obtener_siguiente_pregunta() # Reinicia el flujo de preguntas
        self.boton_rehacer.pack_forget() # Ocultar el botón de rehacer al reiniciar

if __name__ == "__main__":
    root = tk.Tk()
    app = SistemaExpertoGUI(root)
    root.mainloop()
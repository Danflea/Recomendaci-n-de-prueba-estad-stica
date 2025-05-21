
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
        # Inicialmente no empaquetado, se gestionará en mostrar_pregunta()

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
        
        # Lógica para mostrar u ocultar el botón "Rehacer Pregunta Actual"
        if self.pregunta_actual_id in ['normalidad', 'varianzas_iguales']:
            # Asegurarse de que el botón se empaquete si no lo está
            self.boton_rehacer.pack(pady=5)
        else:
            # Asegurarse de que el botón se desempaquete si lo está
            self.boton_rehacer.pack_forget()

    def enviar_respuesta(self):
        respuesta_seleccionada = self.opciones_var.get()
        if not respuesta_seleccionada:
            messagebox.showwarning("Advertencia", "Por favor selecciona una opción antes de continuar.")
            return

        self.resultado_texto.delete(1.0, tk.END) # Limpiar cualquier mensaje anterior en el área de texto

        if respuesta_seleccionada == "no_se":
             self.resultado_texto.delete(1.0, tk.END)
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
             # Al seleccionar "no_se", volvemos a mostrar la misma pregunta para que el usuario pueda verificar
             # Usamos pregunta_especifica_id para forzar que se muestre la pregunta actual
             self.obtener_siguiente_pregunta(pregunta_especifica_id=self.pregunta_actual_id)
        else:
            # Afirmar la respuesta en Prolog si no es "no_se"
            self.prolog.assertz(f"respuesta({self.pregunta_actual_id}, {respuesta_seleccionada})")
            self.obtener_siguiente_pregunta() # Avanzar a la siguiente pregunta

    # Modificamos obtener_siguiente_pregunta para que pueda recibir un ID específico para volver a preguntar
    def obtener_siguiente_pregunta(self, pregunta_especifica_id=None):
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

        # Si no se pide una pregunta específica, buscamos la siguiente no respondida
        preguntas_definidas = list(self.prolog.query("pregunta_completa(Id, Texto, Opciones)"))

        pregunta_encontrada = False
        for p_info in preguntas_definidas:
            pregunta_id = p_info['Id']
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
            self.resultado_texto.insert(tk.END, "\n\nNo se pudo determinar una prueba estadística con la información proporcionada.\n")
            self.resultado_texto.insert(tk.END, "Por favor, revise sus respuestas o la base de conocimiento.")
        
        # Ocultar el botón de rehacer una vez que se muestra el resultado final
        self.boton_rehacer.pack_forget()

    def reiniciar(self):
        # Limpiar la interfaz
        self.resultado_texto.delete(1.0, tk.END)
        self.opciones_var.set("")
        
        # Eliminar todas las respuestas almacenadas en Prolog
        # Usamos retractall directamente en lugar de depender de un predicado reiniciar
        list(self.prolog.query("retractall(respuesta(_, _))"))
        
        # Buscar la primera pregunta definida en la base de conocimiento
        primera_pregunta = list(self.prolog.query("findall(Id, pregunta_completa(Id, _, _), Ids), Ids = [FirstId|_]"))
        
        if primera_pregunta and 'FirstId' in primera_pregunta[0]:
            primer_id = primera_pregunta[0]['FirstId']
            self.pregunta_actual_id = None  # Reset el id actual
            self.obtener_siguiente_pregunta(pregunta_especifica_id=primer_id)
        else:
            # Si no podemos obtener la primera pregunta con findall, intentamos obtener todas las preguntas
            # y tomamos la primera
            preguntas = list(self.prolog.query("pregunta_completa(Id, _, _)"))
            if preguntas:
                primer_id = preguntas[0]['Id']
                self.pregunta_actual_id = None  # Reset el id actual
                self.obtener_siguiente_pregunta(pregunta_especifica_id=primer_id)
            else:
                messagebox.showerror("Error", "No se encontraron preguntas en la base de conocimiento.")
        
        # Asegurarse de que el botón de rehacer se oculte al reiniciar
        self.boton_rehacer.pack_forget()
        
        # Mensaje de confirmación
        messagebox.showinfo("Reinicio", "El sistema ha sido reiniciado exitosamente.")

if __name__ == "__main__":
    root = tk.Tk()
    app = SistemaExpertoGUI(root)
    root.mainloop()
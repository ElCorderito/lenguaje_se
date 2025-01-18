# Link para señas de manos: https://es.hesperian.org/hhg/Disabled_Village_Children:Lenguaje_de_se%C3%B1as

import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
from traductor import TraductorFrame
from diccionario import DiccionarioFrame
from recursos import RecursosFrame
from utils import configure_styles

# Crear ventana con tema moderno usando ThemedTk
root = ThemedTk(theme="arc")
root.title("Lenguaje de Señas")

# Configurar estilos generales
configure_styles(root)

# Contenedor principal para los frames
container = tk.Frame(root)
container.pack(side="top", fill="both", expand=True)
container.configure(bg='#F5E8D0')

# Configurar el grid en el contenedor principal
container.grid_rowconfigure(0, weight=1)
container.grid_columnconfigure(0, weight=1)

# Diccionario para mantener referencias a los frames
frames = {}

def show_frame(frame_name):
    frame = frames[frame_name]
    frame.tkraise()

# Inicializar los frames y añadirlos al contenedor
for F in (TraductorFrame, DiccionarioFrame, RecursosFrame):
    frame_name = F.__name__
    frame = F(parent=container, controller=root, show_frame=show_frame)
    frames[frame_name] = frame
    frame.grid(row=0, column=0, sticky="nsew")

# Mostrar el frame inicial
show_frame("TraductorFrame")

# Crear el menú
menubar = tk.Menu(root)

# Menú principal
menu_principal = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Menú", menu=menu_principal)

# Añadir opciones al menú
menu_principal.add_command(label="Traductor", command=lambda: show_frame("TraductorFrame"))
menu_principal.add_command(label="Diccionario", command=lambda: show_frame("DiccionarioFrame"))
menu_principal.add_command(label="Recursos", command=lambda: show_frame("RecursosFrame"))
menu_principal.add_separator()
menu_principal.add_command(label="Salir", command=root.quit)

# Configurar el menú en la ventana
root.config(menu=menubar)

# Ejecutar la aplicación
root.mainloop()

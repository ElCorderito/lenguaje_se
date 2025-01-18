import tkinter as tk
from tkinter import ttk
from utils import AnimatedGIF, resize_image
from PIL import Image, ImageTk
import os
from collections import defaultdict

class DiccionarioFrame(tk.Frame):
    def __init__(self, parent, controller, show_frame):
        super().__init__(parent)
        self.controller = controller
        self.show_frame = show_frame
        self.configure(bg='#F5E8D0')

        # Título
        title_label = tk.Label(self, text="Diccionario de Señas", font=('Helvetica', 20, 'bold'),
                               bg='#F5E8D0', fg='#8B4513')
        title_label.pack(pady=20)

        # Frame para la búsqueda
        search_frame = tk.Frame(self, bg='#F5E8D0')
        search_frame.pack(pady=10)

        # Etiqueta y campo de entrada para la búsqueda
        search_label = ttk.Label(search_frame, text="Buscar:", background='#F5E8D0',
                                 font=('Helvetica', 14), foreground='#8B4513')
        search_label.pack(side=tk.LEFT, padx=5)

        self.search_entry = ttk.Entry(search_frame, width=30, font=('Helvetica', 14), style="TEntry")
        self.search_entry.pack(side=tk.LEFT, padx=5)

        # Botón de búsqueda
        search_button = ttk.Button(search_frame, text="Buscar", command=self.perform_search,
                                   style="TButton", padding=(5, 5))
        search_button.pack(side=tk.LEFT, padx=5)

        # Índice alfabético
        alphabet_frame = tk.Frame(self, bg='#F5E8D0')
        alphabet_frame.pack(pady=5)

        # Agregar el símbolo '#' al alfabeto
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ#'

        for letter in alphabet:
            letter_button = tk.Button(alphabet_frame, text=letter, font=('Helvetica', 12),
                                      bg='#D4B897', fg='#8B4513', relief='flat',
                                      command=lambda l=letter: self.scroll_to_letter(l))
            letter_button.pack(side='left', padx=2)

        # Frame para el canvas y scrollbar
        canvas_frame = tk.Frame(self, bg='#F5E8D0')
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas para el diccionario
        self.dict_canvas = tk.Canvas(canvas_frame, bg='#F5E8D0')
        self.dict_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar vertical para el canvas del diccionario
        dict_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.dict_canvas.yview)
        dict_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.dict_canvas.configure(yscrollcommand=dict_scrollbar.set)

        # Frame interno donde se colocarán las imágenes y etiquetas
        self.dict_frame = tk.Frame(self.dict_canvas, bg='#F5E8D0')
        self.dict_canvas.create_window((0, 0), window=self.dict_frame, anchor='nw')

        # Ajustar el tamaño del frame interno
        self.dict_frame.bind("<Configure>", self.update_scrollregion)

        # Inicializar el diccionario para las etiquetas de letras
        self.letter_labels = {}

        # Cargar y mostrar todas las imágenes
        self.load_dictionary()

        # Binding del evento de la rueda del ratón
        self.dict_canvas.bind("<MouseWheel>", self.on_mouse_wheel)  # Windows
        self.dict_canvas.bind("<Button-4>", self.on_mouse_wheel)    # Linux (scroll up)
        self.dict_canvas.bind("<Button-5>", self.on_mouse_wheel)    # Linux (scroll down)

    def on_mouse_wheel(self, event):
        # Desplazar el canvas verticalmente
        if event.num == 4:  # Scroll up en Linux
            self.dict_canvas.yview_scroll(-1, "units")
        elif event.num == 5:  # Scroll down en Linux
            self.dict_canvas.yview_scroll(1, "units")
        else:  # Windows y macOS
            self.dict_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def update_scrollregion(self, event):
        self.dict_canvas.configure(scrollregion=self.dict_canvas.bbox("all"))
   
    def load_dictionary(self, search_term=''):
        # Limpiar los widgets existentes
        for widget in self.dict_frame.winfo_children():
            widget.destroy()

        # Convertir el término de búsqueda a minúsculas para una búsqueda insensible a mayúsculas
        search_term = search_term.lower()

        # Definir tamaño máximo para las imágenes
        max_image_height = 90
        max_image_width = 90

        # Diccionario para almacenar las entradas organizadas
        items_dict = defaultdict(lambda: defaultdict(list))

        # Directorios donde se almacenan las imágenes y GIFs
        image_dirs = [('Letras', 'images'), ('Números', 'numbers'), ('Palabras', 'words'), ('Frases', 'phrases')]

        for category, dir_path in image_dirs:
            if os.path.exists(dir_path):
                for filename in os.listdir(dir_path):
                    if filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                        filepath = os.path.join(dir_path, filename)
                        name = os.path.splitext(filename)[0]
                        # Reemplazar guiones bajos por espacios y capitalizar
                        display_name = name.replace('_', ' ').title()

                        # Aplicar filtro de búsqueda
                        if search_term and search_term not in display_name.lower():
                            continue

                        # Determinar la clave de agrupación
                        if display_name[0].isalpha():
                            first_letter = display_name[0].upper()
                        else:
                            first_letter = '#'  # Agrupar bajo el símbolo '#'

                        items_dict[category][first_letter].append((display_name, filepath))

        # Verificar si no se encontraron resultados
        no_results = True

        # Mostrar las entradas organizadas
        self.letter_labels = {}  # Para navegación alfabética
        for category in sorted(items_dict.keys()):
            if items_dict[category]:
                no_results = False
                # Etiqueta de categoría
                category_label = tk.Label(self.dict_frame, text=category, font=('Helvetica', 16, 'bold'),
                                        bg='#F5E8D0', fg='#8B4513')
                category_label.pack(pady=(10, 5))

                for letter in sorted(items_dict[category].keys()):
                    # Etiqueta de letra o símbolo
                    letter_label = tk.Label(self.dict_frame, text=letter, font=('Helvetica', 14, 'bold'),
                                            bg='#F5E8D0', fg='#8B4513')
                    letter_label.pack(pady=(5, 5))
                    self.letter_labels[letter] = letter_label  # Guardar referencia para navegación

                    # Mostrar los ítems bajo cada letra
                    for display_name, filepath in sorted(items_dict[category][letter], key=lambda x: x[0]):
                        # Crear un frame para cada ítem
                        item_frame = tk.Frame(self.dict_frame, bg='#F5E8D0', padx=10, pady=5)
                        item_frame.pack(fill='x', padx=20, pady=2)

                        # Etiqueta con el nombre (display_name)
                        name_label = tk.Label(item_frame, text=display_name, font=('Helvetica', 12),
                                            bg='#F5E8D0', fg='#8B4513')
                        name_label.pack(side='left', padx=10)

                        # Mostrar la imagen o GIF
                        if filepath.endswith('.gif'):
                            image_label = AnimatedGIF(item_frame, filepath, bg='#F5E8D0')
                            image_label.pack(side='left', padx=10)
                        else:
                            try:
                                img = Image.open(filepath).convert('RGBA')
                                img = resize_image(img, max_image_width, max_image_height)
                                img_tk = ImageTk.PhotoImage(img)
                                image_label = tk.Label(item_frame, image=img_tk, bg='#F5E8D0')
                                image_label.image = img_tk  # Mantener referencia
                                image_label.pack(side='left', padx=10)
                            except IOError:
                                print(f"No se pudo abrir la imagen {filepath}")

        if no_results:
            no_results_label = tk.Label(self.dict_frame, text="No se encontraron resultados.", font=('Helvetica', 14),
                                        bg='#F5E8D0', fg='red')
            no_results_label.pack(pady=20)

        # Actualizar la región de scroll
        self.dict_frame.update_idletasks()
        self.dict_canvas.config(scrollregion=self.dict_canvas.bbox("all"))

    def perform_search(self):
        search_term = self.search_entry.get()
        self.load_dictionary(search_term=search_term)
    
    def scroll_to_letter(self, letter):
        if letter in self.letter_labels:
            target_widget = self.letter_labels[letter]
            self.dict_canvas.update_idletasks()
            # Obtener la posición Y del widget dentro del frame interno
            y = target_widget.winfo_y()
            # Obtener la altura total del contenido
            content_height = self.dict_frame.winfo_height()
            # Calcular la fracción para desplazarse
            fraction = y / content_height
            # Mover la vista del canvas
            self.dict_canvas.yview_moveto(fraction)

import tkinter as tk
from tkinter import ttk, messagebox
from utils import AnimatedGIF, resize_image
from PIL import Image, ImageTk
import os
import re

# Lista de símbolos que no se utilizan en el lenguaje de señas
symbols_not_used = [',', '.', '_', '-', '{', '}', '[', ']', '(', ')', '!','@','#','$','%','^','&','*','=','+',';','|','/','<','>','',':',';']

# Historial de palabras buscadas
search_history = []

# Clase para el frame del Traductor
class TraductorFrame(tk.Frame):
    def __init__(self, parent, controller, show_frame):
        super().__init__(parent)
        self.controller = controller
        self.show_frame = show_frame
        self.configure(bg='#F5E8D0')

        # Título
        title_label = tk.Label(self, text="Traductor de Señas", font=('Helvetica', 20, 'bold'),
                               bg='#F5E8D0', fg='#8B4513')
        title_label.grid(row=0, column=0, pady=10)

        # Definir fuente grande
        self.font_large = ('Helvetica', 12)

        # Configurar el grid en el frame
        self.grid_rowconfigure(0, weight=0)  # Fila del título
        self.grid_rowconfigure(1, weight=0)  # Fila del input_frame
        self.grid_rowconfigure(2, weight=1)  # Fila del content_frame
        self.grid_rowconfigure(3, weight=0)  # Fila del h_scrollbar
        self.grid_columnconfigure(0, weight=1)

        # Frame para la entrada y los botones
        input_frame = tk.Frame(self, bg='#F5E8D0')
        input_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

        # Ajustar el grid del input_frame
        input_frame.columnconfigure(0, weight=1)
        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(2, weight=1)

        # Campo de entrada
        entry_label = ttk.Label(input_frame, text="Escribe una palabra o frase:", background='#F5E8D0', font=('Helvetica', 16), foreground='#8B4513')
        entry_label.grid(row=0, column=0, columnspan=3, pady=5, sticky="w")
        self.entry = ttk.Entry(input_frame, width=100, font=('Helvetica', 16), style="TEntry")
        self.entry.grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

        # Frame para los botones de acción
        button_frame = tk.Frame(input_frame, bg='#F5E8D0')
        button_frame.grid(row=2, column=0, columnspan=3, pady=5)

        # Botón para procesar la entrada
        button = ttk.Button(button_frame, text="Mostrar", command=self.process_input, style="TButton", padding=(5, 5))
        button.pack(side=tk.LEFT, padx=5)

        # Botón para borrar el contenido del campo de entrada
        clear_button = ttk.Button(button_frame, text="Borrar", command=self.clear_entry, style="TButton", padding=(5, 5))
        clear_button.pack(side=tk.LEFT, padx=5)

        # Frame principal para el contenido
        content_frame = tk.Frame(self, bg='#F5E8D0')
        content_frame.grid(row=2, column=0, sticky="nsew")

        # Ajustar pesos de las columnas en content_frame
        content_frame.columnconfigure(0, weight=1)  # Historial
        content_frame.columnconfigure(1, weight=5)  # Imágenes
        content_frame.rowconfigure(0, weight=1)

        # Historial de búsquedas
        history_frame = tk.Frame(content_frame, bg='#F5E8D0')
        history_frame.grid(row=0, column=0, sticky='nsew')

        history_label = ttk.Label(history_frame, text="Historial de palabras (haz clic en una palabra para volver a verla):", background='#F5E8D0', font=('Helvetica', 16), foreground='#8B4513')
        history_label.pack(pady=5)

        # Text widget para el historial (ancho reducido)
        self.history_text = tk.Text(history_frame, width=20, wrap='word', state='disabled', font=self.font_large)
        self.history_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar para el historial
        history_scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_text.yview)
        history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        # Configurar el fondo del historial de palabras
        self.history_text.configure(bg='#F1D9B0', fg='#8B4513', yscrollcommand=history_scrollbar.set)
        self.history_text.bind_all("<MouseWheel>", self.on_mouse_wheel)

        # Frame para el canvas de imágenes y scrollbars
        canvas_frame = tk.Frame(content_frame)
        canvas_frame.grid(row=0, column=1, sticky='nsew')

        # Canvas para las imágenes
        self.image_canvas = tk.Canvas(canvas_frame, bg='#F5E8D0')
        self.image_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar vertical para el canvas de imágenes
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.image_canvas.yview, style="Vertical.TScrollbar")
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Scrollbar horizontal para el canvas de imágenes
        h_scrollbar = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.image_canvas.xview, style="Horizontal.TScrollbar")
        h_scrollbar.grid(row=3, column=0, sticky='ew')

        self.image_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        self.image_canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)

        # Frame interno donde se colocarán las imágenes
        self.inner_frame = tk.Frame(self.image_canvas, bg='#F5E8D0')
        self.inner_frame_window = self.image_canvas.create_window((0, 0), window=self.inner_frame, anchor='nw')

        # Ajustar el ancho del inner_frame al ancho del canvas
        self.inner_frame.bind('<Configure>', self.update_scrollregion)
        self.image_canvas.bind('<Configure>', self.resize_inner_frame)

    # Funciones internas del TraductorFrame
    def process_input(self):
        text = self.entry.get()
        
        # Separar el texto en "palabras" y verificar cada una
        words = text.split()
        for word in words:
            # Si una palabra contiene tanto letras como números sin separación
            if re.search(r'[A-Za-z]', word) and re.search(r'[0-9]', word):
                messagebox.showerror("Entrada no válida", "Por favor, separe letras y números con espacios.")
                return
        
        # Si pasa la validación, continúa con el procesamiento
        if text:
            self.show_images(text)
            self.update_history(text)

    def clear_entry(self):
        self.entry.delete(0, tk.END)

    def on_mouse_wheel(self, event):
        # Desplazar el canvas de imágenes
        self.image_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        # Desplazar el historial de búsqueda
        self.history_text.yview_scroll(int(-1*(event.delta/120)), "units")

    def resize_inner_frame(self, event):
        # Ajustar el ancho del inner_frame al ancho del canvas si es mayor
        canvas_width = event.width
        self.image_canvas.itemconfig(self.inner_frame_window, width=canvas_width)

    def update_scrollregion(self, event=None):
        # Actualizar el scrollregion del canvas
        self.image_canvas.configure(scrollregion=self.image_canvas.bbox("all"))

    def update_history(self, text):
        # Añadir la nueva búsqueda al historial
        search_history.append(text)
        index = len(search_history)  # Contador de búsqueda (el total de búsquedas realizadas)

        # Crear una etiqueta clicable para cada palabra en el historial
        self.history_text.configure(state='normal')
        self.history_text.insert('end', f"{index}. {text}\n")
        start_index = f"{index}.0"
        end_index = f"{index}.end"
        tag_name = f"item{index}"
        self.history_text.tag_add(tag_name, start_index, end_index)
        self.history_text.tag_bind(tag_name, "<Button-1>", lambda event, t=text: self.on_history_click(t))
        self.history_text.tag_bind(tag_name, "<Enter>", lambda event: self.history_text.tag_configure(tag_name, underline=True, foreground="#0000FF") or self.history_text.config(cursor="hand2"))
        self.history_text.tag_bind(tag_name, "<Leave>", lambda event: self.history_text.tag_configure(tag_name, underline=False, foreground="#8B4513") or self.history_text.config(cursor=""))
        self.history_text.tag_configure(tag_name, foreground="#8B4513")
        self.history_text.configure(state='disabled')

        # Guardar el historial en el archivo
        if os.path.exists("historial_palabras.txt"):
            with open("historial_palabras.txt", "r+", encoding='utf-8') as file:
                content = file.read()
                file.seek(0, 0)
                file.write(text + "\n" + content)  # Insertar al principio del archivo
        else:
            with open("historial_palabras.txt", "w", encoding='utf-8') as file:
                file.write(text + "\n")

    def on_history_click(self, text):
        # Colocar la palabra/frase en la barra de búsqueda
        self.entry.delete(0, tk.END)  # Borrar cualquier texto actual
        self.entry.insert(0, text)    # Insertar la palabra/frase del historial

        self.show_images(text)

    def add_image_to_word_images(self, number_str, word_images):
        for dir in ['words', 'numbers']:
            image_path_gif = f"{dir}/{number_str}.gif"
            image_path_png = f"{dir}/{number_str}.png"
            image_path_jpeg = f"{dir}/{number_str}.jpeg"

            if os.path.exists(image_path_gif):
                word_images.append((image_path_gif, 'gif'))
                return True
            elif os.path.exists(image_path_png):
                word_images.append((image_path_png, 'png'))
                return True
            elif os.path.exists(image_path_jpeg):
                word_images.append((image_path_jpeg, 'jpeg'))
                return True
        return False

    def process_two_digit_number(self, number_str, word_images):
        number = int(number_str)
        tens = (number // 10) * 10
        units = number % 10

        # Agregar imagen de las decenas
        tens_found = self.add_image_to_word_images(str(tens), word_images)

        # Agregar imagen de las unidades si no es cero
        if units != 0:
            units_found = self.add_image_to_word_images(str(units), word_images)
        else:
            units_found = True  # No es necesario agregar imagen para cero

        return tens_found and units_found

    def process_three_digit_number(self, number_str, word_images):
        number = int(number_str)
        hundreds = (number // 100) * 100
        remainder = number % 100

        # Agregar imagen de las centenas
        hundreds_found = self.add_image_to_word_images(str(hundreds), word_images)

        # Procesar las decenas y unidades restantes
        if remainder != 0:
            if remainder < 20:
                # Agregar imagen directamente si es menor que 20
                remainder_found = self.add_image_to_word_images(str(remainder), word_images)
            else:
                remainder_found = self.process_two_digit_number(str(remainder), word_images)
        else:
            remainder_found = True  # No es necesario agregar imagen para cero

        return hundreds_found and remainder_found

    def add_individual_digits(self, number_str, word_images):
        for digit in number_str:
            self.add_image_to_word_images(digit, word_images)


    def show_images(self, text):
        # Elimina cualquier imagen mostrada previamente
        for widget in self.inner_frame.winfo_children():
            widget.destroy()

        # Definir tamaño máximo para las imágenes
        max_image_height = 90  # Ajusta este valor según tus necesidades
        max_image_width = 90   # Ajusta este valor según tus necesidades

        # Dividir el texto en palabras
        words = text.split()
        i = 0
        while i < len(words):
            found_match = False
            # Intentar encontrar la frase más larga desde la posición actual
            for j in range(len(words), i, -1):
                phrase = ' '.join(words[i:j])
                phrase_with_underscores = phrase.replace(' ', '_')
                # Intentar encontrar la imagen de la frase
                image_dirs = ['phrases', 'words']
                found_image = False
                word_images = []

                for dir in image_dirs:
                    text_image_path_gif = f"{dir}/{phrase_with_underscores}.gif"
                    text_image_path_png = f"{dir}/{phrase_with_underscores}.png"
                    text_image_path_jpeg = f"{dir}/{phrase_with_underscores}.jpeg"

                    if os.path.exists(text_image_path_gif):
                        word_images.append((text_image_path_gif, 'gif'))
                        found_image = True
                        break
                    elif os.path.exists(text_image_path_png):
                        word_images.append((text_image_path_png, 'png'))
                        found_image = True
                        break
                    elif os.path.exists(text_image_path_jpeg):
                        word_images.append((text_image_path_jpeg, 'jpeg'))
                        found_image = True
                        break

                if found_image:
                    # Mostrar la imagen de la frase encontrada
                    word_frame = tk.Frame(self.inner_frame, bg='#F5E8D0', bd=2, relief='solid',
                                        padx=10, pady=10, highlightbackground='#A97C50')
                    word_frame.pack(fill='x', pady=10)

                    word_label = tk.Label(word_frame, text=phrase, bg='#F5E8D0',
                                        font=('Helvetica', 14, 'bold'), fg='#8B4513')
                    word_label.pack(pady=(0, 5))

                    images_frame = tk.Frame(word_frame, bg='#F5E8D0')
                    images_frame.pack(anchor='center')

                    for img_path, img_type in word_images:
                        if img_type == 'gif':
                            label = AnimatedGIF(images_frame, img_path, bg='#F5E8D0')
                            label.pack(side='left', padx=5, pady=5)
                        elif img_type in ['png', 'jpeg']:
                            img = Image.open(img_path).convert('RGBA')
                            img = resize_image(img, max_image_width, max_image_height)
                            img_tk = ImageTk.PhotoImage(img)
                            label = tk.Label(images_frame, image=img_tk, bg='#F5E8D0')
                            label.image = img_tk  # Evita que la imagen se elimine
                            label.pack(side='left', padx=5, pady=5)

                    # Actualizar el scroll
                    self.inner_frame.update_idletasks()
                    self.image_canvas.config(scrollregion=self.image_canvas.bbox("all"))
                    i = j  # Avanzar el índice a la posición después de la frase encontrada
                    found_match = True
                    break  # Salir del bucle interno ya que se encontró la frase

            if not found_match:
                # Procesar words[i] como palabra individual
                word = words[i]
                word_images = []
                # Lista de directorios donde buscar imágenes de palabras
                word_dirs = ['words', 'numbers']

                found_word_image = False
                for dir in word_dirs:
                    word_image_path_gif = f"{dir}/{word}.gif"
                    word_image_path_png = f"{dir}/{word}.png"
                    word_image_path_jpeg = f"{dir}/{word}.jpeg"

                    if os.path.exists(word_image_path_gif):
                        word_images.append((word_image_path_gif, 'gif'))
                        found_word_image = True
                        break
                    elif os.path.exists(word_image_path_png):
                        word_images.append((word_image_path_png, 'png'))
                        found_word_image = True
                        break
                    elif os.path.exists(word_image_path_jpeg):
                        word_images.append((word_image_path_jpeg, 'jpeg'))
                        found_word_image = True
                        break

                if not found_word_image:
                    word_images = []
                    # Verificar si la palabra es un número
                    if word.isdigit():
                        number = int(word)
                        if number > 999:
                            messagebox.showwarning("Número demasiado grande", "Por favor, ingrese un número menor o igual a 999.")
                            i += 1  # Avanzar al siguiente índice
                            continue  # Pasar a la siguiente palabra
                        elif 100 <= number <= 999:
                            # Procesar número de tres dígitos
                            number_found = self.process_three_digit_number(word, word_images)
                        elif 20 <= number < 100:
                            # Procesar número de dos dígitos
                            number_found = self.process_two_digit_number(word, word_images)
                        else:
                            # Procesar números menores de 20
                            number_found = self.add_image_to_word_images(word, word_images)
                        if not number_found:
                            # Si no se encontraron imágenes para el número, procesar dígitos individuales
                            self.add_individual_digits(word, word_images)
                    else:
                        # Si la palabra no es un número, procesar por letras
                        for letter in word:
                            if letter == " ":
                                continue
                            elif letter in symbols_not_used:
                                warning_message = f"El símbolo '{letter}' no se usa en el lenguaje de señas."
                                word_images.append((warning_message, 'warning'))
                                continue
                            elif letter == "?":
                                question_image_path_gif = "images/question_mark.gif"
                                question_image_path_png = "images/question_mark.png"
                                if os.path.exists(question_image_path_gif):
                                    word_images.append((question_image_path_gif, 'gif'))
                                elif os.path.exists(question_image_path_png):
                                    word_images.append((question_image_path_png, 'png'))
                            else:
                                letter_variants = [letter.lower(), letter.upper()]
                                letter_found = False
                                for l in letter_variants:
                                    letter_image_path_gif = f"images/{l}.gif"
                                    letter_image_path_png = f"images/{l}.png"
                                    letter_image_path_jpeg = f"images/{l}.jpeg"

                                    if os.path.exists(letter_image_path_gif):
                                        word_images.append((letter_image_path_gif, 'gif'))
                                        letter_found = True
                                        break
                                    elif os.path.exists(letter_image_path_png):
                                        word_images.append((letter_image_path_png, 'png'))
                                        letter_found = True
                                        break
                                    elif os.path.exists(letter_image_path_jpeg):
                                        word_images.append((letter_image_path_jpeg, 'jpeg'))
                                        letter_found = True
                                        break

                                if not letter_found:
                                    continue


                # Mostrar imágenes de la palabra o letras
                word_frame = tk.Frame(self.inner_frame, bg='#F5E8D0', bd=2, relief='solid',
                                    padx=10, pady=10, highlightbackground='#A97C50')
                word_frame.pack(fill='x', pady=10)

                word_label = tk.Label(word_frame, text=word, bg='#F5E8D0',
                                    font=('Helvetica', 14, 'bold'), fg='#8B4513')
                word_label.pack(pady=(0, 5))

                images_frame = tk.Frame(word_frame, bg='#F5E8D0')
                images_frame.pack(anchor='center')

                for img_path, img_type in word_images:
                    if img_type == 'gif':
                        label = AnimatedGIF(images_frame, img_path, bg='#F5E8D0')
                        label.pack(side='left', padx=5, pady=5)
                    elif img_type in ['png', 'jpeg']:
                        img = Image.open(img_path).convert('RGBA')
                        img = resize_image(img, max_image_width, max_image_height)
                        img_tk = ImageTk.PhotoImage(img)
                        label = tk.Label(images_frame, image=img_tk, bg='#F5E8D0')
                        label.image = img_tk
                        label.pack(side='left', padx=5, pady=5)
                    elif img_type == 'warning':
                        warning_label = tk.Label(images_frame, text=img_path, fg='red', bg='#F5E8D0',
                                                font=('Helvetica', 12, 'bold'))
                        warning_label.pack(side='left', padx=5, pady=5)

                # Actualizar el scroll
                self.inner_frame.update_idletasks()
                self.image_canvas.config(scrollregion=self.image_canvas.bbox("all"))
                i += 1  # Avanzar al siguiente índice

        # Actualizar el scroll final
        self.inner_frame.update_idletasks()
        self.image_canvas.config(scrollregion=self.image_canvas.bbox("all"))
        
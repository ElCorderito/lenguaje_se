import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageSequence

# Clase para manejar GIFs animados
class AnimatedGIF(tk.Label):
    def __init__(self, master, path, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.sequence = []
        self.delay = 100  # Tiempo entre cuadros en milisegundos

        # Cargar el GIF y obtener los cuadros
        self.load_frames(path)

        self.idx = 0
        if len(self.sequence) > 1:
            self.after(self.delay, self.next_frame)

    def load_frames(self, path):
        img = Image.open(path)
        try:
            for frame in ImageSequence.Iterator(img):
                frame = frame.convert('RGBA')
                self.sequence.append(ImageTk.PhotoImage(frame))
            self.configure(image=self.sequence[0])
        except EOFError:
            pass

    def next_frame(self):
        self.idx = (self.idx + 1) % len(self.sequence)
        self.configure(image=self.sequence[self.idx])
        self.after(self.delay, self.next_frame)

# Función para redimensionar las imágenes o GIFs manteniendo la proporción
def resize_image(img, max_width, max_height):
    original_width, original_height = img.size
    scale_factor = min(max_width / original_width, max_height / original_height)
    new_size = (int(original_width * scale_factor), int(original_height * scale_factor))
    return img.resize(new_size, Image.LANCZOS)

# Función para configurar estilos
def configure_styles(root):
    style = ttk.Style(root)
    style.theme_use('clam')

    # Personalizar estilos
    style.configure("TButton", font=('Helvetica', 14), background='#D4B897', foreground='#8B4513')
    style.configure("TEntry", fieldbackground='#F5E8D0', foreground='#8B4513')
    style.configure("Vertical.TScrollbar",
                    background="#C0C0C0",
                    troughcolor="#F5E8D0",
                    bordercolor="#F5E8D0",
                    arrowcolor="#505050",
                    gripcount=0,
                    relief='flat')
    style.configure("Horizontal.TScrollbar",
                    background="#C0C0C0",
                    troughcolor="#F5E8D0",
                    bordercolor="#F5E8D0",
                    arrowcolor="#505050",
                    gripcount=0,
                    relief='flat')

    style.map("Vertical.TScrollbar",
              background=[('active', '#A0A0A0'), ('disabled', '#F5E8D0')],
              arrowcolor=[('active', '#303030')])

    style.map("Horizontal.TScrollbar",
              background=[('active', '#A0A0A0'), ('disabled', '#F5E8D0')],
              arrowcolor=[('active', '#303030')])

    style.map("TButton",
              background=[('active', '#A97C50')],  # Color de fondo cuando está activo
              foreground=[('active', '#FFFFFF')])  # Color del texto cuando está activo

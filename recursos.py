import tkinter as tk
from tkinter import ttk
import webbrowser

class RecursosFrame(tk.Frame):
    def __init__(self, parent, controller, show_frame):
        super().__init__(parent)
        self.controller = controller
        self.show_frame = show_frame
        self.configure(bg='#F5E8D0')

        # Título
        title_label = tk.Label(self, text="Recursos", font=('Helvetica', 20, 'bold'),
                               bg='#F5E8D0', fg='#8B4513')
        title_label.pack(pady=20)

        # Descripción
        description_label = tk.Label(
            self,
            text="Encuentra aquí enlaces a páginas y videos para profundizar en el aprendizaje del lenguaje de señas.",
            font=('Helvetica', 14), bg='#F5E8D0', fg='#8B4513', wraplength=800, justify="center"
        )
        description_label.pack(pady=10)

        # Frame para los recursos con scrollbar
        resources_frame = tk.Frame(self, bg='#F5E8D0')
        resources_frame.pack(pady=10, fill='both', expand=True)

        # Canvas para permitir scroll si hay muchos recursos
        canvas = tk.Canvas(resources_frame, bg='#F5E8D0')
        scrollbar = ttk.Scrollbar(resources_frame, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#F5E8D0')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Binding del evento de la rueda del ratón
        canvas.bind("<MouseWheel>", self.on_mouse_wheel)  # Windows
        canvas.bind("<Button-4>", self.on_mouse_wheel)    # Linux (scroll up)
        canvas.bind("<Button-5>", self.on_mouse_wheel)    # Linux (scroll down)

        # Lista de recursos (enlaces)
        resources = [
            {"title": "Curso de Lengua de Señas Mexicana (LSM)", "url": "https://www.dif.puebla.gob.mx/cursos-lsm", "description": "Curso oficial ofrecido por el DIF de Puebla."},
            {"title": "Alfabeto Dactilológico", "url": "https://www.fundacioncnse.org/alfabeto"},
            {"title": "10 Señas Básicas (LSM) | Tutorial Rápido", "url": "https://www.youtube.com/watch?v=rLL4LJdPRtY"},
            {"title": "25 palabras y frases en LSM para principiantes. Aprende Lengua de Señas Mexicana.", "url": "https://www.youtube.com/watch?v=9kt4R2wCrv4"},
            {"title": "LENGUA DE SEÑAS MEXICANA: PREGUNTAS", "url": "https://www.youtube.com/watch?v=N-XVPcig0LE"},
            {"title": "¡Aprende Lengua de Señas Mexicana en menos de 10 minutos!", "url": "https://www.youtube.com/watch?v=YUlkHjm5AFA"},
        ]

        # Agregar los recursos al frame
        for resource in resources:
            resource_frame = tk.Frame(scrollable_frame, bg='#F5E8D0', pady=5)
            resource_frame.pack(fill='x', padx=20, pady=5)

            title = resource["title"]
            url = resource["url"]

            # Título del recurso como enlace clicable
            resource_title_label = tk.Label(resource_frame, text=title, font=('Helvetica', 14, 'underline'),
                                            fg='blue', bg='#F5E8D0', cursor="hand2")
            resource_title_label.pack(anchor='w')
            resource_title_label.bind("<Button-1>", lambda e, url=url: self.open_link(url))

            # Mostrar la URL (opcional)
            url_label = tk.Label(resource_frame, text=url, font=('Helvetica', 12),
                                 fg='#8B4513', bg='#F5E8D0')
            url_label.pack(anchor='w', padx=20)

            # Descripción (opcional)
            description = resource.get("description", "")
            if description:
                resource_description_label = tk.Label(resource_frame, text=description, font=('Helvetica', 12),
                                                      fg='#8B4513', bg='#F5E8D0', wraplength=700, justify="left")
                resource_description_label.pack(anchor='w', padx=20)

    def open_link(self, url):
        webbrowser.open_new_tab(url)

    def on_mouse_wheel(self, event):
        if event.num == 4:  # Scroll up en Linux
            event.widget.yview_scroll(-1, "units")
        elif event.num == 5:  # Scroll down en Linux
            event.widget.yview_scroll(1, "units")
        else:  # Windows y macOS
            event.widget.yview_scroll(int(-1*(event.delta/120)), "units")

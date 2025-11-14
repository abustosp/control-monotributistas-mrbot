import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import webbrowser
import subprocess
import sys
import pandas as pd
import glob
import threading
from dotenv import load_dotenv
from control import procesar_descarga_mc, procesar_descarga_rcel, control

load_dotenv()

class MonotributistasGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Control de Monotributistas")
        self.geometry("650x780")
        self.resizable(False, False)
        self.configure(bg='#1e1e1e')
        
        # Variable para guardar el archivo seleccionado
        self.archivo_seleccionado = None
        
        # Crear interfaz
        self.crear_interfaz()
        
    def crear_interfaz(self):
        """Crea todos los elementos de la interfaz"""
        # ==================== HEADER CON LOGOS ====================
        header_frame = tk.Frame(self, bg='#1e1e1e')
        header_frame.pack(fill=tk.X, padx=30, pady=(25, 15))
        
        # Logo MrBot (izquierda) - Proporción original: 342x74
        try:
            mrbot_img = Image.open("lib/MrBot.png")
            # Mantener proporción original (4.62:1)
            mrbot_height = 60
            mrbot_width = int(mrbot_height * 342 / 74)
            mrbot_img = mrbot_img.resize((mrbot_width, mrbot_height), Image.Resampling.LANCZOS)
            self.mrbot_photo = ImageTk.PhotoImage(mrbot_img)
            mrbot_label = tk.Label(header_frame, image=self.mrbot_photo, bg='#1e1e1e')
            mrbot_label.pack(side=tk.LEFT, padx=(0, 15))
        except Exception as e:
            print(f"Error cargando MrBot.png: {e}")
        
        # Título central
        title_frame = tk.Frame(header_frame, bg='#1e1e1e')
        title_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        titulo = tk.Label(title_frame, 
                         text="Control de Monotributistas",
                         bg='#1e1e1e',
                         fg='#ffffff',
                         font=("Segoe UI", 16, "bold"))
        titulo.pack(pady=(10, 3))
        
        subtitulo = tk.Label(title_frame,
                            text="Sistema de control y descarga de comprobantes",
                            bg='#1e1e1e',
                            fg='#7fb3d5',
                            font=("Segoe UI", 10))
        subtitulo.pack()
        
        # Logo ABP (derecha) - Proporción original: 189x189 (1:1)
        try:
            abp_img = Image.open("lib/ABP blanco en sin fondo.png")
            # Mantener proporción cuadrada original
            abp_size = 70
            abp_img = abp_img.resize((abp_size, abp_size), Image.Resampling.LANCZOS)
            self.abp_photo = ImageTk.PhotoImage(abp_img)
            abp_label = tk.Label(header_frame, image=self.abp_photo, bg='#1e1e1e')
            abp_label.pack(side=tk.RIGHT, padx=(15, 0))
        except Exception as e:
            print(f"Error cargando ABP blanco en sin fondo.png: {e}")
        
        # Separador decorativo
        separator_frame = tk.Frame(self, bg='#1e1e1e')
        separator_frame.pack(fill=tk.X, padx=30, pady=15)
        
        tk.Frame(separator_frame, height=2, bg='#3a3a3a').pack(fill=tk.X)
        
        # ==================== CONTENIDO PRINCIPAL ====================
        main_frame = tk.Frame(self, bg='#1e1e1e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=10)
        
        # Sección: Seleccionar Archivo
        self.create_section_label("📂  Archivo de Planilla", main_frame)
        
        # Frame contenedor para botón y label
        archivo_container = tk.Frame(main_frame, bg='#282828', relief=tk.FLAT, bd=0)
        archivo_container.pack(fill=tk.X, pady=(8, 5), ipady=2)
        
        self.btn_seleccionar = tk.Button(archivo_container,
                                        text="Seleccionar Excel",
                                        command=self.seleccionar_excel,
                                        bg='#0d7377',
                                        fg='white',
                                        activebackground='#14a085',
                                        activeforeground='white',
                                        font=("Segoe UI", 11, "bold"),
                                        relief=tk.FLAT,
                                        cursor='hand2',
                                        padx=25,
                                        pady=12,
                                        borderwidth=0)
        self.btn_seleccionar.pack(fill=tk.X, padx=8, pady=8)
        
        # Efecto hover para botón seleccionar
        self.btn_seleccionar.bind('<Enter>', lambda e: self.btn_seleccionar.config(bg='#14a085'))
        self.btn_seleccionar.bind('<Leave>', lambda e: self.btn_seleccionar.config(bg='#0d7377'))
        
        self.label_archivo = tk.Label(main_frame,
                                     text="📄 Ningún archivo seleccionado",
                                     bg='#1e1e1e',
                                     fg='#999999',
                                     font=("Segoe UI", 9, "italic"),
                                     anchor="w",
                                     padx=5)
        self.label_archivo.pack(fill=tk.X, pady=(3, 12))
        
        ejemplo_container = tk.Frame(main_frame, bg='#282828', relief=tk.FLAT, bd=0)
        ejemplo_container.pack(fill=tk.X, pady=(0, 20), ipady=2)
        
        self.btn_ejemplo = tk.Button(ejemplo_container,
                                    text="📋 Ver Archivo de Ejemplo",
                                    command=self.abrir_ejemplo,
                                    bg='#323232',
                                    fg='#cccccc',
                                    activebackground='#3e3e3e',
                                    activeforeground='white',
                                    font=("Segoe UI", 10),
                                    relief=tk.FLAT,
                                    cursor='hand2',
                                    padx=20,
                                    pady=10,
                                    borderwidth=0)
        self.btn_ejemplo.pack(fill=tk.X, padx=8, pady=8)
        
        # Efecto hover para botón ejemplo
        self.btn_ejemplo.bind('<Enter>', lambda e: self.btn_ejemplo.config(bg='#3e3e3e'))
        self.btn_ejemplo.bind('<Leave>', lambda e: self.btn_ejemplo.config(bg='#323232'))
        
        # Sección: Descargas
        self.create_section_label("⬇️  Descargas de Comprobantes", main_frame)
        
        descargas_container = tk.Frame(main_frame, bg='#282828', relief=tk.FLAT, bd=0)
        descargas_container.pack(fill=tk.X, pady=(8, 5), ipady=2)
        
        self.btn_descargar_mc = tk.Button(descargas_container,
                                         text="Descargar Mis Comprobantes",
                                         command=self.descargar_mc,
                                         bg='#4a5568',
                                         fg='white',
                                         activebackground='#5a6578',
                                         activeforeground='white',
                                         font=("Segoe UI", 10, "bold"),
                                         relief=tk.FLAT,
                                         cursor='hand2',
                                         padx=20,
                                         pady=10,
                                         borderwidth=0,
                                         state=tk.DISABLED,
                                         disabledforeground='#666666')
        self.btn_descargar_mc.pack(fill=tk.X, padx=8, pady=(8, 4))
        
        self.btn_descargar_rcel = tk.Button(descargas_container,
                                           text="Descargar RCEL",
                                           command=self.descargar_rcel,
                                           bg='#4a5568',
                                           fg='white',
                                           activebackground='#5a6578',
                                           activeforeground='white',
                                           font=("Segoe UI", 10, "bold"),
                                           relief=tk.FLAT,
                                           cursor='hand2',
                                           padx=20,
                                           pady=10,
                                           borderwidth=0,
                                           state=tk.DISABLED,
                                           disabledforeground='#666666')
        self.btn_descargar_rcel.pack(fill=tk.X, padx=8, pady=(4, 8))
        
        # Sección: Procesamiento
        self.create_section_label("⚙️  Procesamiento y Reporte", main_frame)
        
        proceso_container = tk.Frame(main_frame, bg='#282828', relief=tk.FLAT, bd=0)
        proceso_container.pack(fill=tk.X, pady=(8, 5), ipady=2)
        
        self.btn_procesar = tk.Button(proceso_container,
                                     text="🚀 Procesar y Generar Reporte",
                                     command=self.procesar_datos,
                                     bg='#4a5568',
                                     fg='white',
                                     activebackground='#5a6578',
                                     activeforeground='white',
                                     font=("Segoe UI", 11, "bold"),
                                     relief=tk.FLAT,
                                     cursor='hand2',
                                     padx=25,
                                     pady=12,
                                     borderwidth=0,
                                     state=tk.DISABLED,
                                     disabledforeground='#666666')
        self.btn_procesar.pack(fill=tk.X, padx=8, pady=8)
        
        # ==================== FOOTER ====================
        footer_frame = tk.Frame(self, bg='#1e1e1e')
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=30, pady=(15, 25))
        
        # Separador
        tk.Frame(footer_frame, height=2, bg='#3a3a3a').pack(fill=tk.X, pady=(0, 15))
        
        # Link de donaciones
        link_frame = tk.Frame(footer_frame, bg='#1e1e1e')
        link_frame.pack()
        
        tk.Label(link_frame,
                text="¿Te resulta útil esta aplicación?",
                bg='#1e1e1e',
                fg='#aaaaaa',
                font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=5)
        
        link_label = tk.Label(link_frame,
                             text="☕ Invitame un café en Cafecito",
                             bg='#1e1e1e',
                             fg='#7fb3d5',
                             font=("Segoe UI", 9, "bold underline"),
                             cursor='hand2')
        link_label.pack(side=tk.LEFT)
        link_label.bind('<Button-1>', lambda e: self.abrir_donaciones())
        
        # Efecto hover para el link
        link_label.bind('<Enter>', lambda e: link_label.config(fg='#9fc8e5'))
        link_label.bind('<Leave>', lambda e: link_label.config(fg='#7fb3d5'))
    
    def create_section_label(self, text, parent):
        """Crea una etiqueta de sección con estilo"""
        section_frame = tk.Frame(parent, bg='#1e1e1e')
        section_frame.pack(fill=tk.X, pady=(15, 5))
        
        tk.Label(section_frame,
                text=text,
                bg='#1e1e1e',
                fg='#7fb3d5',
                anchor="w",
                font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT)
        
        # Línea decorativa
        tk.Frame(section_frame, height=1, bg='#3a3a3a').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
    
    def seleccionar_excel(self):
        """Abre el diálogo para seleccionar un archivo Excel"""
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo Excel",
            filetypes=[("Archivos Excel", "*.xlsx *.xls"), ("Todos los archivos", "*.*")],
            initialdir=os.getcwd()
        )
        
        if filename:
            self.archivo_seleccionado = filename
            # Mostrar solo el nombre del archivo
            nombre_archivo = os.path.basename(filename)
            self.label_archivo.config(text=f"✅ {nombre_archivo}", fg='#4ade80', font=("Segoe UI", 9, "bold"))
            
            # Habilitar botones de descarga y procesamiento con colores activos
            self.btn_descargar_mc.config(
                state=tk.NORMAL,
                bg='#2563eb',
                cursor='hand2'
            )
            self.btn_descargar_rcel.config(
                state=tk.NORMAL,
                bg='#2563eb',
                cursor='hand2'
            )
            self.btn_procesar.config(
                state=tk.NORMAL,
                bg='#059669',
                cursor='hand2'
            )
            
            # Agregar efectos hover a botones habilitados
            self.btn_descargar_mc.bind('<Enter>', lambda e: self.btn_descargar_mc.config(bg='#3b82f6'))
            self.btn_descargar_mc.bind('<Leave>', lambda e: self.btn_descargar_mc.config(bg='#2563eb'))
            
            self.btn_descargar_rcel.bind('<Enter>', lambda e: self.btn_descargar_rcel.config(bg='#3b82f6'))
            self.btn_descargar_rcel.bind('<Leave>', lambda e: self.btn_descargar_rcel.config(bg='#2563eb'))
            
            self.btn_procesar.bind('<Enter>', lambda e: self.btn_procesar.config(bg='#10b981'))
            self.btn_procesar.bind('<Leave>', lambda e: self.btn_procesar.config(bg='#059669'))
            
    def abrir_ejemplo(self):
        """Abre el archivo de ejemplo"""
        archivo_ejemplo = "planilla-control-monotributistas-ejemplo.xlsx"
        
        if os.path.exists(archivo_ejemplo):
            try:
                if sys.platform == 'win32':
                    os.startfile(archivo_ejemplo)
                elif sys.platform == 'darwin':  # macOS
                    subprocess.call(['open', archivo_ejemplo])
                else:  # linux
                    subprocess.call(['xdg-open', archivo_ejemplo])
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{e}")
        else:
            messagebox.showerror("Error", f"No se encontró el archivo:\n{archivo_ejemplo}")
    
    def descargar_mc(self):
        """Ejecuta la descarga de Mis Comprobantes"""
        if not self.archivo_seleccionado:
            messagebox.showwarning("Advertencia", "Primero debes seleccionar un archivo Excel")
            return
        
        respuesta = messagebox.askyesno(
            "Confirmar Descarga",
            "¿Deseas iniciar la descarga de Mis Comprobantes?\n\nEsto puede tardar varios minutos."
        )
        
        if respuesta:
            # Ejecutar en hilo separado para no bloquear la UI
            thread = threading.Thread(target=self._ejecutar_descarga_mc, daemon=True)
            thread.start()
    
    def _ejecutar_descarga_mc(self):
        """Ejecuta la descarga de MC en segundo plano"""
        try:
            # Deshabilitar botones durante el proceso
            self.after(0, lambda: self.btn_descargar_mc.config(state=tk.DISABLED, text="Descargando..."))
            
            # Leer variables de entorno
            mrbot_user = os.getenv("MRBOT_USER")
            mrbot_api_key = os.getenv("MRBOT_API_KEY")
            base_url = os.getenv("BASE_URL")
            mis_comprobantes_endpoint = os.getenv("MIS_COMPROBANTES_ENDPOINT")
            downloads_mc_path = os.getenv("DOWNLOADS_MC_PATH", "descargas_mis_comprobantes")
            
            # Verificar variables
            if not all([mrbot_user, mrbot_api_key, base_url, mis_comprobantes_endpoint]):
                self.after(0, lambda: messagebox.showerror(
                    "Error de Configuración",
                    "Faltan variables de entorno necesarias.\nVerifica el archivo .env"
                ))
                return
            
            # Leer Excel
            df = pd.read_excel(self.archivo_seleccionado)
            
            # Procesar cada fila
            for index, row in df.iterrows():
                procesar_descarga_mc(row, mrbot_user, mrbot_api_key, base_url, 
                                    mis_comprobantes_endpoint, downloads_mc_path)
            
            self.after(0, lambda: messagebox.showinfo(
                "Éxito",
                "Descarga de Mis Comprobantes completada."
            ))
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror(
                "Error",
                f"Error durante la descarga:\n{str(e)}"
            ))
        finally:
            # Rehabilitar botón
            self.after(0, lambda: self.btn_descargar_mc.config(
                state=tk.NORMAL,
                text="Descargar Mis Comprobantes"
            ))
    
    def descargar_rcel(self):
        """Ejecuta la descarga de RCEL"""
        if not self.archivo_seleccionado:
            messagebox.showwarning("Advertencia", "Primero debes seleccionar un archivo Excel")
            return
        
        respuesta = messagebox.askyesno(
            "Confirmar Descarga",
            "¿Deseas iniciar la descarga de RCEL?\n\nEsto puede tardar varios minutos."
        )
        
        if respuesta:
            # Ejecutar en hilo separado para no bloquear la UI
            thread = threading.Thread(target=self._ejecutar_descarga_rcel, daemon=True)
            thread.start()
    
    def _ejecutar_descarga_rcel(self):
        """Ejecuta la descarga de RCEL en segundo plano"""
        try:
            # Deshabilitar botones durante el proceso
            self.after(0, lambda: self.btn_descargar_rcel.config(state=tk.DISABLED, text="Descargando..."))
            
            # Leer variables de entorno
            mrbot_user = os.getenv("MRBOT_USER")
            mrbot_api_key = os.getenv("MRBOT_API_KEY")
            base_url = os.getenv("BASE_URL")
            rcel_endpoint = os.getenv("RCEL_ENDPOINT")
            downloads_rcel_path = os.getenv("DOWNLOADS_RCEL_PATH", "descargas_rcel")
            
            # Verificar variables
            if not all([mrbot_user, mrbot_api_key, base_url, rcel_endpoint]):
                self.after(0, lambda: messagebox.showerror(
                    "Error de Configuración",
                    "Faltan variables de entorno necesarias.\nVerifica el archivo .env"
                ))
                return
            
            # Leer Excel
            df = pd.read_excel(self.archivo_seleccionado)
            
            # Procesar cada fila
            for index, row in df.iterrows():
                procesar_descarga_rcel(row, mrbot_user, mrbot_api_key, base_url, 
                                      rcel_endpoint, downloads_rcel_path)
            
            self.after(0, lambda: messagebox.showinfo(
                "Éxito",
                "Descarga de RCEL completada."
            ))
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror(
                "Error",
                f"Error durante la descarga:\n{str(e)}"
            ))
        finally:
            # Rehabilitar botón
            self.after(0, lambda: self.btn_descargar_rcel.config(
                state=tk.NORMAL,
                text="Descargar RCEL"
            ))
    
    def procesar_datos(self):
        """Procesa los datos y genera el reporte"""
        if not self.archivo_seleccionado:
            messagebox.showwarning("Advertencia", "Primero debes seleccionar un archivo Excel")
            return
        
        respuesta = messagebox.askyesno(
            "Confirmar Procesamiento",
            "¿Deseas procesar los datos y generar el reporte?\n\n" +
            "Se generará el archivo:\n'Reporte Recategorizaciones de Monotributistas.xlsx'"
        )
        
        if respuesta:
            # Ejecutar en hilo separado para no bloquear la UI
            thread = threading.Thread(target=self._ejecutar_procesamiento, daemon=True)
            thread.start()
    
    def _ejecutar_procesamiento(self):
        """Ejecuta el procesamiento en segundo plano"""
        try:
            # Deshabilitar botón durante el proceso
            self.after(0, lambda: self.btn_procesar.config(state=tk.DISABLED, text="Procesando..."))
            
            downloads_mc_path = os.getenv("DOWNLOADS_MC_PATH", "descargas_mis_comprobantes")
            downloads_rcel_path = os.getenv("DOWNLOADS_RCEL_PATH", "descargas_rcel")
            
            # Buscar archivos de Mis Comprobantes y RCEL
            archivos_mc = glob.glob(f"{downloads_mc_path}/**/extraido/*.csv", recursive=True)
            archivos_PDF = []  # No se usan archivos PDF directamente
            archivos_PDF_JSON = glob.glob(f"{downloads_rcel_path}/**/*.json", recursive=True)
            
            if not archivos_mc and not archivos_PDF_JSON:
                self.after(0, lambda: messagebox.showwarning(
                    "Sin Archivos",
                    "No se encontraron archivos para procesar.\n\n" +
                    "Primero descarga los comprobantes."
                ))
                return
            
            # Ejecutar función de control
            control(archivos_mc, archivos_PDF, archivos_PDF_JSON)
            
            self.after(0, lambda: messagebox.showinfo(
                "Éxito",
                "Reporte generado exitosamente.\n\n" +
                "Archivo: 'Reporte Recategorizaciones de Monotributistas.xlsx'"
            ))
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror(
                "Error",
                f"Error durante el procesamiento:\n{str(e)}"
            ))
        finally:
            # Rehabilitar botón
            self.after(0, lambda: self.btn_procesar.config(
                state=tk.NORMAL,
                text="🚀 Procesar y Generar Reporte"
            ))
    
    def abrir_donaciones(self):
        """Abre el link de donaciones en el navegador"""
        webbrowser.open("https://cafecito.app/abustos")

def main():
    app = MonotributistasGUI()
    app.mainloop()


if __name__ == "__main__":
    main()

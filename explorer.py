# Explorador de archivos moderno en Python usando Tkinter
# Cada archivo y carpeta es un objeto
# Se aplican patrones de diseño GOF y principios SOLID
# Se documenta cada linea en espanol y se declaran variables al inicio de cada bloque

import os  # Módulo para operaciones del sistema operativo
import sys  # Módulo para acceder a variables del sistema
import tkinter as tk  # Biblioteca de interfaz gráfica
from tkinter import ttk  # Conjunto de widgets temáticos
from abc import ABC, abstractmethod  # Herramientas para clases abstractas

# ------------------------------------------------------------
# Definición de la clase base para los elementos del sistema
# ------------------------------------------------------------
class ItemSistema(ABC):
    """Clase base para archivos y directorios."""

    def __init__(self, ruta):
        ruta_objeto = ruta  # Ruta del elemento en el sistema
        self.ruta = ruta_objeto  # Se asigna a un atributo de instancia

    @abstractmethod
    def nombre(self):
        nombre_objeto = os.path.basename(self.ruta)  # Nombre del archivo/directorio
        return nombre_objeto  # Se devuelve el nombre

    @abstractmethod
    def es_directorio(self):
        es_dir = os.path.isdir(self.ruta)  # Booleano para verificar si es directorio
        return es_dir  # Se devuelve el resultado


# ------------------------------------------------------------
# Implementación concreta para archivos
# ------------------------------------------------------------
class Archivo(ItemSistema):
    """Representa un archivo del sistema."""

    def __init__(self, ruta):
        super().__init__(ruta)  # Llama al constructor de la clase base

    def nombre(self):  # Devuelve el nombre del archivo
        nombre_archivo = os.path.basename(self.ruta)
        return nombre_archivo

    def es_directorio(self):  # Un archivo nunca es directorio
        return False


# ------------------------------------------------------------
# Implementación concreta para directorios
# ------------------------------------------------------------
class Directorio(ItemSistema):
    """Representa un directorio que puede contener otros items."""

    def __init__(self, ruta):
        super().__init__(ruta)  # Llama al constructor de la clase base
        hijos = []  # Se declara la lista de hijos
        self.hijos = hijos  # Lista de elementos dentro del directorio

    def nombre(self):  # Devuelve el nombre del directorio
        nombre_directorio = os.path.basename(self.ruta)
        return nombre_directorio

    def es_directorio(self):  # Un directorio es siempre True
        return True

    def cargar_hijos(self):  # Carga los archivos y carpetas hijos
        hijos_temp = []  # Lista temporal de hijos
        for nombre in os.listdir(self.ruta):  # Itera sobre el contenido
            ruta_completa = os.path.join(self.ruta, nombre)  # Ruta completa del item
            if os.path.isdir(ruta_completa):  # Si es un directorio
                hijos_temp.append(Directorio(ruta_completa))  # Agrega directorio
            else:
                hijos_temp.append(Archivo(ruta_completa))  # Agrega archivo
        self.hijos = hijos_temp  # Actualiza la lista de hijos


# ------------------------------------------------------------
# Interface del patrón Command
# ------------------------------------------------------------
class Comando(ABC):
    """Interface base para comandos."""

    @abstractmethod
    def ejecutar(self):
        pass  # Método que se implementará en concretos


# ------------------------------------------------------------
# Comando para abrir elementos
# ------------------------------------------------------------
class ComandoAbrir(Comando):
    """Comando concreto para abrir archivos o directorios."""

    def __init__(self, item):
        item_objetivo = item  # Objeto a abrir
        self.item = item_objetivo  # Se asigna al atributo

    def ejecutar(self):
        if self.item.es_directorio():  # Si es directorio
            ExploradorControlador.instancia().abrir_directorio(self.item.ruta)
        else:
            if sys.platform.startswith('darwin'):  # Apertura en macOS
                os.system(f'open "{self.item.ruta}"')
            elif os.name == 'nt':  # Apertura en Windows
                os.startfile(self.item.ruta)
            else:  # Apertura en Linux u otros
                os.system(f'xdg-open "{self.item.ruta}"')


# ------------------------------------------------------------
# Controlador siguiendo el patrón Singleton
# ------------------------------------------------------------
class ExploradorControlador:
    """Maneja las operaciones principales del explorador."""

    _instancia = None  # Variable de clase para la instancia única

    def __init__(self, vista):
        vista_asignada = vista  # Se recibe la vista
        self.vista = vista_asignada  # Se asigna al atributo
        self.directorio_actual = Directorio(os.getcwd())  # Directorio inicial
        self.directorio_actual.cargar_hijos()  # Se cargan los hijos del directorio

    @classmethod
    def crear(cls, vista):  # Método para crear o devolver la instancia
        if cls._instancia is None:  # Si no existe
            cls._instancia = cls(vista)  # Crea la instancia
        return cls._instancia  # Devuelve la instancia

    @classmethod
    def instancia(cls):  # Devuelve la instancia existente
        return cls._instancia

    def abrir_directorio(self, ruta):  # Abre un directorio dado
        nuevo_directorio = Directorio(ruta)  # Se crea el nuevo directorio
        nuevo_directorio.cargar_hijos()  # Se cargan sus hijos
        self.directorio_actual = nuevo_directorio  # Se actualiza el actual
        self.vista.mostrar_directorio(nuevo_directorio)  # Se actualiza la vista

    def abrir_item(self, item):  # Ejecuta el comando de abrir
        comando = ComandoAbrir(item)  # Se crea el comando
        comando.ejecutar()  # Se ejecuta


# ------------------------------------------------------------
# Vista del explorador usando Tkinter
# ------------------------------------------------------------
class ExploradorVista(tk.Frame):
    """Vista principal del explorador de archivos."""

    def __init__(self, maestro):
        tk.Frame.__init__(self, master=maestro)  # Inicialización de tk.Frame
        self.pack(fill=tk.BOTH, expand=True)  # Empaqueta el frame
        self.tree = ttk.Treeview(self)  # Widget de árbol
        self.tree.pack(fill=tk.BOTH, expand=True)  # Coloca el árbol
        self.tree.bind('<Double-1>', self._doble_click)  # Enlace de doble clic
        self.controlador = ExploradorControlador.crear(self)  # Se crea el controlador
        self.mostrar_directorio(self.controlador.directorio_actual)  # Muestra directorio inicial

    def mostrar_directorio(self, directorio):  # Muestra el contenido de un directorio
        self.tree.delete(*self.tree.get_children())  # Elimina el contenido previo
        for item in directorio.hijos:  # Itera sobre los hijos
            texto = item.nombre()  # Texto a mostrar
            nodo = self.tree.insert('', 'end', text=texto, values=[item.ruta])  # Inserta nodo
            if item.es_directorio():  # Si es directorio, agrega un marcador
                self.tree.insert(nodo, 'end')  # Agrega hijo vacío para expandible

    def _doble_click(self, evento):  # Maneja doble clic en un elemento
        seleccion = self.tree.selection()  # Elemento seleccionado
        if not seleccion:  # Si no hay selección
            return  # Se sale
        item_id = seleccion[0]  # ID del elemento
        ruta = self.tree.item(item_id, 'values')[0]  # Ruta asociada
        if os.path.isdir(ruta):  # Si es directorio
            self.controlador.abrir_directorio(ruta)  # Se abre el directorio
        else:
            self.controlador.abrir_item(Archivo(ruta))  # Se abre el archivo


# ------------------------------------------------------------
# Función principal para iniciar la aplicación
# ------------------------------------------------------------
def main():
    ruta_inicial = os.getcwd()  # Ruta inicial del explorador
    raiz = tk.Tk()  # Ventana principal de Tkinter
    raiz.title('Explorador de Archivos Moderno')  # Título de la ventana
    vista = ExploradorVista(raiz)  # Se crea la vista y se asocia a la ventana
    raiz.mainloop()  # Bucle principal de la interfaz


if __name__ == '__main__':
    main()  # Se ejecuta la función principal

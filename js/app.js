// Clase base para un ítem del sistema
class Item {
    constructor(path) {
        // Ruta del ítem
        const ruta = path;
        this.path = ruta;
    }

    // Devuelve el nombre del ítem
    nombre() {
        const nombreItem = this.path.split('/').pop();
        return nombreItem;
    }

    // Determina si es directorio (por defecto falso)
    esDirectorio() {
        return false;
    }
}

// Clase que representa un archivo
class Archivo extends Item {
    constructor(path) {
        // Llama al constructor base
        super(path);
    }
}

// Clase que representa un directorio
class Directorio extends Item {
    constructor(path) {
        super(path);
        // Lista de hijos
        let hijos = [];
        this.hijos = hijos;
    }

    // Sobrescribe para indicar que es un directorio
    esDirectorio() {
        return true;
    }
}

// Comando para abrir un ítem
class ComandoAbrir {
    constructor(item) {
        // Ítem a abrir
        const itemObjetivo = item;
        this.item = itemObjetivo;
    }

    // Ejecuta la acción de abrir
    ejecutar() {
        if (this.item.esDirectorio()) {
            // Si es directorio, se muestra su contenido
            vista.mostrarDirectorio(this.item);
        } else {
            // Si es archivo, se intenta abrir
            window.open(URL.createObjectURL(this.item.file), '_blank');
        }
    }
}

// Clase principal del explorador
class Explorador {
    constructor() {
        // Directorio actual
        let dirActual = null;
        this.directorioActual = dirActual;
    }

    // Abre un directorio
    abrirDirectorio(directorio) {
        this.directorioActual = directorio;
        vista.mostrarDirectorio(directorio);
    }
}

// Vista del explorador
class ExploradorVista {
    constructor() {
        // Referencia al contenedor principal
        const contenedor = document.getElementById('app');
        this.contenedor = contenedor;
        // Header con botón para seleccionar carpeta
        const header = document.createElement('header');
        this.header = header;
        // Input para seleccionar directorios
        const input = document.createElement('input');
        input.type = 'file';
        input.webkitdirectory = true;
        header.appendChild(input);
        contenedor.appendChild(header);
        // Lista donde se muestran los archivos
        const lista = document.createElement('div');
        lista.id = 'file-list';
        this.lista = lista;
        contenedor.appendChild(lista);
        // Explorador controlador
        const controlador = new Explorador();
        this.controlador = controlador;
        // Maneja cambio en input
        input.addEventListener('change', (e) => {
            // Archivos seleccionados
            const archivos = e.target.files;
            const raiz = new Directorio('');
            // Crea objetos para cada archivo
            for (let i = 0; i < archivos.length; i++) {
                const file = archivos[i];
                const partes = file.webkitRelativePath.split('/');
                this._agregarEnArbol(raiz, partes, file);
            }
            this.controlador.abrirDirectorio(raiz);
        });
    }

    // Agrega archivo al árbol de directorios
    _agregarEnArbol(directorio, partes, file) {
        // Directorio actual en el recorrido
        let actual = directorio;
        for (let i = 0; i < partes.length; i++) {
            const parte = partes[i];
            if (i === partes.length - 1) {
                const archivo = new Archivo(parte);
                archivo.file = file;
                actual.hijos.push(archivo);
            } else {
                let dirHijo = actual.hijos.find(h => h.esDirectorio() && h.path === parte);
                if (!dirHijo) {
                    dirHijo = new Directorio(parte);
                    actual.hijos.push(dirHijo);
                }
                actual = dirHijo;
            }
        }
    }

    // Muestra el contenido de un directorio
    mostrarDirectorio(directorio) {
        this.lista.innerHTML = '';
        for (let i = 0; i < directorio.hijos.length; i++) {
            const item = directorio.hijos[i];
            const div = document.createElement('div');
            div.className = 'file-item';
            div.textContent = item.nombre();
            div.addEventListener('dblclick', () => {
                const comando = new ComandoAbrir(item);
                comando.ejecutar();
            });
            this.lista.appendChild(div);
        }
    }
}

// Instancia global de la vista
const vista = new ExploradorVista();

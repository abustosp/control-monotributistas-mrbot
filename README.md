# Control de Monotributistas

Sistema automatizado para el control y recategorización de monotributistas mediante la descarga y análisis de comprobantes desde AFIP utilizando la API de MrBot.

## Tabla de Contenidos

- [Descripción](#descripción)
- [Características](#características)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Requisitos Previos](#requisitos-previos)
- [Instalación](#instalación)
  - [Windows](#windows)
  - [Linux](#linux)
- [Configuración](#configuración)
- [Uso](#uso)
  - [Interfaz Gráfica (GUI)](#interfaz-gráfica-gui)
  - [Línea de Comandos](#línea-de-comandos)
- [Opciones y Parámetros](#opciones-y-parámetros)
- [Estructura de Archivos](#estructura-de-archivos)
- [Salida del Programa](#salida-del-programa)
- [Testing](#testing)
- [Solución de Problemas](#solución-de-problemas)
- [Contribuir](#contribuir)
- [Autor](#autor)
- [Licencia](#licencia)
- [Donaciones](#donaciones)

## Descripción

Este proyecto permite automatizar el proceso de control de categorías de monotributistas comparando los ingresos declarados con las escalas vigentes de AFIP. El sistema descarga comprobantes desde "Mis Comprobantes" y RCEL (Registro de Comprobantes en Línea) utilizando la API de MrBot, procesa la información y genera un reporte completo en Excel.

## Características

- **Descarga automática** de comprobantes desde Mis Comprobantes (MC) y RCEL
- **Procesamiento concurrente** para optimizar tiempos de descarga
- **Cálculo de prorrateo** de ingresos según períodos configurables
- **Cruce de información** entre MC y RCEL
- **Generación de reportes** en Excel con formato profesional
- **Interfaz gráfica** intuitiva para usuarios no técnicos
- **Modo consola** para automatización y scripts
- **Validación de categorías** según escalas de AFIP

## Estructura del Proyecto

```
control-monotributistas/
├── descargas_mis_comprobantes/     # Directorio de descargas MC
│   └── [CUIT]_[Nombre]/
│       └── extraido/               # CSVs extraídos
├── descargas_rcel/                 # Directorio de descargas RCEL
│   └── [CUIT]_[Nombre]/
│       ├── *.pdf                   # PDFs de facturas
│       └── *.json                  # Metadata de facturas
├── lib/                            # Módulos del proyecto
│   ├── caller_mc.py               # Cliente API Mis Comprobantes
│   ├── caller_rcel.py             # Cliente API RCEL
│   ├── caller_user.py             # Cliente API Usuario
│   ├── formatos.py                # Formateo de Excel
│   ├── helpers.py                 # Funciones auxiliares
│   ├── procesadores.py            # Procesadores de datos
│   ├── utils.py                   # Utilidades generales
│   ├── ABP blanco en sin fondo.png
│   └── MrBot.png
├── test/                          # Tests del proyecto
│   └── test_control.py
├── Categorias.xlsx                # Escalas de categorías AFIP
├── control.py                     # Script principal
├── gui.py                         # Interfaz gráfica
├── planilla-control-monotributistas.xlsx        # Planilla principal
├── planilla-control-monotributistas-ejemplo.xlsx # Ejemplo
├── requirements.txt               # Dependencias Python
├── test_performance.py           # Tests de rendimiento
└── README.md                     # Este archivo
```

## Requisitos Previos

- **Python** 3.8 o superior
- **Cuenta en MrBot** ([api-bots.mrbot.com.ar](https://api-bots.mrbot.com.ar/))
- **API Key de MrBot** (solicitar en el panel de usuario)
- **Claves fiscales** de los contribuyentes a procesar
- **Microsoft Excel** o LibreOffice Calc (para visualizar reportes)

## Instalación

### Windows

1. **Instalar Python**
   - Descargar Python desde [python.org](https://www.python.org/downloads/)
   - Durante la instalación, marcar la opción "Add Python to PATH"
   - Verificar instalación:
     ```cmd
     python --version
     ```

2. **Clonar o descargar el proyecto**
   ```cmd
   git clone https://github.com/tu-usuario/control-monotributistas.git
   cd control-monotributistas
   ```
   
   O descargar el ZIP y extraerlo en una carpeta.

3. **Crear entorno virtual** (recomendado)
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

4. **Instalar dependencias**
   ```cmd
   pip install -r requirements.txt
   ```

### Linux

1. **Verificar Python**
   ```bash
   python3 --version
   ```
   
   Si no está instalado:
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3 python3-pip python3-venv

   # Fedora
   sudo dnf install python3 python3-pip

   # Arch Linux
   sudo pacman -S python python-pip
   ```

2. **Clonar o descargar el proyecto**
   ```bash
   git clone https://github.com/tu-usuario/control-monotributistas.git
   cd control-monotributistas
   ```

3. **Crear entorno virtual** (recomendado)
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

## Configuración

### 1. Configurar Variables de Entorno

Crear un archivo `.env` en la raíz del proyecto basándose en `.env.example`:

```bash
# Windows
copy .env.example .env

# Linux
cp .env.example .env
```

Editar el archivo `.env` con tus credenciales:

```env
# Credenciales MrBot
MRBOT_USER = "tu-email@mrbot.com.ar"
MRBOT_API_KEY = "tu-api-key-de-mrbot"

# Configuración API
BASE_URL = "https://api.mrbot.com.ar"
VERSION = "v1"
MAX_WORKERS = 10

# Endpoints
USER_ENDPOINT = "api/v1/user"
MIS_COMPROBANTES_ENDPOINT = "api/v1/mis_comprobantes"
RCEL_ENDPOINT = "api/v1/rcel"

# Directorios de descarga
DOWNLOADS_MC_PATH = "descargas_mis_comprobantes"
DOWNLOADS_RCEL_PATH = "descargas_rcel"
```

### 2. Configurar Archivo de Categorías

El archivo `Categorias.xlsx` debe contener:

- **Hoja "Categorías"**: Tabla con las escalas de AFIP (columnas: `Categoria`, `Ingresos brutos`)
- **Hoja "Rango de Fechas"**: 
  - Celda A2: Fecha inicial del período (formato: dd/mm/yyyy)
  - Celda B2: Fecha final del período (formato: dd/mm/yyyy)

### 3. Preparar Planilla de Control

Completar el archivo `planilla-control-monotributistas.xlsx` con los datos de los contribuyentes:

| Columna | Descripción | Ejemplo |
|---------|-------------|---------|
| CUIT_Representante | CUIT del representante/contador | 20123456789 |
| Clave_representante | Clave fiscal del representante | MiClave123 |
| CUIT_Representado | CUIT del monotributista | 27987654321 |
| Denominacion_MC | Nombre según Mis Comprobantes | PEREZ JUAN |
| Denominacion_RCEL | Nombre según RCEL | PEREZ JUAN |
| Descarga_MC | Descargar Mis Comprobantes (si/no) | si |
| Descarga_MC_emitidos | Descargar emitidos (si/no) | si |
| Descarga_MC_recibidos | Descargar recibidos (si/no) | no |
| Desde_MC | Fecha inicio MC | 01/01/2024 |
| Hasta_MC | Fecha fin MC | 31/12/2024 |
| Descarga_RCEL | Descargar RCEL (si/no) | si |
| Desde_RCEL | Fecha inicio RCEL | 01/01/2024 |
| Hasta_RCEL | Fecha fin RCEL | 31/12/2024 |

Ver `planilla-control-monotributistas-ejemplo.xlsx` para referencia.

## Uso

### Interfaz Gráfica (GUI)

La forma más sencilla para usuarios no técnicos:

```bash
# Windows
python gui.py

# Linux
python3 gui.py
```

**Pasos en la GUI:**

1. **Seleccionar archivo Excel** → Clic en "Seleccionar Excel"
2. **Descargar comprobantes** → Clic en "Descargar Mis Comprobantes" y/o "Descargar RCEL"
3. **Generar reporte** → Clic en "🚀 Procesar y Generar Reporte"

### Línea de Comandos

Para automatización o ejecución en servidores:

```bash
# Windows
python control.py

# Linux
python3 control.py
```

El script ejecutará las siguientes tareas automáticamente:

1. Leer la planilla `planilla-control-monotributistas.xlsx`
2. Descargar comprobantes de Mis Comprobantes (según configuración)
3. Descargar facturas de RCEL (según configuración)
4. Procesar todos los archivos descargados
5. Generar el reporte `Reporte Recategorizaciones de Monotributistas.xlsx`

## Opciones y Parámetros

### Variables de Entorno

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `MRBOT_USER` | Email de usuario MrBot | (requerido) |
| `MRBOT_API_KEY` | API Key de MrBot | (requerido) |
| `BASE_URL` | URL base de la API | https://api.mrbot.com.ar |
| `MAX_WORKERS` | Hilos concurrentes para descargas | 10 |
| `DOWNLOADS_MC_PATH` | Directorio de descargas MC | descargas_mis_comprobantes |
| `DOWNLOADS_RCEL_PATH` | Directorio de descargas RCEL | descargas_rcel |

### Parámetros de la Planilla

| Parámetro | Valores Válidos | Descripción |
|-----------|----------------|-------------|
| `Descarga_MC` | si / no | Habilita descarga de Mis Comprobantes |
| `Descarga_MC_emitidos` | si / no | Descarga comprobantes emitidos |
| `Descarga_MC_recibidos` | si / no | Descarga comprobantes recibidos |
| `Descarga_RCEL` | si / no | Habilita descarga de RCEL |

**Nota:** Las fechas deben estar en formato `dd/mm/yyyy`

## Estructura de Archivos

### Archivos de Entrada

- **`planilla-control-monotributistas.xlsx`**: Planilla con datos de contribuyentes
- **`Categorias.xlsx`**: Escalas de categorías AFIP y rango de fechas
- **`.env`**: Variables de entorno y credenciales

### Archivos de Salida

- **`Reporte Recategorizaciones de Monotributistas.xlsx`**: Reporte final con:
  - **Hoja "Tabla Dinámica"**: Resumen por contribuyente con categoría sugerida
  - **Hoja "Consolidado"**: Detalle de todos los comprobantes procesados

### Estructura de Descargas

```
descargas_mis_comprobantes/
└── [CUIT]_[Nombre]/
    ├── [archivo].zip
    └── extraido/
        ├── MCE-[...].csv      # Comprobantes emitidos
        └── MCR-[...].csv      # Comprobantes recibidos

descargas_rcel/
└── [CUIT]_[Nombre]/
    ├── [CUIT]-[COD]-[PtoVenta]-[Numero].pdf
    └── [CUIT]-[COD]-[PtoVenta]-[Numero].json
```

## Salida del Programa

El reporte generado contiene:

### Tabla Dinámica
- Cliente y tipo de comprobante (MC)
- Cantidad de comprobantes
- Importe prorrateado total
- Categoría sugerida según escala AFIP
- Ingresos brutos máximos de la categoría

### Consolidado
- Detalle completo de cada comprobante
- Información de emisor/receptor
- Fechas de emisión y validez
- Cálculos de prorrateo
- Indicador de cruce con RCEL
- Referencias a archivos PDF (cuando aplica)

## Testing

Ejecutar tests de rendimiento:

```bash
# Windows
python test_performance.py

# Linux
python3 test_performance.py
```

Ejecutar tests unitarios:

```bash
# Windows
pytest test/

# Linux
python3 -m pytest test/
```

## Solución de Problemas

### Error: "No se encontró el módulo X"
```bash
pip install -r requirements.txt
```

### Error: "Faltan variables de entorno"
Verificar que el archivo `.env` existe y contiene todas las variables requeridas.

### Error: "No se pudo conectar a la API"
- Verificar credenciales en `.env`
- Confirmar que tienes acceso activo a MrBot
- Revisar conexión a Internet

### Los archivos no se descargan
- Verificar que las claves fiscales sean correctas
- Confirmar que el CUIT tiene representación fiscal activa
- Revisar que las fechas estén en el formato correcto

## Contribuir

Las contribuciones son bienvenidas. Para cambios importantes:

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## Autor

**Agustín Bustos Piasentini**
- MrBot: [www.mrbot.com.ar](https://www.mrbot.com.ar)
- Cafecito: [cafecito.app/abustos](https://cafecito.app/abustos)

## Licencia

Este proyecto es de código abierto y está disponible bajo la licencia que el autor determine.

## Donaciones
Si este proyecto te resulta útil, puedes invitarme un café en [Cafecito](https://cafecito.app/abustos).

---

**Nota**: Este proyecto requiere una suscripción activa a MrBot para funcionar. MrBot es un servicio de automatización de AFIP desarrollado por profesionales independientes.

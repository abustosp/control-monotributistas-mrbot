"""
Módulo de procesamiento de descargas genérico
"""
import os
from typing import Callable, Dict, Any, Optional, List
from lib.helpers import formatear_fecha, normalizar_si_no, construir_nombre_directorio


def procesar_descarga_generica(
    row: Any,
    tipo_descarga: str,
    callback_consulta: Callable,
    callback_procesamiento: Callable,
    credenciales: Dict[str, str],
    columnas_config: Dict[str, str]
) -> None:
    """
    Función genérica para procesar descargas de contribuyentes.
    
    Args:
        row: Fila del DataFrame con los datos del contribuyente
        tipo_descarga: Tipo de descarga ('MC' o 'RCEL')
        callback_consulta: Función para consultar la API
        callback_procesamiento: Función para procesar la respuesta
        credenciales: Diccionario con credenciales de API
        columnas_config: Diccionario con nombres de columnas específicas
    """
    # Extraer datos comunes
    cuit_representante = str(row['CUIT_Representante'])
    clave_representante = row['Clave_representante']
    cuit_representado = str(row['CUIT_Representado'])
    
    # Extraer datos específicos según el tipo
    desde = formatear_fecha(row[columnas_config['desde']])
    hasta = formatear_fecha(row[columnas_config['hasta']])
    denominacion = row[columnas_config['denominacion']]
    descarga_activa = normalizar_si_no(row[columnas_config['descarga']])
    
    # Verificar si debe descargar
    if descarga_activa != 'si':
        print(f"Saltando descarga {tipo_descarga} para CUIT {cuit_representado} - Descarga: {descarga_activa}")
        return
    
    print(f"\n{'='*80}")
    print(f"Procesando {tipo_descarga}: {denominacion} - CUIT: {cuit_representado}")
    print(f"Desde {desde} hasta {hasta}")
    print(f"{'='*80}\n")
    
    try:
        # Consultar API
        response = callback_consulta(
            cuit_representante=cuit_representante,
            clave_representante=clave_representante,
            cuit_representado=cuit_representado,
            desde=desde,
            hasta=hasta,
            denominacion=denominacion,
            **credenciales
        )
        
        # Procesar respuesta
        callback_procesamiento(
            response=response,
            cuit_representado=cuit_representado,
            denominacion=denominacion
        )
        
        print(f"\n✓ Proceso {tipo_descarga} completado para {denominacion}")
        
    except Exception as e:
        print(f"\n✗ Error procesando {tipo_descarga} {denominacion} (CUIT: {cuit_representado}): {e}")


def crear_directorios_descarga(
    base_path: str, 
    cuit: str, 
    denominacion: str,
    subdirectorios: Optional[List[str]] = None
) -> Dict[str, str]:
    """
    Crea la estructura de directorios para las descargas.
    
    Args:
        base_path: Ruta base para las descargas
        cuit: CUIT del contribuyente
        denominacion: Denominación del contribuyente
        subdirectorios: Lista de subdirectorios a crear (opcional)
        
    Returns:
        Dict[str, str]: Diccionario con las rutas creadas
    """
    dir_contribuyente = os.path.join(base_path, construir_nombre_directorio(cuit, denominacion))
    os.makedirs(dir_contribuyente, exist_ok=True)
    
    rutas = {'principal': dir_contribuyente}
    
    if subdirectorios:
        for subdir in subdirectorios:
            ruta_subdir = os.path.join(dir_contribuyente, subdir)
            os.makedirs(ruta_subdir, exist_ok=True)
            rutas[subdir] = ruta_subdir
    
    return rutas

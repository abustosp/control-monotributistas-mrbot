"""
Módulo de funciones auxiliares comunes
"""
import pandas as pd
from datetime import date, datetime
from typing import Optional, Dict, Any


def formatear_fecha(val: Any) -> str:
    """
    Formatea valores de fecha al formato DD/MM/YYYY.
    
    Args:
        val: Valor a formatear (puede ser fecha, string, etc.)
        
    Returns:
        str: Fecha formateada o cadena vacía si no es válida
    """
    if pd.isna(val):
        return ''
    if isinstance(val, (pd.Timestamp, datetime, date)):
        return val.strftime('%d/%m/%Y')
    parsed = pd.to_datetime(val, errors='coerce')
    if pd.isna(parsed):
        return str(val)
    return parsed.strftime('%d/%m/%Y')


def validar_credenciales(credenciales: Dict[str, Optional[str]]) -> bool:
    """
    Valida que todas las credenciales necesarias estén presentes.
    
    Args:
        credenciales: Diccionario con las credenciales a validar
        
    Returns:
        bool: True si todas las credenciales están presentes, False en caso contrario
    """
    return all(credenciales.values())


def normalizar_si_no(valor: Any) -> str:
    """
    Normaliza valores a 'si' o 'no'.
    
    Args:
        valor: Valor a normalizar
        
    Returns:
        str: 'si' o 'no'
    """
    return str(valor).lower().strip()


def construir_nombre_directorio(cuit: str, denominacion: str) -> str:
    """
    Construye el nombre del directorio para un contribuyente.
    
    Args:
        cuit: CUIT del contribuyente
        denominacion: Denominación del contribuyente
        
    Returns:
        str: Nombre del directorio
    """
    return f"{cuit}_{denominacion}"


def imprimir_separador(caracter: str = '=', longitud: int = 80) -> None:
    """
    Imprime un separador visual.
    
    Args:
        caracter: Caracter a usar para el separador
        longitud: Longitud del separador
    """
    print(f"\n{caracter * longitud}")


def imprimir_encabezado(titulo: str, subtitulo: Optional[str] = None) -> None:
    """
    Imprime un encabezado formateado.
    
    Args:
        titulo: Título principal
        subtitulo: Subtítulo opcional
    """
    imprimir_separador()
    print(titulo)
    if subtitulo:
        print(subtitulo)
    imprimir_separador()

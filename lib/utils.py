import json
import os
import re
import shutil
from typing import Any, Dict, Optional
from zipfile import ZipFile

import requests


def descargar_archivo(
    url: str,
    nombre_archivo: None | str = None,
    directorio_objetivo: str | None = None
) -> str:
    """
    Descarga un recurso binario via URL conservando el nombre sugerido por el servidor cuando sea posible.

    Args:
        url (str): URL desde donde se descarga el archivo.
        nombre_archivo (Optional[str]): nombre local en el que guardar el archivo.
        directorio_objetivo (Optional[str]): directorio donde guardar el archivo.

    Returns:
        str: Ruta completa del archivo descargado.
    """
    response = requests.get(url, stream=True)
    response.raise_for_status()

    filename = None
    cd = response.headers.get('content-disposition')

    if cd:
        m = re.search(r"filename\*?=(?:UTF-8''|\"?)([^\";]+)\"?", cd, flags=re.IGNORECASE)
        if m:
            filename = m.group(1)

    if not filename:
        from urllib.parse import unquote, urlparse
        path = urlparse(url).path
        filename = unquote(path.rsplit('/', 1)[-1]) or 'downloaded_file'

    save_as = nombre_archivo if nombre_archivo else filename
    
    if directorio_objetivo:
        os.makedirs(directorio_objetivo, exist_ok=True)
        save_as = os.path.join(directorio_objetivo, save_as)

    with open(save_as, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)

    print(f"Archivo guardado como: {save_as}")
    return save_as


def extraer_url_minio(response: Dict[str, Any], tipo: str) -> Optional[str]:
    """
    Extrae la URL de descarga alojada en MinIO para un tipo de comprobante.

    Args:
        response (Dict[str, Any]): JSON retornado por la API.
        tipo (str): `emitidos` o `recibidos`.

    Returns:
        Optional[str]: URL de descarga si está presente, de lo contrario `None`.
    """
    clave_directa = f"mis_comprobantes_{tipo}_url_minio"
    url = response.get(clave_directa)
    if url:
        return url

    nodo = response.get("descargas_minio", {}).get(tipo, [])
    if nodo:
        return nodo[0].get("url_descarga")

    return None


def extraccion_urls_minio(response: Dict[str, Any]) -> Dict[str, Optional[str]]:
    """
    Extrae las URLs de descarga alojadas en MinIO para emitidos y recibidos.

    Args:
        response (Dict[str, Any]): JSON retornado por la API.

    Returns:
        Dict[str, Optional[str]]: Diccionario con URLs de emitidos y recibidos.
    """
    minio_mce = None
    minio_mcr = None

    if isinstance(response, dict):
        minio_mce = response.get('mis_comprobantes_emitidos_url_minio') or None
        minio_mcr = response.get('mis_comprobantes_recibidos_url_minio') or None

        if not minio_mce:
            try:
                minio_mce = response.get('descargas_minio', {}).get('emitidos', [])[0].get('url_descarga')
            except Exception:
                minio_mce = None
        if not minio_mcr:
            try:
                minio_mcr = response.get('descargas_minio', {}).get('recibidos', [])[0].get('url_descarga')
            except Exception:
                minio_mcr = None

    if not minio_mce:
        print("No se encontró URL para emitidos en la respuesta")
    if not minio_mcr:
        print("No se encontró URL para recibidos en la respuesta")

    return {"emitidos": minio_mce, "recibidos": minio_mcr}


def guardar_json(
    datos: Dict[str, Any],
    ruta_base: str,
    extension_actual: str = ".pdf"
) -> None:
    """
    Guarda un diccionario como archivo JSON.

    Args:
        datos (Dict[str, Any]): Diccionario con los datos a guardar.
        ruta_base (str): Ruta del archivo base (se cambiará la extensión).
        extension_actual (str): Extensión actual del archivo base.
    """
    ruta_json = os.path.splitext(ruta_base)[0] + ".json"
    
    with open(ruta_json, "w", encoding="utf-8") as file:
        json.dump(datos, file, indent=2, ensure_ascii=False)
    
    print(f"JSON guardado como: {ruta_json}")


def extraer_zip(
    ruta_zip: str,
    directorio_destino: str,
) -> None:
    """
    Extrae el contenido del ZIP en el directorio destino especificado.

    Args:
        ruta_zip (str): Ruta al archivo ZIP.
        directorio_destino (str): Directorio donde se extraerán los archivos.
    """
    with ZipFile(ruta_zip, 'r') as zip_ref:
        primer_archivo = zip_ref.namelist()[0]
        nombre_zip = os.path.basename(ruta_zip)
        
        cuit_archivo = primer_archivo.split('_')[5] if primer_archivo else 'desconocido'
        cuit_nombre_zip = nombre_zip.split('-')[4].strip() if nombre_zip else 'desconocido'
        
        if cuit_archivo != cuit_nombre_zip:
            print(f"Advertencia: El CUIT en el nombre del archivo ({cuit_nombre_zip}) no coincide con el CUIT en el contenido ({cuit_archivo}).")
            
        else:
            if cuit_archivo == cuit_nombre_zip:
                zip_ref.extractall(directorio_destino)
                
                for archivo in zip_ref.namelist():
                    ruta_origen = os.path.join(directorio_destino, archivo)
                    ruta_destino = os.path.join(directorio_destino, nombre_zip.replace('.zip', '.csv'))
                    shutil.move(ruta_origen, ruta_destino)
                    print(f"Archivo extraído y renombrado a: {ruta_destino}")
                
            else:
                print("No se extrajo el archivo debido a la discrepancia en el CUIT.")


if __name__ == "__main__":
    ruta_zip_ejemplo = "descargas_mis_comprobantes/9 - MCE - 01012025 - 31122025 - 20374730429 - BUSTOS PIASENTINI AGUSTIN.zip"
    ruta_zip_ejemplo2 = "descargas_mis_comprobantes/9 - MCR - 01012025 - 31122025 - 20374730429 - BUSTOS PIASENTINI AGUSTIN.zip"
    
    directorio_destino_ejemplo = "descargas_mis_comprobantes/extracciones"
    
    extraer_zip(ruta_zip_ejemplo, directorio_destino_ejemplo)
    extraer_zip(ruta_zip_ejemplo2, directorio_destino_ejemplo)

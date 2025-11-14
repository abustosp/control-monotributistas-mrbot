import json
import os
import re
from typing import Any, Dict, Iterable, List

import requests
from dotenv import load_dotenv


def consulta_rcel(
    mrbot_user: str,
    mrbot_api_key: str,
    base_url: str,
    rcel_endpoint: str,
    desde: str = "01/01/2024",
    hasta: str = "31/12/2024",
    cuit_inicio_sesion: str = "20123456780",
    representado_nombre: str = "Empresa Ejemplo S.A.",
    representado_cuit: str = "30876543210",
    contrasena: str = "mi_contraseña_secreta",
    b64_pdf: bool = False,
    minio_upload: bool = True,
) -> Dict[str, Any]:
    """
    Ejecuta la consulta de facturas emitidas por el representado desde la API de Mrbot para RCEL.

    Args:
        mrbot_user (str): email que identifica al usuario del cliente.
        mrbot_api_key (str): API key asociada al usuario.
        base_url (str): URL base de Mrbot.
        mis_comprobantes_endpoint (str): endpoint para `mis_comprobantes`.
        desde (str): fecha inicial del rango a consultar.
        hasta (str): fecha final del rango a consultar.
        cuit_inicio_sesion (str): CUIT utilizado para iniciar sesión.
        representado_nombre (str): nombre del representado.
        representado_cuit (str): CUIT del representado.
        contrasena (str): contraseña del representado.
        b64_pdf (bool): solicitar el PDF en base64.
        minio_upload (bool): solicitar carga a MinIO.

    Returns:
        Dict[str, Any]: JSON retornado por la API con los datos de facturas.
    """

    url = f"{base_url.rstrip('/')}/{rcel_endpoint.lstrip('/')}/consulta"

    payload = json.dumps({
        "desde": desde,
        "hasta": hasta,
        "cuit_representante": cuit_inicio_sesion,
        "nombre_rcel": representado_nombre,
        "representado_cuit": representado_cuit,
        "clave": contrasena,
        "b64_pdf": b64_pdf,
        "minio_upload": minio_upload,
    })

    headers = {
        "x-api-key": mrbot_api_key,
        "email": mrbot_user,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    response = requests.post(url, headers=headers, data=payload)
    try:
        parsed = response.json()
    except ValueError:
        response.raise_for_status()
        raise

    print(response.text)
    return parsed


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
    # Descargar en streaming y determinar nombre sugerido por el servidor (Content-Disposition)
    response = requests.get(url, stream=True)
    response.raise_for_status()

    # Intentar obtener filename desde Content-Disposition
    filename = None
    cd = response.headers.get('content-disposition')

    # soporta: filename="name.ext"  y filename*=UTF-8''name.ext
    if cd:
        m = re.search(r"filename\*?=(?:UTF-8''|\"?)([^\";]+)\"?", cd, flags=re.IGNORECASE)
        if m:
            filename = m.group(1)

    # Si no hay header o no se pudo extraer, extraer desde la URL (y decodificar)
    if not filename:
        from urllib.parse import unquote, urlparse
        path = urlparse(url).path
        filename = unquote(path.rsplit('/', 1)[-1]) or 'downloaded_file'

    # Si se pasó un nombre explícito, respetarlo; si no, usar el sugerido
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


def validar_respuesta_rcel(response: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Asegura que la respuesta indica éxito y retorna el listado de facturas emitidas.

    Si la API devuelve éxito falso, levanta un RuntimeError con los mensajes de error recibidos.
    """

    # Caso éxito
    if response.get("success"):
        # Ajustá esta clave si tu API la nombra distinto
        return response.get("facturas_emitidas", [])

    detail = response.get("detail")

    mensajes: List[str] = []
    error_code = None

    # detail como dict {"message": "...", "error_code": "...", ...}
    if isinstance(detail, dict):
        posibles_claves_msg = ("message", "msg", "detail")
        for clave in posibles_claves_msg:
            val = detail.get(clave)
            if isinstance(val, str):
                mensajes.append(val)
            elif isinstance(val, list):
                mensajes.extend(str(v) for v in val)

        error_code = detail.get("error_code") or detail.get("type")

    # detail como lista de dicts (típico error de validación de FastAPI/Pydantic)
    elif isinstance(detail, list):
        for item in detail:
            if not isinstance(item, dict):
                continue
            msg = item.get("message") or item.get("msg") or item.get("detail")
            if msg:
                mensajes.append(str(msg))
            if not error_code:
                error_code = item.get("error_code") or item.get("type")

    # detail como string plano
    elif isinstance(detail, str):
        mensajes.append(detail)

    # Fallback: tomar mensaje de nivel raíz si no se juntó nada
    if not mensajes:
        top_msg = response.get("message") or response.get("detail")
        if isinstance(top_msg, str):
            mensajes.append(top_msg)

    mensaje_base = " | ".join(mensajes) if mensajes else "Respuesta sin detalles."
    codigo = f" ({error_code})" if error_code else ""

    raise RuntimeError(f"Consulta RCEL fallida{codigo}: {mensaje_base}")


def iter_urls_facturas(facturas: Iterable[Dict[str, Any]]) -> Iterable[str]:
    """Devuelve las URLs que contienen `URL_MINIO` dentro de las facturas retornadas."""

    for factura in facturas:
        url = factura.get("URL_MINIO")
        if url:
            yield url


def guardar_json_factura(
    factura: Dict[str, Any],
    ruta_pdf: str
) -> None:
    """
    Guarda el diccionario de una factura como archivo JSON.

    Args:
        factura (Dict[str, Any]): Diccionario con los datos de la factura.
        ruta_pdf (str): Ruta del archivo PDF descargado.
    """
    # Cambiar extensión de .pdf a .json
    ruta_json = os.path.splitext(ruta_pdf)[0] + ".json"
    
    with open(ruta_json, "w", encoding="utf-8") as file:
        json.dump(factura, file, indent=2, ensure_ascii=False)
    
    print(f"JSON guardado como: {ruta_json}")


def main() -> None:
    load_dotenv()

    mrbot_user = os.getenv("MRBOT_USER")
    mrbot_api_key = os.getenv("MRBOT_API_KEY")
    base_url = os.getenv("BASE_URL")
    rcel_endpoint = os.getenv("RCEL_ENDPOINT")
    desde = os.getenv("RCEL_DESDE_EJEMPLO")
    hasta = os.getenv("RCEL_HASTA_EJEMPLO")
    cuit_inicio_sesion = os.getenv("CUIT_REPRESENTADO_EJEMPLO")
    representado_nombre = os.getenv("RCEL_DENOMINACION_EJEMPLO")
    representado_cuit = os.getenv("CUIT_REPRESENTANTE_EJEMPLO")
    contrasena = os.getenv("CLAVE_REPRESENTANTE_EJEMPLO")

    assert mrbot_user and mrbot_api_key and base_url and rcel_endpoint, "Faltan credenciales obligatorias"

    response = consulta_rcel(
        mrbot_user=mrbot_user,
        mrbot_api_key=mrbot_api_key,
        base_url=base_url,
        rcel_endpoint=rcel_endpoint,
        desde=desde,
        hasta=hasta,
        cuit_inicio_sesion=cuit_inicio_sesion,
        representado_nombre=representado_nombre,
        representado_cuit=representado_cuit,
        contrasena=contrasena,
    )

    try:
        facturas = validar_respuesta_rcel(response)
    except RuntimeError as exc:
        print(str(exc))
        return

    if not facturas:
        print("La consulta RCEL no devolvió facturas.")
        return

    directorio_objetivo = f"descargas_rcel/{representado_cuit}"

    # Procesar cada factura: descargar PDF y guardar JSON
    for factura in facturas:
        url_pdf = factura.get("URL_MINIO")
        if url_pdf:
            # Descargar PDF
            ruta_pdf = descargar_archivo(url_pdf, directorio_objetivo=directorio_objetivo)
            # Guardar JSON con los datos de la factura
            guardar_json_factura(factura, ruta_pdf)
        else:
            print(f"Factura sin URL_MINIO: {factura.get('NUMERO_FACTURA', 'N/A')}")


if __name__ == "__main__":
    main()

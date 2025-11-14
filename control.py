import tkinter as tk
from lib.caller_mc import consulta_mis_comprobantes
from lib.caller_rcel import consulta_rcel, validar_respuesta_rcel
from lib.utils import descargar_archivo, extraccion_urls_minio, extraer_zip, guardar_json
from dotenv import load_dotenv
import os
import pandas as pd
from datetime import date, datetime

load_dotenv()


def _fmt_fecha(val):
    """Formatea valores de fecha al formato DD/MM/YYYY."""
    if pd.isna(val):
        return ''
    if isinstance(val, (pd.Timestamp, datetime, date)):
        return val.strftime('%d/%m/%Y')
    parsed = pd.to_datetime(val, errors='coerce')
    if pd.isna(parsed):
        return str(val)
    return parsed.strftime('%d/%m/%Y')


def procesar_descarga_mc(row, mrbot_user, mrbot_api_key, base_url, mis_comprobantes_endpoint, downloads_mc_path):
    """
    Procesa la descarga de Mis Comprobantes para un contribuyente.
    
    Args:
        row: Fila del DataFrame con los datos del contribuyente
        mrbot_user: Usuario de Mrbot
        mrbot_api_key: API key de Mrbot
        base_url: URL base de la API
        mis_comprobantes_endpoint: Endpoint de Mis Comprobantes
        downloads_mc_path: Directorio de descargas
    """
    cuit_representante = str(row['CUIT_Representante'])
    clave_representante = row['Clave_representante']
    cuit_representado = str(row['CUIT_Representado'])
    desde = _fmt_fecha(row['Desde_MC'])
    hasta = _fmt_fecha(row['Hasta_MC'])
    denominacion_mc = row['Denominacion_MC']
    descarga_MC = str(row['Descarga_MC']).lower().strip()
    descarga_MC_emitidos = str(row['Descarga_MC_emitidos']).lower().strip()
    descarga_MC_recibidos = str(row['Descarga_MC_recibidos']).lower().strip()

    if descarga_MC != 'si':
        print(f"Saltando descarga MC para CUIT {cuit_representado} - Descarga_MC: {descarga_MC}")
        return
    
    print(f"\n{'='*80}")
    print(f"Procesando MC: {denominacion_mc} - CUIT: {cuit_representado}")
    print(f"Desde {desde} hasta {hasta}")
    print(f"Emitidos: {descarga_MC_emitidos} | Recibidos: {descarga_MC_recibidos}")
    print(f"{'='*80}\n")

    # Determinar qué descargar
    descargar_emitidos = descarga_MC_emitidos == 'si'
    descargar_recibidos = descarga_MC_recibidos == 'si'

    if not descargar_emitidos and not descargar_recibidos:
        print(f"No hay nada que descargar para {cuit_representado}")
        return

    try:
        # Consultar API
        response = consulta_mis_comprobantes(
            mrbot_user=mrbot_user,
            mrbot_api_key=mrbot_api_key,
            base_url=base_url,
            mis_comprobantes_endpoint=mis_comprobantes_endpoint,
            desde=desde,
            hasta=hasta,
            cuit_inicio_sesion=cuit_representante,
            representado_nombre=denominacion_mc,
            representado_cuit=cuit_representado,
            contrasena=clave_representante,
            descarga_emitidos=descargar_emitidos,
            descarga_recibidos=descargar_recibidos,
        )

        # Extraer URLs de MinIO
        urls = extraccion_urls_minio(response)

        # Crear directorio del contribuyente
        directorio_contribuyente = os.path.join(downloads_mc_path, f"{cuit_representado}_{denominacion_mc}")
        directorio_extraido = os.path.join(directorio_contribuyente, "extraido")
        os.makedirs(directorio_contribuyente, exist_ok=True)
        os.makedirs(directorio_extraido, exist_ok=True)

        # Descargar archivos
        archivos_descargados = []
        
        if descargar_emitidos and urls.get('emitidos'):
            print(f"\nDescargando emitidos...")
            archivo_emitidos = descargar_archivo(
                urls['emitidos'],
                None,
                directorio_contribuyente
            )
            archivos_descargados.append(archivo_emitidos)
        
        if descargar_recibidos and urls.get('recibidos'):
            print(f"\nDescargando recibidos...")
            archivo_recibidos = descargar_archivo(
                urls['recibidos'],
                None,
                directorio_contribuyente
            )
            archivos_descargados.append(archivo_recibidos)

        # Extraer ZIPs
        for archivo_zip in archivos_descargados:
            if archivo_zip and archivo_zip.endswith('.zip'):
                print(f"\nExtrayendo: {archivo_zip}")
                try:
                    extraer_zip(archivo_zip, directorio_extraido)
                except Exception as e:
                    print(f"Error al extraer {archivo_zip}: {e}")

        print(f"\n✓ Proceso MC completado para {denominacion_mc}")

    except Exception as e:
        print(f"\n✗ Error procesando MC {denominacion_mc} (CUIT: {cuit_representado}): {e}")


def procesar_descarga_rcel(row, mrbot_user, mrbot_api_key, base_url, rcel_endpoint, downloads_rcel_path):
    """
    Procesa la descarga de RCEL para un contribuyente.
    
    Args:
        row: Fila del DataFrame con los datos del contribuyente
        mrbot_user: Usuario de Mrbot
        mrbot_api_key: API key de Mrbot
        base_url: URL base de la API
        rcel_endpoint: Endpoint de RCEL
        downloads_rcel_path: Directorio de descargas
    """
    cuit_representante = str(row['CUIT_Representante'])
    clave_representante = row['Clave_representante']
    cuit_representado = str(row['CUIT_Representado'])
    desde = _fmt_fecha(row['Desde_RCEL'])
    hasta = _fmt_fecha(row['Hasta_RCEL'])
    denominacion_rcel = row['Denominacion_RCEL']
    descarga_RCEL = str(row['Descarga_RCEL']).lower().strip()

    if descarga_RCEL != 'si':
        print(f"Saltando descarga RCEL para CUIT {cuit_representado} - Descarga_RCEL: {descarga_RCEL}")
        return
    
    print(f"\n{'='*80}")
    print(f"Procesando RCEL: {denominacion_rcel} - CUIT: {cuit_representado}")
    print(f"Desde {desde} hasta {hasta}")
    print(f"{'='*80}\n")

    try:
        # Consultar API
        response = consulta_rcel(
            mrbot_user=mrbot_user,
            mrbot_api_key=mrbot_api_key,
            base_url=base_url,
            rcel_endpoint=rcel_endpoint,
            desde=desde,
            hasta=hasta,
            cuit_inicio_sesion=cuit_representante,
            representado_nombre=denominacion_rcel,
            representado_cuit=cuit_representado,
            contrasena=clave_representante,
        )

        # Validar respuesta
        facturas = validar_respuesta_rcel(response)

        if not facturas:
            print(f"No se encontraron facturas RCEL para {denominacion_rcel}")
            return

        # Crear directorio del contribuyente
        directorio_contribuyente = os.path.join(downloads_rcel_path, f"{cuit_representado}_{denominacion_rcel}")
        os.makedirs(directorio_contribuyente, exist_ok=True)

        # Descargar archivos
        print(f"\nDescargando {len(facturas)} facturas...")
        for factura in facturas:
            url_pdf = factura.get("URL_MINIO")
            if url_pdf:
                try:
                    ruta_descargada = descargar_archivo(
                        url_pdf,
                        None,
                        directorio_contribuyente
                    )
                    # Guardar metadata JSON
                    guardar_json(factura, ruta_descargada)
                except Exception as e:
                    print(f"Error descargando factura {factura.get('NUMERO_FACTURA', 'N/A')}: {e}")
            else:
                print(f"Factura sin URL_MINIO: {factura.get('NUMERO_FACTURA', 'N/A')}")

        print(f"\n✓ Proceso RCEL completado para {denominacion_rcel}")

    except Exception as e:
        print(f"\n✗ Error procesando RCEL {denominacion_rcel} (CUIT: {cuit_representado}): {e}")


if __name__ == "__main__":
    archivo_base = "planilla-control-monotributistas.xlsx"
    df = pd.read_excel(archivo_base)

    print(df.head())

    mrbot_user = os.getenv("MRBOT_USER")
    mrbot_api_key = os.getenv("MRBOT_API_KEY")
    base_url = os.getenv("BASE_URL")
    mis_comprobantes_endpoint = os.getenv("MIS_COMPROBANTES_ENDPOINT")
    rcel_endpoint = os.getenv("RCEL_ENDPOINT")
    downloads_mc_path = os.getenv("DOWNLOADS_MC_PATH", "descargas_mis_comprobantes")
    downloads_rcel_path = os.getenv("DOWNLOADS_RCEL_PATH", "descargas_rcel")

    # Procesar cada fila
    for index, row in df.iterrows():
        # Procesar Mis Comprobantes
        procesar_descarga_mc(row, mrbot_user, mrbot_api_key, base_url, mis_comprobantes_endpoint, downloads_mc_path)
        
        # Procesar RCEL
        procesar_descarga_rcel(row, mrbot_user, mrbot_api_key, base_url, rcel_endpoint, downloads_rcel_path)
        
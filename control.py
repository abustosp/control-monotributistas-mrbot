import tkinter as tk
from lib.caller_mc import consulta_mis_comprobantes
from lib.utils import descargar_archivo, extraccion_urls_minio, extraer_zip
from dotenv import load_dotenv
import os
import pandas as pd
from datetime import date, datetime

load_dotenv()

archivo_base = "planilla-control-monotributistas.xlsx"

df = pd.read_excel(archivo_base,)

print(df.head())

mrbot_user = os.getenv("MRBOT_USER")
mrbot_api_key = os.getenv("MRBOT_API_KEY")
base_url = os.getenv("BASE_URL")
mis_comprobantes_endpoint = os.getenv("MIS_COMPROBANTES_ENDPOINT")
downloads_mc_path = os.getenv("DOWNLOADS_MC_PATH", "descargas_mis_comprobantes")

# Descarga MC
for index, row in df.iterrows():
    cuit_representante = str(row['CUIT_Representante'])
    clave_representante = row['Clave_representante']
    cuit_representado = str(row['CUIT_Representado'])
    def _fmt_fecha(val):
        if pd.isna(val):
            return ''
        if isinstance(val, (pd.Timestamp, datetime, date)):
            return val.strftime('%d/%m/%Y')
        parsed = pd.to_datetime(val, errors='coerce')
        if pd.isna(parsed):
            return str(val)
        return parsed.strftime('%d/%m/%Y')

    desde = _fmt_fecha(row['Desde_MC'])
    hasta = _fmt_fecha(row['Hasta_MC'])
    denominacion_mc = row['Denominacion_MC']
    descarga_MC = str(row['Descarga_MC']).lower().strip()
    descarga_MC_emitidos = str(row['Descarga_MC_emitidos']).lower().strip()
    descarga_MC_recibidos = str(row['Descarga_MC_recibidos']).lower().strip()

    if descarga_MC != 'si':
        print(f"Saltando descarga para CUIT {cuit_representado} - Descarga_MC: {descarga_MC}")
        continue
    
    print(f"\n{'='*80}")
    print(f"Procesando: {denominacion_mc} - CUIT: {cuit_representado}")
    print(f"Desde {desde} hasta {hasta}")
    print(f"Emitidos: {descarga_MC_emitidos} | Recibidos: {descarga_MC_recibidos}")
    print(f"{'='*80}\n")

    # Determinar qué descargar
    descargar_emitidos = descarga_MC_emitidos == 'si'
    descargar_recibidos = descarga_MC_recibidos == 'si'

    if not descargar_emitidos and not descargar_recibidos:
        print(f"No hay nada que descargar para {cuit_representado}")
        continue

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

        print(f"\n✓ Proceso completado para {denominacion_mc}")

    except Exception as e:
        print(f"\n✗ Error procesando {denominacion_mc} (CUIT: {cuit_representado}): {e}")
        
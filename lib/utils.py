from zipfile import ZipFile
import os
import shutil

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
        # Obtener el nombre del primer archivo para mostrarlo
        primer_archivo = zip_ref.namelist()[0]
        # Obtener el nombre del ZIP sin la ruta
        nombre_zip = os.path.basename(ruta_zip)
        
        cuit_archivo = primer_archivo.split('_')[5] if primer_archivo else 'desconocido'
        cuit_nombre_zip = nombre_zip.split('-')[4].strip() if nombre_zip else 'desconocido'
        
        if cuit_archivo != cuit_nombre_zip:
            print(f"Advertencia: El CUIT en el nombre del archivo ({cuit_nombre_zip}) no coincide con el CUIT en el contenido ({cuit_archivo}).")
            
        else:
            if cuit_archivo == cuit_nombre_zip:
                # Extraer el archivo ZIP pero con el nombre_zip
                zip_ref.extractall(directorio_destino)
                
                # renombrar los archivos extraidos al mismo del del ZIP
                for archivo in zip_ref.namelist():
                    ruta_origen = os.path.join(directorio_destino, archivo)
                    ruta_destino = os.path.join(directorio_destino, nombre_zip.replace('.zip', '.csv'))
                    shutil.move(ruta_origen, ruta_destino)
                    print(f"Archivo extraído y renombrado a: {ruta_destino}")
                
            else:
                print("No se extrajo el archivo debido a la discrepancia en el CUIT.")
            
            
if __name__ == "__main__":
    # Ejemplo de uso
    ruta_zip_ejemplo = "descargas_mis_comprobantes/9 - MCE - 01012025 - 31122025 - 20374730429 - BUSTOS PIASENTINI AGUSTIN.zip"
    ruta_zip_ejemplo2 = "descargas_mis_comprobantes/9 - MCR - 01012025 - 31122025 - 20374730429 - BUSTOS PIASENTINI AGUSTIN.zip"
    
    directorio_destino_ejemplo = "descargas_mis_comprobantes/extracciones"
    
    extraer_zip(ruta_zip_ejemplo, directorio_destino_ejemplo)
    extraer_zip(ruta_zip_ejemplo2, directorio_destino_ejemplo)
            
            
            
"""
Script de comparación de rendimiento entre versión original y optimizada
"""
import time
import glob
import pandas as pd
import numpy as np
import os
import json


def test_lectura_csv_original(archivos_mc):
    """Simula la lectura original (concatenación incremental)"""
    consolidado = pd.DataFrame()
    
    for f in archivos_mc:
        if not os.path.isfile(f):
            continue
        
        data = pd.read_csv(f, sep=';', decimal=',', encoding='utf-8-sig')
        
        if len(data) == 0:
            continue
        
        data['Archivo'] = f.split("/")[-1]
        partes_archivo = data["Archivo"].str.split("-")
        data['Fin CUIT'] = partes_archivo.str[4].str.strip().astype(np.int64)
        data['CUIT Cliente'] = partes_archivo.str[4].str.strip().astype(np.int64)
        data['Cliente'] = partes_archivo.str[5].str.strip().str.replace('.csv','', regex=True)
        
        es_emitido = 'Denominación Receptor' in data.columns
        es_recibido = 'Denominación Emisor' in data.columns
        
        if es_emitido:
            data['Nro. Doc. Receptor/Emisor'] = data['Nro. Doc. Receptor']
            data['Denominación Receptor/Emisor'] = data['Denominación Receptor']
        elif es_recibido:
            data['Nro. Doc. Receptor/Emisor'] = data['Nro. Doc. Emisor']
            data['Denominación Receptor/Emisor'] = data['Denominación Emisor']
        
        columnas_necesarias = [
            'Fecha de Emisión', 'Tipo de Comprobante', 'Punto de Venta', 
            'Número Desde', 'Número Hasta', 'Cód. Autorización',
            'Tipo Cambio', 'Moneda', 
            'Imp. Neto Gravado Total', 'Imp. Neto No Gravado', 
            'Imp. Op. Exentas', 'Otros Tributos', 'Total IVA', 'Imp. Total',
            'Nro. Doc. Receptor/Emisor', 'Denominación Receptor/Emisor',
            'Archivo', 'CUIT Cliente', 'Fin CUIT', 'Cliente'
        ]
        data = data[columnas_necesarias]
        
        # Concatenación incremental (ineficiente)
        consolidado = pd.concat([consolidado, data], ignore_index=True)
    
    return consolidado


def test_lectura_json_original(archivos_json):
    """Simula la lectura original de JSON (concatenación incremental)"""
    Info_Facturas_PDF = pd.DataFrame()
    
    for factura in archivos_json:
        if not os.path.isfile(factura):
            continue
        
        try:
            with open(factura, 'r', encoding='utf-8-sig') as f:
                data_dict = json.load(f)
            
            data_pdf = pd.DataFrame([data_dict])
            
            if len(data_pdf) > 0:
                data_pdf['Archivo PDF'] = factura.split("/")[-1]
                partes = data_pdf["Archivo PDF"].str.split("-")
                data_pdf['CUIT Cliente'] = partes.str[0].str.strip().astype(np.int64)
                data_pdf['Fin CUIT'] = partes.str[0].str.strip().astype(np.int64)
                
                directorio_padre = factura.split("/")[-2]
                cliente = directorio_padre.split("_", 1)[1] if "_" in directorio_padre else directorio_padre
                data_pdf['Cliente'] = cliente
                
                # Concatenación incremental (ineficiente)
                Info_Facturas_PDF = pd.concat([Info_Facturas_PDF, data_pdf], ignore_index=True)
        except Exception as e:
            continue
    
    return Info_Facturas_PDF


def comparar_rendimiento():
    """Compara el rendimiento de ambas versiones"""
    from control import leer_archivos_csv_batch, leer_archivos_json_batch
    
    print("="*80)
    print("COMPARACIÓN DE RENDIMIENTO - LECTURA DE ARCHIVOS")
    print("="*80)
    
    # Test CSV
    archivos_mc = glob.glob('descargas_mis_comprobantes/**/extraido/*.csv', recursive=True)
    print(f"\n📊 Test con {len(archivos_mc)} archivos CSV")
    
    if archivos_mc:
        # Versión original
        start = time.time()
        df_original = test_lectura_csv_original(archivos_mc)
        tiempo_original = time.time() - start
        
        # Versión optimizada
        start = time.time()
        df_optimizado = leer_archivos_csv_batch(archivos_mc)
        tiempo_optimizado = time.time() - start
        
        mejora_csv = ((tiempo_original - tiempo_optimizado) / tiempo_original) * 100
        
        print(f"\n📄 Resultados CSV:")
        print(f"  • Método Original:   {tiempo_original:.4f} segundos")
        print(f"  • Método Optimizado: {tiempo_optimizado:.4f} segundos")
        print(f"  • Mejora:            {mejora_csv:.1f}%")
        print(f"  • Registros:         {len(df_original)} (original) vs {len(df_optimizado)} (optimizado)")
    
    # Test JSON
    archivos_json = glob.glob('descargas_rcel/**/*.json', recursive=True)
    print(f"\n📊 Test con {len(archivos_json)} archivos JSON")
    
    if archivos_json:
        # Versión original
        start = time.time()
        df_original_json = test_lectura_json_original(archivos_json)
        tiempo_original_json = time.time() - start
        
        # Versión optimizada
        start = time.time()
        df_optimizado_json = leer_archivos_json_batch(archivos_json)
        tiempo_optimizado_json = time.time() - start
        
        mejora_json = ((tiempo_original_json - tiempo_optimizado_json) / tiempo_original_json) * 100
        
        print(f"\n📄 Resultados JSON:")
        print(f"  • Método Original:   {tiempo_original_json:.4f} segundos")
        print(f"  • Método Optimizado: {tiempo_optimizado_json:.4f} segundos")
        print(f"  • Mejora:            {mejora_json:.1f}%")
        print(f"  • Registros:         {len(df_original_json)} (original) vs {len(df_optimizado_json)} (optimizado)")
    
    print("\n" + "="*80)
    print("RESUMEN")
    print("="*80)
    
    if archivos_mc:
        print(f"✅ CSV:  {mejora_csv:.1f}% más rápido ({tiempo_original:.3f}s → {tiempo_optimizado:.3f}s)")
    if archivos_json:
        print(f"✅ JSON: {mejora_json:.1f}% más rápido ({tiempo_original_json:.3f}s → {tiempo_optimizado_json:.3f}s)")
    
    print("\n💡 Nota: Las mejoras son más significativas con mayor cantidad de archivos")
    print("="*80 + "\n")


if __name__ == "__main__":
    comparar_rendimiento()

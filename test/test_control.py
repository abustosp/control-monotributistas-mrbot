#!/usr/bin/env python3
"""Script de prueba para la función control"""

import glob
from control import control

# Buscar archivos de ejemplo en las carpetas de descargas
archivos_mc = glob.glob("descargas_mis_comprobantes/**/extraido/*.csv", recursive=True)
archivos_PDF = []  # No se usan PDF en este caso
archivos_PDF_JSON = glob.glob("descargas_rcel/**/*.json", recursive=True)

print("=" * 80)
print("PRUEBA DE LA FUNCIÓN CONTROL")
print("=" * 80)
print(f"\nArchivos MC encontrados: {len(archivos_mc)}")
for f in archivos_mc:
    print(f"  - {f}")

print(f"\nArchivos JSON encontrados: {len(archivos_PDF_JSON)}")
print(f"  (mostrando primeros 5)")
for f in archivos_PDF_JSON[:5]:
    print(f"  - {f}")

print("\n" + "=" * 80)
print("EJECUTANDO FUNCIÓN CONTROL...")
print("=" * 80 + "\n")

# Ejecutar la función
control(archivos_mc, archivos_PDF, archivos_PDF_JSON)

print("\n" + "=" * 80)
print("PRUEBA COMPLETADA")
print("=" * 80)

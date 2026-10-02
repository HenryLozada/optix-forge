"""
Optix Forge // Build Script
Compilación del proyecto a ejecutable portable (.exe) para Windows con PyInstaller.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def build_executable():
    print("===================================================")
    print("  OPTIX FORGE // PyInstaller Build Engine")
    print("===================================================")

    gui_dir = BASE_DIR / "gui"
    data_dir = BASE_DIR / "data"

    add_data_args = [
        f"--add-data={gui_dir};gui",
        f"--add-data={data_dir};data"
    ]

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name=OptixForge",
        *add_data_args,
        str(BASE_DIR / "main.py")
    ]

    print("Ejecutando PyInstaller con el siguiente comando:")
    print(" ".join(cmd))
    
    result = subprocess.run(cmd, cwd=str(BASE_DIR))
    
    if result.returncode == 0:
        print("\n[ÉXITO] Compilación completada con éxito.")
        print(f"Ejecutable disponible en: {BASE_DIR / 'dist' / 'OptixForge' / 'OptixForge.exe'}")
    else:
        print("\n[ERROR] La compilación falló. Código de salida:", result.returncode)

if __name__ == "__main__":
    build_executable()

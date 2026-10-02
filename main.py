"""
Optix Forge // Engine & FOV / Ultrawide Tweaker
Suite de optimización gráfica, FOV dinámico y relación de aspecto para PC.
Diseño NVIDIA Power Green & Interfaz de Alto Impacto.
"""

import os
import sys
import subprocess
import webview
from pathlib import Path
from typing import Dict, Any, Optional

# Configurar directorio base
BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
sys.path.insert(0, str(BASE_DIR))

from core.drive_scanner import DriveScanner
from core.game_scanner import GameScanner
from core.engine_detector import EngineDetector
from core.tweak_matrix import TweakMatrix
from core.backup_manager import BackupManager

class OptixForgeApi:
    def __init__(self):
        self.game_scanner = GameScanner()
        self._window = None

    def set_window(self, window):
        self._window = window

    # 1. Detección de Discos y Unidades
    def get_drives(self):
        """Retorna todas las unidades de almacenamiento disponibles (C:, D:, etc.)."""
        try:
            return {"success": True, "drives": DriveScanner.get_available_drives()}
        except Exception as e:
            return {"success": False, "error": str(e), "drives": []}

    # 2. Escaneo de Juegos
    def scan_games(self, target_drive: Optional[str] = None):
        """Escanea todos los juegos en el disco especificado o en todos los discos."""
        try:
            games = self.game_scanner.scan_games(target_drive=target_drive)
            # Enriquecer cada juego con detección de motor y configuración
            enriched = []
            for g in games:
                engine_info = EngineDetector.detect_engine_and_configs(g["name"], g["install_path"])
                g["engine_type"] = engine_info["engine"]
                g["has_config"] = engine_info["has_config"]
                g["primary_config"] = engine_info["primary_config"]
                g["supported_features"] = engine_info["supported_features"]
                g["is_restorable"] = BackupManager.has_backup(engine_info["primary_config"]) if engine_info["primary_config"] else False
                enriched.append(g)

            return {
                "success": True,
                "total_games": len(enriched),
                "games": enriched
            }
        except Exception as e:
            return {"success": False, "error": str(e), "games": []}

    # 3. Estado de Tweaks para un Juego
    def get_game_status(self, config_path: str):
        """Obtiene los valores actuales de FOV, filtros y ultrawide en la configuración."""
        try:
            status = TweakMatrix.get_game_tweak_status(config_path)
            return {"success": True, "status": status}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # 4. Aplicar Tweaks (con Respaldo .bak Automático)
    def apply_tweaks(self, config_path: str, options: Dict[str, Any]):
        """Aplica las optimizaciones solicitadas con copia de seguridad garantizada."""
        try:
            res = TweakMatrix.apply_tweaks(config_path, options)
            return res
        except Exception as e:
            return {"success": False, "error": str(e)}

    # 5. Botón de Restaurar a Fábrica (.bak)
    def restore_factory(self, config_path: str):
        """Restaura la configuración original de fábrica a partir del respaldo inmutable .bak."""
        try:
            res = BackupManager.restore_original(config_path)
            return res
        except Exception as e:
            return {"success": False, "error": str(e)}

    # 6. Selector de Directorio Manual
    def select_folder(self):
        """Abre el diálogo nativo de Windows para añadir una carpeta personalizada."""
        try:
            if self._window:
                res = self._window.create_file_dialog(webview.FOLDER_DIALOG)
                if res and len(res) > 0:
                    chosen = res[0]
                    self.game_scanner.add_custom_path(chosen)
                    return {"success": True, "path": chosen}
            return {"success": False, "error": "Operación cancelada"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # 6b. Selector de Archivo de Configuración Manual
    def select_config_file(self, game_name: str, install_path: str):
        """Abre un diálogo nativo para vincular manualmente un archivo .ini / .xml / .cfg a un título."""
        try:
            if self._window:
                file_types = ('Archivos de Configuración (*.ini;*.xml;*.cfg;*.config)', 'Todos los archivos (*.*)')
                res = self._window.create_file_dialog(webview.OPEN_DIALOG, file_types=file_types)
                if res and len(res) > 0:
                    chosen = res[0]
                    import re
                    name_clean = re.sub(r"[^a-zA-Z0-9]", "", game_name).lower()
                    inst_clean = re.sub(r"[^a-zA-Z0-9]", "", Path(install_path).name).lower()
                    EngineDetector.save_custom_config(name_clean, chosen)
                    EngineDetector.save_custom_config(inst_clean, chosen)
                    EngineDetector.save_custom_config(f"{name_clean}_{inst_clean}", chosen)
                    return {"success": True, "path": chosen}
            return {"success": False, "error": "Operación cancelada"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # 7. Abrir Carpeta de Configuración en el Explorador
    def open_config_folder(self, file_path: str):
        """Abre la carpeta que contiene el archivo de configuración en el explorador de Windows."""
        try:
            p = Path(file_path)
            folder = p.parent if p.is_file() else p
            if folder.exists():
                os.startfile(str(folder))
                return {"success": True}
            return {"success": False, "error": "Ruta no encontrada"}
        except Exception as e:
            return {"success": False, "error": str(e)}

def main():
    api = OptixForgeApi()
    gui_dir = BASE_DIR / "gui"
    html_file = gui_dir / "index.html"

    window = webview.create_window(
        title="OPTIX FORGE // Engine & FOV / Ultrawide Tweaker",
        url=str(html_file),
        js_api=api,
        width=1320,
        height=880,
        min_size=(1080, 720),
        background_color="#000000"
    )
    api.set_window(window)
    webview.start(debug=False)

if __name__ == "__main__":
    main()

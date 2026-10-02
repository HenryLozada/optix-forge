"""
Optix Forge // Core Backup Manager
Gestor inmutable de copias de seguridad (.bak) y reversión a estado de fábrica en 1 clic.
Garantiza que cualquier archivo de configuración o binario pueda ser restaurado al estado original.
"""

import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

class BackupManager:
    REGISTRY_FILE = Path(__file__).resolve().parent.parent / "data" / "backup_registry.json"

    @classmethod
    def _load_registry(cls) -> Dict[str, Any]:
        if cls.REGISTRY_FILE.exists():
            try:
                return json.loads(cls.REGISTRY_FILE.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}

    @classmethod
    def _save_registry(cls, registry: Dict[str, Any]):
        try:
            cls.REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
            cls.REGISTRY_FILE.write_text(json.dumps(registry, indent=2), encoding="utf-8")
        except Exception:
            pass

    @classmethod
    def ensure_backup(cls, file_path: str | Path) -> bool:
        """
        Crea una copia de seguridad inmutable (.bak) del archivo si no existe ya una.
        """
        target = Path(file_path)
        if not target.exists():
            return False

        bak_path = target.with_suffix(target.suffix + ".bak")
        
        # Si ya existe un .bak original inmutable, no lo sobreescribimos
        if not bak_path.exists():
            try:
                shutil.copy2(target, bak_path)
                registry = cls._load_registry()
                registry[str(target.resolve()).lower()] = {
                    "original_path": str(target.resolve()),
                    "backup_path": str(bak_path.resolve()),
                    "created_at": datetime.now().isoformat(),
                    "file_size": target.stat().st_size
                }
                cls._save_registry(registry)
                return True
            except Exception:
                return False
        return True

    @classmethod
    def has_backup(cls, file_path: str | Path) -> bool:
        """Verifica si existe un respaldo .bak para el archivo."""
        target = Path(file_path)
        bak_path = target.with_suffix(target.suffix + ".bak")
        return bak_path.exists()

    @classmethod
    def restore_original(cls, file_path: str | Path) -> Dict[str, Any]:
        """
        Restaura el archivo original desde su respaldo .bak en 1 clic.
        """
        target = Path(file_path)
        bak_path = target.with_suffix(target.suffix + ".bak")

        if not bak_path.exists():
            return {
                "success": False,
                "error": f"No se encontró copia de respaldo (.bak) para {target.name}"
            }

        try:
            # Restaurar sobreescribiendo el modificado
            shutil.copy2(bak_path, target)
            return {
                "success": True,
                "restored_file": str(target.resolve()),
                "message": f"Configuración de fábrica de {target.name} restaurada exitosamente."
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error al restaurar respaldo: {str(e)}"
            }

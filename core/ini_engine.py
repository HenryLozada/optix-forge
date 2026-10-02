"""
Optix Forge // Core INI Engine
Lector y escritor de alta precisión para archivos de configuración de videojuegos (.ini / .config).
Preserva intactos los comentarios, mayúsculas, espacios y secciones especiales de Unreal Engine.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

class IniEngine:
    def __init__(self, filepath: str | Path):
        self.filepath = Path(filepath)
        self.lines: List[str] = []
        self._load()

    def _load(self):
        if self.filepath.exists():
            try:
                self.lines = self.filepath.read_text(encoding="utf-8", errors="ignore").splitlines()
            except Exception:
                self.lines = []
        else:
            self.lines = []

    def get_value(self, section: str, key: str) -> Optional[str]:
        """Obtiene el valor de una clave dentro de una sección específica."""
        current_section = None
        target_section = section.strip().lower()
        target_key = key.strip().lower()

        for line in self.lines:
            stripped = line.strip()
            if stripped.startswith("[") and stripped.endswith("]"):
                current_section = stripped[1:-1].strip().lower()
                continue
            
            if current_section == target_section and not stripped.startswith((";", "#")):
                if "=" in stripped:
                    k, v = stripped.split("=", 1)
                    if k.strip().lower() == target_key:
                        return v.strip()
        return None

    def set_values(self, section: str, key_values: Dict[str, Any]):
        """
        Inserta o actualiza múltiples pares clave=valor bajo la sección indicada.
        Si la sección no existe, la crea al final del archivo.
        """
        target_section_raw = section.strip()
        target_section_lower = target_section_raw.lower()

        section_start_idx = -1
        section_end_idx = len(self.lines)

        # Localizar la sección
        for i, line in enumerate(self.lines):
            stripped = line.strip()
            if stripped.startswith("[") and stripped.endswith("]"):
                sec_name = stripped[1:-1].strip().lower()
                if sec_name == target_section_lower:
                    section_start_idx = i
                elif section_start_idx != -1:
                    # Fin de la sección encontrada
                    section_end_idx = i
                    break

        # Si la sección no existe, agregarla al final
        if section_start_idx == -1:
            if self.lines and self.lines[-1].strip() != "":
                self.lines.append("")
            self.lines.append(f"[{target_section_raw}]")
            section_start_idx = len(self.lines) - 1
            section_end_idx = len(self.lines)

        # Actualizar claves existentes en el rango de la sección
        keys_to_add = dict(key_values)
        new_lines = list(self.lines)

        for i in range(section_start_idx + 1, section_end_idx):
            line = new_lines[i]
            stripped = line.strip()
            if "=" in stripped and not stripped.startswith((";", "#")):
                k, _ = stripped.split("=", 1)
                k_clean = k.strip()
                # Comparar ignorando mayúsculas
                for target_k in list(keys_to_add.keys()):
                    if target_k.lower() == k_clean.lower():
                        new_val = str(keys_to_add.pop(target_k))
                        new_lines[i] = f"{target_k}={new_val}"
                        break

        # Cualquier clave restante se inserta al final de la sección
        if keys_to_add:
            insert_idx = section_end_idx
            added_lines = [f"{k}={v}" for k, v in keys_to_add.items()]
            new_lines[insert_idx:insert_idx] = added_lines

        self.lines = new_lines

    def save(self) -> bool:
        """Guarda los cambios en el archivo en codificación UTF-8."""
        try:
            self.filepath.parent.mkdir(parents=True, exist_ok=True)
            self.filepath.write_text("\n".join(self.lines) + "\n", encoding="utf-8")
            return True
        except Exception:
            return False

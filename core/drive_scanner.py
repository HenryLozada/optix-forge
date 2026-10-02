"""
Optix Forge // Core Drive Scanner
Detección nativa de unidades de almacenamiento locales y secundarias en Windows
utilizando llamadas directas a la API Win32 (kernel32).
"""

import ctypes
import string
from pathlib import Path
from typing import List, Dict, Any

class DriveScanner:
    @staticmethod
    def get_available_drives() -> List[Dict[str, Any]]:
        """
        Retorna la lista de todas las unidades de disco activas en el sistema,
        con letra de unidad, espacio total, espacio libre y etiqueta de volumen.
        """
        drives_info = []
        bitmask = ctypes.windll.kernel32.GetLogicalDrives()

        for i, letter in enumerate(string.ascii_uppercase):
            if (bitmask >> i) & 1:
                root_path = f"{letter}:\\"
                drive_type = ctypes.windll.kernel32.GetDriveTypeW(root_path)
                
                # 3 = DRIVE_FIXED (HDD/SSD), 2 = DRIVE_REMOVABLE (USB), 4 = DRIVE_REMOTE
                if drive_type in (3, 2, 4):
                    total_bytes = ctypes.c_ulonglong(0)
                    free_bytes = ctypes.c_ulonglong(0)
                    avail_bytes = ctypes.c_ulonglong(0)

                    success = ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                        root_path,
                        ctypes.byref(avail_bytes),
                        ctypes.byref(total_bytes),
                        ctypes.byref(free_bytes)
                    )

                    volume_name_buf = ctypes.create_unicode_buffer(261)
                    fs_name_buf = ctypes.create_unicode_buffer(261)
                    ctypes.windll.kernel32.GetVolumeInformationW(
                        root_path,
                        volume_name_buf,
                        ctypes.sizeof(volume_name_buf),
                        None, None, None,
                        fs_name_buf,
                        ctypes.sizeof(fs_name_buf)
                    )

                    total_gb = round(total_bytes.value / (1024 ** 3), 1) if success else 0.0
                    free_gb = round(free_bytes.value / (1024 ** 3), 1) if success else 0.0
                    label = volume_name_buf.value.strip() or ("Disco Local" if letter == "C" else f"Volumen {letter}")

                    drives_info.append({
                        "letter": letter,
                        "path": root_path,
                        "label": label,
                        "fs": fs_name_buf.value or "NTFS",
                        "total_gb": total_gb,
                        "free_gb": free_gb,
                        "used_gb": round(total_gb - free_gb, 1),
                        "percent_used": round(((total_gb - free_gb) / total_gb * 100), 1) if total_gb > 0 else 0,
                        "is_primary": letter == "C"
                    })

        return drives_info

"""
Test suite para Optix Forge
Verifica detección de unidades de disco, motor INI, respaldos .bak y aplicación de tweaks.
"""

import os
import shutil
import tempfile
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core.drive_scanner import DriveScanner
from core.ini_engine import IniEngine
from core.backup_manager import BackupManager
from core.tweak_matrix import TweakMatrix

def test_drive_scanner():
    drives = DriveScanner.get_available_drives()
    assert len(drives) > 0, "Debe detectar al menos una unidad de disco (C:)"
    c_drive = next((d for d in drives if d["letter"] == "C"), None)
    assert c_drive is not None, "La unidad C: debe estar presente"
    assert c_drive["total_gb"] > 0
    print(f"[OK] Unidades detectadas: {[d['letter'] + ': (' + str(d['total_gb']) + ' GB)' for d in drives]}")

def test_ini_engine_and_tweaks():
    temp_dir = Path(tempfile.mkdtemp(prefix="optix_test_"))
    try:
        sample_ini = temp_dir / "Engine.ini"
        sample_ini.write_text(
            "; Archivo de prueba de motor Unreal\n"
            "[SystemSettings]\n"
            "r.MotionBlurQuality=4\n"
            "r.DepthOfFieldQuality=2\n"
            "\n"
            "[/Script/Engine.Engine]\n"
            "bSmoothFrameRate=True\n",
            encoding="utf-8"
        )

        # 1. Aplicar Tweaks
        options = {
            "disable_motion_blur": True,
            "disable_dof": True,
            "disable_chromatic_aberration": True,
            "disable_film_grain": True,
            "force_anisotropic_16x": True,
            "fix_fov_aspect": True,
            "custom_fov": 105,
            "aspect_ratio_mode": "21:9",
            "unlock_fps": True
        }

        res = TweakMatrix.apply_tweaks(str(sample_ini), options)
        assert res["success"] is True, "Aplicación de tweaks debe ser exitosa"

        # Verificar que se creó el respaldo inmutable .bak
        assert BackupManager.has_backup(sample_ini), "Debe existir copia .bak"

        # Verificar estado
        status = TweakMatrix.get_game_tweak_status(str(sample_ini))
        assert status["motion_blur_disabled"] is True
        assert status["dof_disabled"] is True
        assert status["anisotropic_16x"] is True
        assert status["fov_maintain_y"] is True
        assert status["ultrawide_enabled"] is True
        assert status["fps_unlocked"] is True
        print("[OK] Aplicación de tweaks y verificación de valores exitosa")

        # 2. Restaurar copia original .bak
        restore_res = BackupManager.restore_original(sample_ini)
        assert restore_res["success"] is True, "Restauración debe ser exitosa"

        status_restored = TweakMatrix.get_game_tweak_status(str(sample_ini))
        assert status_restored["motion_blur_disabled"] is False, "Debe haber vuelto al valor de fábrica (motion blur activo)"
        assert status_restored["fps_unlocked"] is False, "FPS no deben estar desbloqueados tras restaurar fábrica"
        print("[OK] Restauración a fábrica desde .bak completada exitosamente")

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    test_drive_scanner()
    test_ini_engine_and_tweaks()
    print("\nTODOS LOS TESTS DE OPTIX FORGE PASARON CORRECTAMENTE [100% OK]")

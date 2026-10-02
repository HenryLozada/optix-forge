"""
Optix Forge // Core Tweak Matrix
Matriz de inyección de optimizaciones gráficas, FOV dinámico, corrección de relación de aspecto
y kill-switches de postprocesado para motores Unreal Engine y configuraciones PC.
"""

from pathlib import Path
from typing import Dict, Any, Optional
from core.ini_engine import IniEngine
from core.backup_manager import BackupManager

class TweakMatrix:
    @staticmethod
    def get_game_tweak_status(config_path: str) -> Dict[str, Any]:
        """
        Lee el estado actual de los tweaks aplicados en un archivo de configuración.
        """
        p = Path(config_path)
        if not p.exists():
            return {
                "has_config": False,
                "motion_blur_disabled": False,
                "dof_disabled": False,
                "chromatic_aberration_disabled": False,
                "film_grain_disabled": False,
                "vignette_disabled": False,
                "lens_flare_disabled": False,
                "fov_maintain_y": False,
                "ultrawide_enabled": False,
                "fps_unlocked": False,
                "anisotropic_16x": False,
                "has_backup": False
            }

        engine = IniEngine(p)
        has_bak = BackupManager.has_backup(p)

        # Evaluar valores actuales
        mb_val = engine.get_value("SystemSettings", "r.MotionBlurQuality") or engine.get_value("/Script/Engine.RendererSettings", "r.MotionBlurQuality")
        dof_val = engine.get_value("SystemSettings", "r.DepthOfFieldQuality") or engine.get_value("/Script/Engine.RendererSettings", "r.DepthOfFieldQuality")
        ca_val = engine.get_value("SystemSettings", "r.SceneColorFringeQuality") or engine.get_value("/Script/Engine.RendererSettings", "r.SceneColorFringeQuality")
        fg_val = engine.get_value("SystemSettings", "r.Tonemapper.GrainQuantization")
        vig_val = engine.get_value("SystemSettings", "r.Vignette")
        lf_val = engine.get_value("SystemSettings", "r.LensFlareQuality")
        fov_axis = engine.get_value("/Script/Engine.LocalPlayer", "AspectRatioAxisConstraint")
        uw_val = engine.get_value("SystemSettings", "r.AspectRatio")
        fps_val = engine.get_value("/Script/Engine.Engine", "bSmoothFrameRate")
        aniso_val = engine.get_value("SystemSettings", "r.MaxAnisotropy")

        return {
            "has_config": True,
            "motion_blur_disabled": mb_val == "0",
            "dof_disabled": dof_val == "0",
            "chromatic_aberration_disabled": ca_val == "0",
            "film_grain_disabled": fg_val == "0",
            "vignette_disabled": vig_val == "0",
            "lens_flare_disabled": lf_val == "0",
            "fov_maintain_y": fov_axis == "AspectRatio_MaintainYFOV",
            "ultrawide_enabled": uw_val is not None and float(uw_val) >= 2.3,
            "fps_unlocked": fps_val == "False",
            "anisotropic_16x": aniso_val == "16",
            "has_backup": has_bak
        }

    @staticmethod
    def apply_tweaks(config_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aplica la combinación solicitada de tweaks garantizando respaldo previo inmutable (.bak).
        """
        p = Path(config_path)
        if not p.exists():
            # Si el archivo no existe pero el directorio es válido, inicializarlo
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("[SystemSettings]\n", encoding="utf-8")

        # Asegurar respaldo antes de cualquier escritura
        BackupManager.ensure_backup(p)

        engine = IniEngine(p)
        system_settings: Dict[str, Any] = {}
        local_player_settings: Dict[str, Any] = {}
        engine_settings: Dict[str, Any] = {}

        # 1. Kill Switches de Postprocesado
        if options.get("disable_motion_blur"):
            system_settings["r.MotionBlurQuality"] = "0"
            system_settings["r.MotionBlur.Max"] = "0"
            system_settings["r.MotionBlur2ndScale"] = "0"

        if options.get("disable_dof"):
            system_settings["r.DepthOfFieldQuality"] = "0"

        if options.get("disable_chromatic_aberration"):
            system_settings["r.SceneColorFringeQuality"] = "0"
            system_settings["r.SceneColorFringe.Max"] = "0"

        if options.get("disable_film_grain"):
            system_settings["r.Tonemapper.GrainQuantization"] = "0"

        if options.get("disable_vignette"):
            system_settings["r.Vignette"] = "0"

        if options.get("disable_lens_flare"):
            system_settings["r.LensFlareQuality"] = "0"

        # 2. Filtrado Anisotrópico 16x
        if options.get("force_anisotropic_16x"):
            system_settings["r.MaxAnisotropy"] = "16"

        # 3. Universal FOV & AspectRatioAxisConstraint
        if options.get("fix_fov_aspect"):
            local_player_settings["AspectRatioAxisConstraint"] = "AspectRatio_MaintainYFOV"

        target_fov = options.get("custom_fov")
        if target_fov and int(target_fov) > 0:
            engine_settings["FOVAngle"] = str(target_fov)

        # 4. Desbloqueo Ultrawide (21:9 o 32:9)
        aspect_ratio_mode = options.get("aspect_ratio_mode")
        if aspect_ratio_mode == "21:9":
            system_settings["r.AspectRatio"] = "2.388889"
            local_player_settings["AspectRatioAxisConstraint"] = "AspectRatio_MaintainYFOV"
        elif aspect_ratio_mode == "32:9":
            system_settings["r.AspectRatio"] = "3.555556"
            local_player_settings["AspectRatioAxisConstraint"] = "AspectRatio_MaintainYFOV"

        # 5. Desbloqueo de FPS
        if options.get("unlock_fps"):
            engine_settings["bSmoothFrameRate"] = "False"
            engine_settings["MinSmoothedFrameRate"] = "0"
            engine_settings["MaxSmoothedFrameRate"] = "1000"

        # Aplicar secciones
        if system_settings:
            engine.set_values("SystemSettings", system_settings)
        if local_player_settings:
            engine.set_values("/Script/Engine.LocalPlayer", local_player_settings)
        if engine_settings:
            engine.set_values("/Script/Engine.Engine", engine_settings)

        success = engine.save()
        return {
            "success": success,
            "applied_file": str(p.resolve()),
            "message": "Optimizaciones de motor inyectadas con éxito." if success else "Error al guardar el archivo."
        }

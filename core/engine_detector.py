"""
Optix Forge // Core Engine Detector
Detección exhaustiva multi-heurística de motores gráficos y localización precisa de configuraciones.
Soporta Unreal Engine 4/5 (con resolución de alias como MK12 para Mortal Kombat 1),
motores Anvil (Assassin's Creed .ini), RAGE (Rockstar settings.xml), Santa Monica (God of War settings.ini)
y vinculación manual persistente.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, Optional, Any, List, Set

class EngineDetector:
    CUSTOM_CONFIGS_FILE = Path(__file__).resolve().parent.parent / "data" / "custom_configs.json"

    IGNORED_INI_NAMES = {
        "dlss-enabler.ini", "optiscaler.ini", "imgui.ini", "hashes.ini",
        "desktop.ini", "unins000.ini", "browscap.ini", "vortextest.ini",
        "steam_emu.ini"
    }

    @classmethod
    def _load_custom_configs(cls) -> Dict[str, str]:
        if cls.CUSTOM_CONFIGS_FILE.exists():
            try:
                return json.loads(cls.CUSTOM_CONFIGS_FILE.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}

    @classmethod
    def save_custom_config(cls, game_key: str, file_path: str):
        try:
            cls.CUSTOM_CONFIGS_FILE.parent.mkdir(parents=True, exist_ok=True)
            data = cls._load_custom_configs()
            data[game_key.lower().strip()] = file_path
            cls.CUSTOM_CONFIGS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception:
            pass

    @classmethod
    def _index_appdata_unreal_dirs(cls) -> Dict[str, Path]:
        local = Path(os.environ.get("LOCALAPPDATA", ""))
        unreal_dirs = {}
        if not local.exists():
            return unreal_dirs

        sub_patterns = [
            "Saved/Config/WindowsNoEditor",
            "Saved/Config/Windows",
            "Saved/Config/WindowsClient",
            "Saved/Steam/Config/WindowsNoEditor",
            "Saved/Steam/Config/Windows",
            "Saved/Config/WinGDK"
        ]

        try:
            for item in local.iterdir():
                if not item.is_dir():
                    continue
                name_l = item.name.lower()
                for sub in sub_patterns:
                    candidate = item / sub
                    if candidate.exists():
                        unreal_dirs[name_l] = candidate
                        break
        except Exception:
            pass

        return unreal_dirs

    @classmethod
    def detect_engine_and_configs(cls, game_name: str, install_path: str) -> Dict[str, Any]:
        inst_dir = Path(install_path)
        name_clean = re.sub(r"[^a-zA-Z0-9]", "", game_name).lower()
        inst_clean = re.sub(r"[^a-zA-Z0-9]", "", inst_dir.name).lower()
        custom_configs = cls._load_custom_configs()

        # 0. Verificar si el usuario ya vinculó un archivo manual
        for k_test in [name_clean, inst_clean, f"{name_clean}_{inst_clean}"]:
            if k_test in custom_configs:
                p_custom = Path(custom_configs[k_test])
                if p_custom.exists():
                    return {
                        "engine": "Configuración Vinculada Manualmente",
                        "has_config": True,
                        "primary_config": str(p_custom.resolve()),
                        "configs": {"custom": str(p_custom.resolve())},
                        "supported_features": {
                            "fov_slider": True,
                            "ultrawide_unlock": True,
                            "kill_switches": True,
                            "fps_unlock": True,
                            "anisotropic_16x": True
                        }
                    }

        is_ue = False
        is_ue5 = False
        is_unity = False
        engine_type = "Desconocido"
        configs: Dict[str, str] = {}
        primary_config: Optional[str] = None

        # 1. Analizar ejecutables y estructura de Unreal Engine en el directorio del juego
        found_exes: List[str] = []
        if inst_dir.exists():
            try:
                for root, dirs, files in os.walk(inst_dir):
                    depth = len(Path(root).relative_to(inst_dir).parts)
                    if depth > 4:
                        dirs.clear()
                        continue
                    
                    for d in dirs:
                        dl = d.lower()
                        if dl in ["windowsnoeditor", "windows", "windowsclient"] or dl == "engine":
                            is_ue = True

                    for f in files:
                        fl = f.lower()
                        if fl.endswith(".exe") and not any(x in fl for x in ["unins", "redist", "crash", "setup", "dx", "vcredist", "launcher"]):
                            stem = Path(f).stem.lower()
                            stem_clean = re.sub(r"(-win64-shipping|_win64_shipping|shipping|win64)$", "", stem)
                            found_exes.append(stem_clean)
                            found_exes.append(stem)
                        if "unityplayer" in fl:
                            is_unity = True
                        if "unrealpak" in fl or "epicaccount" in fl:
                            is_ue = True
                        if fl.endswith(".uproject"):
                            is_ue = True
                            found_exes.append(Path(f).stem.lower())
                        if "ue5" in fl:
                            is_ue5 = True
            except Exception:
                pass

        # 2. Heurística Unreal Engine en %LOCALAPPDATA%
        appdata_unreal = cls._index_appdata_unreal_dirs()

        # Diccionario de alias conocidos (Nombre de juego -> nombre de carpeta Unreal)
        alias_map = {
            "mortalkombat1": "mk12",
            "mk1": "mk12",
            "fortnite": "fortnitegame",
            "silenthill2": "silenthill2",
            "sh2": "silenthill2",
            "starwarsjedi": "swgame",
            "ittakestwo": "ittakestwo",
            "bodycam": "bodycam",
            "biomutant": "biomutant",
            "mgsdelta": "mgsdelta"
        }

        search_tokens = set(found_exes)
        search_tokens.add(name_clean)
        search_tokens.add(inst_clean)

        for k, v in alias_map.items():
            if k in name_clean or k in inst_clean:
                search_tokens.add(v)

        # Buscar coincidencia en Unreal LocalAppData
        matched_unreal_dir = None
        for tok in search_tokens:
            if tok in appdata_unreal:
                matched_unreal_dir = appdata_unreal[tok]
                is_ue = True
                break

        if matched_unreal_dir and matched_unreal_dir.exists():
            for f in matched_unreal_dir.glob("*.ini"):
                fl = f.name.lower()
                if fl == "engine.ini":
                    configs["engine_ini"] = str(f.resolve())
                elif fl == "gameusersettings.ini":
                    configs["game_user_settings_ini"] = str(f.resolve())

            # Si no existe Engine.ini, lo fijamos como destino de creación automática
            if "engine_ini" not in configs:
                configs["engine_ini"] = str((matched_unreal_dir / "Engine.ini").resolve())

            primary_config = configs.get("engine_ini") or configs.get("game_user_settings_ini")

        # 3. Heurística en Documents (Assassin's Creed, GTA V, etc.)
        if not primary_config:
            docs = Path(os.path.expanduser("~/Documents"))
            if docs.exists():
                # Revisar carpetas directas
                for d in docs.iterdir():
                    if not d.is_dir():
                        continue
                    d_clean = re.sub(r"[^a-zA-Z0-9]", "", d.name).lower()
                    # Coincidencia con nombre de juego
                    if any(t in d_clean or d_clean in t for t in search_tokens if len(t) > 3):
                        for f in d.glob("*.ini"):
                            if f.name.lower() not in cls.IGNORED_INI_NAMES:
                                primary_config = str(f.resolve())
                                configs["ini_config"] = primary_config
                                break
                        if not primary_config:
                            for f in d.glob("*.xml"):
                                primary_config = str(f.resolve())
                                configs["xml_config"] = primary_config
                                break

                # Revisar carpetas especiales como Rockstar Games
                if not primary_config and (("gta" in name_clean or "grandtheftauto" in name_clean)):
                    gta_cfg = docs / "Rockstar Games" / "GTA V" / "settings.xml"
                    if gta_cfg.exists():
                        primary_config = str(gta_cfg.resolve())
                        configs["xml_config"] = primary_config

        # 4. Heurística en carpeta de instalación (settings.ini en God of War, etc.)
        if not primary_config and inst_dir.exists():
            # Buscar específicamente settings.ini o archivos de configuración genuinos
            for cand in inst_dir.rglob("settings.ini"):
                if "unins" not in cand.name.lower():
                    primary_config = str(cand.resolve())
                    configs["settings_ini"] = primary_config
                    break

            if not primary_config:
                for cand in inst_dir.rglob("*.ini"):
                    if cand.name.lower() not in cls.IGNORED_INI_NAMES and "unins" not in cand.name.lower():
                        primary_config = str(cand.resolve())
                        configs["local_ini"] = primary_config
                        break

        # 5. Si sabemos que es Unreal Engine pero la carpeta aún no tiene configs en LocalAppData
        if is_ue and not primary_config:
            proj_name = next(iter(found_exes), name_clean)
            local = Path(os.environ.get("LOCALAPPDATA", "C:\\Users\\Public\\AppData\\Local"))
            target_engine = local / proj_name / "Saved" / "Config" / "Windows" / "Engine.ini"
            configs["engine_ini"] = str(target_engine.resolve())
            primary_config = str(target_engine.resolve())

        # Asignar nombre del motor
        if is_ue5:
            engine_type = "Unreal Engine 5"
        elif is_ue:
            engine_type = "Unreal Engine 4"
        elif is_unity:
            engine_type = "Unity Engine"
        elif primary_config:
            if "ACO.ini" in primary_config or "ACBlackFlag.ini" in primary_config:
                engine_type = "Anvil Engine (Ubisoft)"
            elif "settings.xml" in primary_config:
                engine_type = "RAGE Engine (Rockstar)"
            elif "settings.ini" in primary_config and "god of war" in name_clean:
                engine_type = "Santa Monica Engine"
            else:
                engine_type = "PC Engine"

        has_cfg = primary_config is not None

        return {
            "engine": engine_type,
            "has_config": has_cfg,
            "primary_config": primary_config,
            "configs": configs,
            "supported_features": {
                "fov_slider": is_ue or has_cfg,
                "ultrawide_unlock": is_ue or has_cfg,
                "kill_switches": is_ue or has_cfg,
                "fps_unlock": is_ue or is_unity or has_cfg,
                "anisotropic_16x": is_ue or has_cfg
            }
        }

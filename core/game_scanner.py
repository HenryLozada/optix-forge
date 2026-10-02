"""
Optix Forge // Core Game Scanner
Rastreo exhaustivo multi-plataforma y multi-unidad de videojuegos instalados.
Escanea Steam, Epic Games, GOG Galaxy, EA App, Xbox Game Pass y carpetas en todas las unidades.
"""

import os
import re
import json
import winreg
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
from core.drive_scanner import DriveScanner

@dataclass
class ScannedGame:
    name: str
    platform: str
    install_path: str
    drive_letter: str
    app_id: Optional[str] = None
    engine_type: Optional[str] = "Unknown"
    has_config: bool = False
    config_path: Optional[str] = None
    is_restorable: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class GameScanner:
    def __init__(self, config_file: Optional[Path] = None):
        self.config_file = config_file or Path(__file__).resolve().parent.parent / "data" / "custom_paths.json"
        self._custom_paths: List[Path] = []
        self._load_custom_paths()

    def _load_custom_paths(self):
        # 1. Cargar rutas propias de Optix Forge
        if self.config_file.exists():
            try:
                data = json.loads(self.config_file.read_text(encoding="utf-8"))
                for p_str in data:
                    p = Path(p_str).resolve()
                    if p.exists() and p not in self._custom_paths:
                        self._custom_paths.append(p)
            except Exception:
                pass

        # 2. Sincronizar automáticamente con las carpetas personalizadas de Apex Matrix
        apex_cfg = Path(r"c:\Users\Anima\Desktop\PROYECTOS ANIMA\apex-matrix\library\custom_paths.json")
        if apex_cfg.exists():
            try:
                data_apex = json.loads(apex_cfg.read_text(encoding="utf-8"))
                for p_str in data_apex:
                    p = Path(p_str).resolve()
                    if p.exists() and p not in self._custom_paths:
                        self._custom_paths.append(p)
            except Exception:
                pass

    def _save_custom_paths(self):
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            self.config_file.write_text(
                json.dumps([str(p) for p in self._custom_paths], indent=2),
                encoding="utf-8"
            )
        except Exception:
            pass

    def add_custom_path(self, path: str) -> bool:
        p = Path(path).resolve()
        if p.exists():
            if p not in self._custom_paths:
                self._custom_paths.append(p)
                self._save_custom_paths()
            return True
        return False

    def remove_custom_path(self, path: str) -> bool:
        p = Path(path).resolve()
        if p in self._custom_paths:
            self._custom_paths.remove(p)
            self._save_custom_paths()
            return True
        return False

    def get_custom_paths(self) -> List[str]:
        return [str(p) for p in self._custom_paths]

    def scan_games(self, target_drive: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Escanea juegos instalados. Si target_drive se especifica (ej. 'C' o 'D'),
        filtra solo los juegos instalados en esa unidad.
        """
        games: List[ScannedGame] = []
        games.extend(self._scan_steam())
        games.extend(self._scan_epic())
        games.extend(self._scan_gog())
        games.extend(self._scan_ea())
        games.extend(self._scan_xbox())
        games.extend(self._scan_common_drive_folders())
        games.extend(self._scan_custom_paths())

        # Desduplicar por ruta de instalación y nombre canónico
        seen_paths = set()
        seen_names = set()
        unique_games = []
        for g in games:
            p = Path(g.install_path)
            if not p.exists():
                continue
            norm = str(p.resolve()).lower()
            name_clean = re.sub(r"[^a-zA-Z0-9]", "", g.name).lower()
            
            # Evitar carpetas duplicadas o hijas
            if norm not in seen_paths and name_clean not in seen_names:
                seen_paths.add(norm)
                seen_names.add(name_clean)
                drive = p.drive.replace(":", "").upper() or "C"
                g.drive_letter = drive

                if target_drive:
                    if drive == target_drive.upper():
                        unique_games.append(g)
                else:
                    unique_games.append(g)

        unique_games.sort(key=lambda x: x.name.lower())
        return [g.to_dict() for g in unique_games]

    def _scan_steam(self) -> List[ScannedGame]:
        games = []
        steam_path = None
        for hkey in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
            for subkey in [r"SOFTWARE\Valve\Steam", r"SOFTWARE\WOW6432Node\Valve\Steam"]:
                try:
                    with winreg.OpenKey(hkey, subkey) as key:
                        val, _ = winreg.QueryValueEx(key, "InstallPath")
                        if val and Path(val).exists():
                            steam_path = Path(val)
                            break
                except Exception:
                    pass
            if steam_path:
                break

        if not steam_path:
            for fallback in [Path(r"C:\Program Files (x86)\Steam"), Path(r"C:\Program Files\Steam")]:
                if fallback.exists():
                    steam_path = fallback
                    break

        # Buscar bibliotecas adicionales en todos los discos
        lib_dirs = []
        if steam_path:
            lib_dirs.append(steam_path / "steamapps")
            vdf_path = steam_path / "steamapps" / "libraryfolders.vdf"
            if vdf_path.exists():
                try:
                    content = vdf_path.read_text(encoding="utf-8", errors="ignore")
                    for m in re.finditer(r'"path"\s+"([^"]+)"', content):
                        p = Path(m.group(1).replace(r"\\", "\\")) / "steamapps"
                        if p.exists() and p not in lib_dirs:
                            lib_dirs.append(p)
                except Exception:
                    pass

        # Chequear en cada disco conocido carpetas SteamLibrary
        drives = DriveScanner.get_available_drives()
        for d in drives:
            candidate = Path(d["path"]) / "SteamLibrary" / "steamapps"
            if candidate.exists() and candidate not in lib_dirs:
                lib_dirs.append(candidate)

        for lib in lib_dirs:
            if not lib.exists():
                continue
            for acf in lib.glob("appmanifest_*.acf"):
                try:
                    txt = acf.read_text(encoding="utf-8", errors="ignore")
                    name_m = re.search(r'"name"\s+"([^"]+)"', txt)
                    dir_m = re.search(r'"installdir"\s+"([^"]+)"', txt)
                    appid_m = re.search(r'"appid"\s+"(\d+)"', txt)
                    if name_m and dir_m:
                        game_name = name_m.group(1)
                        if "steamworks" in game_name.lower() or "proton" in game_name.lower():
                            continue
                        game_path = lib / "common" / dir_m.group(1)
                        if game_path.exists():
                            games.append(ScannedGame(
                                name=game_name,
                                platform="Steam",
                                install_path=str(game_path.resolve()),
                                drive_letter=game_path.drive.replace(":", "").upper(),
                                app_id=appid_m.group(1) if appid_m else None
                            ))
                except Exception:
                    pass
        return games

    def _scan_epic(self) -> List[ScannedGame]:
        games = []
        manifests_dir = Path(os.environ.get("PROGRAMDATA", "C:\\ProgramData")) / "Epic" / "EpicGamesLauncher" / "Data" / "Manifests"
        if not manifests_dir.exists():
            return games
        for mf in manifests_dir.glob("*.item"):
            try:
                data = json.loads(mf.read_text(encoding="utf-8"))
                install_loc = data.get("InstallLocation")
                display_name = data.get("DisplayName")
                app_name = data.get("AppName")
                if install_loc and display_name:
                    p = Path(install_loc)
                    if p.exists():
                        games.append(ScannedGame(
                            name=display_name,
                            platform="Epic Games",
                            install_path=str(p.resolve()),
                            drive_letter=p.drive.replace(":", "").upper(),
                            app_id=app_name
                        ))
            except Exception:
                pass
        return games

    def _scan_gog(self) -> List[ScannedGame]:
        games = []
        for hkey in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
            for subkey in [r"SOFTWARE\GOG.com\Games", r"SOFTWARE\WOW6432Node\GOG.com\Games"]:
                try:
                    with winreg.OpenKey(hkey, subkey) as key:
                        num_subkeys = winreg.QueryInfoKey(key)[0]
                        for i in range(num_subkeys):
                            try:
                                sub = winreg.EnumKey(key, i)
                                with winreg.OpenKey(key, sub) as game_key:
                                    name, _ = winreg.QueryValueEx(game_key, "gameName")
                                    path, _ = winreg.QueryValueEx(game_key, "path")
                                    if path and Path(path).exists():
                                        p = Path(path)
                                        games.append(ScannedGame(
                                            name=name or p.name,
                                            platform="GOG",
                                            install_path=str(p.resolve()),
                                            drive_letter=p.drive.replace(":", "").upper(),
                                            app_id=sub
                                        ))
                            except Exception:
                                pass
                except Exception:
                    pass
        return games

    def _scan_ea(self) -> List[ScannedGame]:
        games = []
        ea_data = Path(os.environ.get("PROGRAMDATA", "C:\\ProgramData")) / "EA Desktop" / "InstallData"
        if ea_data.exists():
            for folder in ea_data.iterdir():
                if folder.is_dir():
                    clean_name = folder.name.replace("%3a", ":").replace("%5c", "\\")
                    p = Path(clean_name)
                    if p.exists() and p.is_dir():
                        games.append(ScannedGame(
                            name=p.name,
                            platform="EA App",
                            install_path=str(p.resolve()),
                            drive_letter=p.drive.replace(":", "").upper()
                        ))
        return games

    def _scan_xbox(self) -> List[ScannedGame]:
        games = []
        drives = DriveScanner.get_available_drives()
        for d in drives:
            xbox_dir = Path(d["path"]) / "XboxGames"
            if xbox_dir.exists():
                for item in xbox_dir.iterdir():
                    if item.is_dir():
                        games.append(ScannedGame(
                            name=item.name,
                            platform="Xbox Game Pass",
                            install_path=str(item.resolve()),
                            drive_letter=d["letter"]
                        ))
        return games

    def _scan_common_drive_folders(self) -> List[ScannedGame]:
        games = []
        drives = DriveScanner.get_available_drives()
        common_subfolders = ["Games", "Juegos", "Gaming", "Juegos PC", "RaidGames"]
        ignored_names = {"razercortexgameclips", "steamlibrary", "xboxgames", "windows", "program files", "program files (x86)", "$recycle.bin", "system volume information"}

        for d in drives:
            root = Path(d["path"])
            if not root.exists():
                continue

            # 1. Carpetas contenedoras (ej. C:\Games, D:\Juegos)
            for sub in common_subfolders:
                folder = root / sub
                if folder.exists() and folder.is_dir():
                    try:
                        for item in folder.iterdir():
                            if item.is_dir():
                                games.append(ScannedGame(
                                    name=item.name,
                                    platform="Local PC",
                                    install_path=str(item.resolve()),
                                    drive_letter=d["letter"]
                                ))
                    except Exception:
                        pass

            # 2. Carpetas de juegos directamente en la raíz del disco (ej. D:\God-Of-War-AnkerGames)
            try:
                for item in root.iterdir():
                    if not item.is_dir():
                        continue
                    name_l = item.name.lower()
                    if name_l in ignored_names or name_l in [s.lower() for s in common_subfolders] or name_l in ["riot games"]:
                        continue
                    if "ankergames" in name_l or "game" in name_l or "juego" in name_l:
                        # Verificar si tiene una subcarpeta con el juego real
                        target_path = item
                        for sub_item in item.iterdir():
                            if sub_item.is_dir() and any(f.suffix.lower() == ".exe" for f in sub_item.glob("*.exe")):
                                target_path = sub_item
                                break
                        games.append(ScannedGame(
                            name=item.name,
                            platform=f"Disco {d['letter']}: Local",
                            install_path=str(target_path.resolve()),
                            drive_letter=d["letter"]
                        ))
            except Exception:
                pass

        return games

    def _scan_custom_paths(self) -> List[ScannedGame]:
        games = []
        for p in self._custom_paths:
            if p.exists() and p.is_dir():
                games.append(ScannedGame(
                    name=p.name,
                    platform="Personalizado",
                    install_path=str(p.resolve()),
                    drive_letter=p.drive.replace(":", "").upper()
                ))
        return games

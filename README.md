# OPTIX FORGE // Engine & FOV / Ultrawide Matrix ⚡

**Optix Forge** es una suite de escritorio de alto rendimiento para Windows diseñada para **desbloquear el verdadero potencial visual de tus videojuegos de PC**. Permite ajustar el campo de visión (FOV), desbloquear relaciones de aspecto panorámicas (**21:9 Ultrawide** y **32:9 Super-Wide**), erradicar filtros molestos de postprocesado (*Motion Blur, Depth of Field, Chromatic Aberration*) y forzar máxima nitidez de texturas, todo con respaldo inmutable **`.bak`** y reversión a estado de fábrica en 1 clic.

Forma parte de la suite **Anima Gaming Ecosystem** junto a **Animus SaveVault** y **Apex Matrix**.

---

## 🚀 Características Principales

### 1. 💾 Buscador Inteligente Multi-Unidad
* **Detección Automática de Discos:** Reconoce de inmediato el disco local `C:\` y todas las unidades secundarias montadas (`D:\`, `E:\`, etc.) con cálculo de espacio libre y total.
* **Filtro por Unidad en 1 Clic:** Explora los juegos de un disco específico o de todas las unidades simultáneamente.
* **Soporte Multi-Plataforma:** Escanea automáticamente bibliotecas de Steam, Epic Games Launcher, GOG Galaxy, EA Desktop, Xbox Game Pass y carpetas locales comunes.
* **Selector Manual de Directorios:** Botón `[+ CARPETA PERSONALIZADA]` para añadir cualquier directorio sin alterar tus archivos.

### 2. 🎮 Universal FOV & Aspect Ratio Matrix
* **Deslizador Dinámico de FOV:** Calibra el campo de visión desde 70° hasta 125°.
* **Corrección de Eje Vertical (`MaintainYFOV`):** Inyección de `AspectRatioAxisConstraint=AspectRatio_MaintainYFOV` en Unreal Engine, evitando el zoom forzado y el recorte superior/inferior de pantalla.
* **Selector de Aspect Ratio Forzado:** Alterna entre `NATIVO`, `21:9 ULTRAWIDE` y `32:9 SUPER-WIDE` para eliminar barras negras (*pillarboxes*) en monitores panorámicos.

### 3. 🚫 Kill Switch de Postprocesado (1 Clic)
* **Motion Blur Off:** Elimina el desenfoque de movimiento en giros rápidos de cámara.
* **Depth of Field Off:** Desactiva la profundidad de campo que vuelve borroso el escenario de fondo.
* **Chromatic Aberration Off:** Elimina los halos de color distorsionados en los bordes de la pantalla.
* **Film Grain & Ruido Off:** Desactiva el grano cinematográfico para una imagen nítida de alta resolución.
* **Vignette Off:** Suprime el oscurecimiento artificial de las esquinas.
* **Lens Flare Off:** Control sobre destellos de lente cegadores.

### 4. ⚡ Rendimiento & Claridad
* **FPS Unlocker:** Desactiva límites arbitrarios de tasa de refresco (`bSmoothFrameRate=False`).
* **Filtrado Anisotrópico 16x:** Forza máxima definición de texturas lejanas y superficies en ángulo rasante.

### 5. ↺ Escudo Inmutable `.bak` y Restauración a Fábrica
* Antes de modificar cualquier archivo de configuración, se genera una copia de seguridad inmutable `.bak`.
* **Botón `[RESTAURAR FÁBRICA (.BAK)]`:** Reversión instantánea que deja el juego en su estado original sin reinstalar ni perder datos.

### 6. 🥋 Animaciones Agresivas Tekken-Impact
* Interfaz HUD militar/industrial basada en **NVIDIA Power Green** (`#76b900` / `#bff230` / `#000000`).
* Transiciones con snap contundente (80ms), cortes biselados industriales, ráfagas de sobrevoltaje neón y micro-impactos sintetizados con Web Audio API al seleccionar juegos o inyectar parches.

---

## 💻 Ejecución y Compilación

### Requisitos:
* Windows 10 o Windows 11 (64-bit)
* Python 3.10+
* `pip install pywebview`

### Ejecución Directa:
Doble clic en **`Ejecutar_OptixForge.bat`** o desde la terminal:
```powershell
python main.py
```

### Compilar a Ejecutable (.exe) Portable:
```powershell
python build.py
```
El ejecutable generado se ubicará en `dist/OptixForge/OptixForge.exe`.

---

## 🏛️ Estructura del Proyecto

```text
optix-forge/
├── core/
│   ├── drive_scanner.py       # Detección Win32 de discos C:\, D:\ y espacio libre
│   ├── game_scanner.py        # Escáner multi-disco de lanzadores y carpetas de juegos
│   ├── engine_detector.py     # Detección de Unreal Engine / Unity y ubicación de configs
│   ├── ini_engine.py          # Lector/escritor seguro de archivos .ini
│   ├── tweak_matrix.py        # Aplicación atómica de FOV, Ultrawide y Kill switches
│   └── backup_manager.py      # Resguardos .bak inmutables y reversión en 1 clic
├── gui/
│   ├── index.html             # Interfaz HUD con barra de discos y fighter select
│   ├── style.css              # Sistema NVIDIA Power Green + Tekken-Impact motion
│   └── app.js                 # Control reactivo y audio sintético de impacto
├── data/
│   └── presets.json           # Definición de relaciones de aspecto y parámetros base
├── tests/
│   └── test_optix.py          # Test suite con validación 100%
├── DESIGN_SYSTEM.md           # Especificación del sistema de diseño
├── main.py                    # Entrypoint y API bridge con pywebview
├── build.py                   # Script de compilación PyInstaller
├── Ejecutar_OptixForge.bat    # Lanzador directo para Windows
└── README.md                  # Documentación
```

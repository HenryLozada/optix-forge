---
version: "1.0.0"
name: "NVIDIA Power Green // Tekken-Impact Motion System"
description: "Sistema de diseño de ingeniería de alto impacto para utilidades de hardware y optimización visual de videojuegos en PC."
colors:
  bg_primary: "#000000"
  bg_carbon: "#07090a"
  bg_surface: "#0f1214"
  bg_surface_elevated: "#161a1e"
  accent_green: "#76b900"
  accent_neon: "#bff230"
  accent_amber: "#df6500"
  accent_danger: "#ff2a2a"
  text_pure: "#ffffff"
  text_muted: "#52606a"
geometry:
  corners: "Biselado chamfer 10px / 12px (clip-path: polygon)"
  borders: "1px solid #22292f / 1px solid #76b900"
motion:
  hover_impact: "Snap agresivo scale(1.035) translateY(-3px) en 80ms con cubic-bezier(0.1, 1.2, 0.4, 1)"
  click_strike: "Flash de sobretensión eléctrica y micro-sacudida sismográfica"
---

# NVIDIA Power Green // Tekken-Impact Motion System

## 1. Filosofía & Declaración de Intenciones
**Optix Forge** une la sobriedad técnica del diseño de ingeniería de **NVIDIA Power Green** con la contundencia de las interfaces de selección de combate estilo **Tekken**:
- Cero transiciones lentas o flotantes: cada interacción física tiene un **impacto seco** inmediato (80ms - 150ms).
- Bordes con cortes biselados industriales tipo blindaje de hardware en lugar de esquinas redondeadas estilo móvil.
- Feedback de audio-visual sintetizado al vuelo (Web Audio API) que produce un golpe de resonancia física al seleccionar juegos o inyectar configuraciones.

## 2. Paleta de Colorimetría de Silicio
- **Negro Absoluto (`#000000`)**: Fondo maestro y absorción lumínica.
- **Carbón Industrial (`#07090a` / `#0f1214`)**: Superficies de contención de tarjetas y paneles HUD.
- **Verde NVIDIA Puro (`#76b900`)**: Acento de ingeniería y validación de hardware.
- **Lima Voltaje Neón (`#bff230`)**: Señal de combate activo, hover de máxima intensidad y destellos de inyección.
- **Rojo Advertencia / Fábrica (`#ff2a2a` / `#1e1313`)**: Bloque de restauración inmutable `.bak`.

## 3. Dinámicas de Movimiento (Tekken-Strike)
1. **Character Lock-in:**
   Al hacer clic sobre un título, la tarjeta sufre un destello de brillo (`filter: brightness(2)`) y el panel de calibración derecho vibra con una micro-sacudida (`screen-shake`).
2. **Inyección de Parche (Voltage Strike):**
   Al pulsar `[INYECTAR PARCHE OPTIX]`, la interfaz completa experimenta un estallido verde neón acompañado de un sonido sintetizado de sobrecarga eléctrica antes de confirmar el resguardo `.bak`.
3. **Escudo de Respaldo Inmutable (.BAK):**
   Cualquier modificación es reversible con un clic instantáneo en el botón de restauración a fábrica.

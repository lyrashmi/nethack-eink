# NetHack E-Ink

A high-contrast light-mode port of **NetHack 5.0.0** for Android e-ink devices (such as the Ratta Supernote), built on [NetHack-Android](https://github.com/JodiJodington/NetHack-Android) and a customised [ForkFront-Android](https://github.com/lyrashmi/forkfront-android) frontend.

## Key Features

- **E-Ink First Light Theme**: Renders the dungeon canvas, menus, and UI chrome on a pure white (`#FFFFFF`) background with crisp black (`#000000`) text, walls, and solid borders for maximum readability without glare.
- **High-Contrast 16-Colour Palette & Tilesets**: Calibrates every ANSI colour and graphical tileset (`Default`, `Geoduck`, `Nevada`) to high-contrast tones on white backgrounds, eliminating muddy grayscale dithering on monochrome e-paper displays.
- **Ghost-Free UI & Instant Paging**: Removes ripples, shadows, animations, and kinetic drag-scrolling in favour of binary black/white selection states and instant `[ ◄ Prev ]` / `[ Next ► ]` page jumps.
- **Touch & Stylus Navigation**: Dismisses menus, prompts, and tooltips by tapping outside them, keeps your inventory open when backing out of item actions, and includes dedicated `[ Back ]` headers for devices without Android navigation buttons.
- **Static Command Grid & Auto-Opening D-Pad**: Displays all primary commands simultaneously in a fixed multi-row grid (including `ESC` and `#loot`), paired with a collapsible directional numpad and double-tap auto-travel.
- **Large-Screen Ergonomics & Safe-Area Margins**: Scales typography, map zoom, and touch targets for 10-inch e-paper tablets with `5dp` bezel padding, a 7-line rolling message log, and a stationary camera option.
- **In-Game Save & Background Checkpointing**: Includes a dedicated `[ Save Current Game ]` button in Settings alongside automatic background state checkpointing to protect progress against system force-stops.

## Building from Source

1. Clone both repositories side by side (as `settings.gradle` links to `../forkfront-android` via Gradle composite build):
   ```bash
   git clone [https://github.com/lyrashmi/nethack-eink.git](https://github.com/lyrashmi/nethack-eink.git)
   git clone [https://github.com/lyrashmi/forkfront-android.git](https://github.com/lyrashmi/forkfront-android.git)
   ```
2. Provision the Android NDK (`r21e` or compatible) and compile the native NetHack C core and Lua runtime:
   ```bash
   cd nethack-eink/sys/android
   sh ./setup.sh
   cd ../..
   make install
   ```
3. Assemble the debug APK using JDK 21:
   ```bash
   cd sys/android
   ./gradlew assembleDebug
   ```
   The compiled ARM64 APK is output to `sys/android/app/build/outputs/apk/debug/app-arm64-v8a-debug.apk`.

## Installation via ADB

```bash
adb install -r sys/android/app/build/outputs/apk/debug/app-arm64-v8a-debug.apk
```

## Credits & Upstream Projects

- [NetHack](https://www.nethack.org/) — The NetHack DevTeam
- [NetHack-Android](https://github.com/JodiJodington/NetHack-Android) & [ForkFront-Android](https://github.com/JodiJodington/ForkFront-Android) — Gurr & JodiJodington

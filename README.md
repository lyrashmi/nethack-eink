# NetHack E-Ink

A high-contrast light-mode port of **NetHack 3.7** for Android e-ink devices (such as the Ratta Supernote), built on [NetHack-Android](https://github.com/JodiJodington/NetHack-Android) and a customised [ForkFront-Android](https://github.com/lyrashmi/forkfront-android) frontend.

## Key Features

- **High-Contrast E-Ink Light Theme**: Pure white (`#FFFFFF`) canvas and UI chrome with crisp black (`#000000`) text, walls, and `1dp`–`2dp` solid borders.
- **16-Colour E-Ink ANSI Palette**: Remapped all `CLR_*` entries in `winandroid.c` and `defaults.nh` to deep, high-contrast tones ($\ge 6.8:1$ contrast against white) that remain sharp on monochrome Carta e-paper without muddy grayscale dithering.
- **Zero-Animation Instant Inversion**: Replaced Android ripples, shadows, and translucent scrims with binary black/white state selectors to eliminate ghosting and full-screen refresh flashes.
- **Navigation Without Hardware Keys**:
  - Tap anywhere outside menus, questions, or tooltips to dismiss them.
  - Native C sub-menu loop (`invent.c` / `iactions.c`) so backing out of item actions returns directly to the open inventory list.
  - Persistent `[ Back ]` header buttons across single-select menus and nested Settings screens, plus an explicit `ESC` button on the command grid.
- **Uniform Multi-Row Command Grid**: Replaced horizontal scrolling with a deterministic fixed-column grid (`FlowLayout`) so all commands remain visible simultaneously, including `ESC` and `M-l` (loot), alongside a collapsible directional movement pad.
- **150% UI Scaling & Safe-Area Padding**: Scaled UI controls and typography for larger e-paper screens with `5dp` bezel safe-area padding.

## Building from Source

1. Clone both repositories side by side (as `settings.gradle` links to `../forkfront-android` via Gradle composite build):
   ```bash
   git clone [https://github.com/lyrashmi/nethack-eink.git](https://github.com/lyrashmi/nethack-eink.git)
   git clone [https://github.com/lyrashmi/forkfront-android.git](https://github.com/lyrashmi/forkfront-android.git)

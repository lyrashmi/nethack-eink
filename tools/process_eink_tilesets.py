#!/usr/bin/env python3
"""
Process NetHack graphical tilesets for E-Ink light mode:
- Idempotently restores pristine originals from git commit d55c4d2a0 before processing
- Replaces dark/teal room and corridor backgrounds with pure #FFFFFF
- Darkens room floor dots (S_room) and corridor markers to crisp dark (40, 40, 40)
- Adds crisp dark boundary outlines for bright sprite edges
- Darkens low-contrast yellows and cyans/blues so they render clearly on e-ink
- Converts stone (1272) and unexplored void (1469, 1470) to 100% pure #FFFFFF
"""

import os
import sys
import subprocess
from PIL import Image

def restore_pristine_tilesets(base_dir):
    print("Checking out pristine untouched tilesets from git commit d55c4d2a0...")
    repo_dir = "/home/vivien/src/nethack-eink"
    cmd = ["git", "-C", repo_dir, "checkout", "d55c4d2a0", "--", "sys/android/app/res/drawable-nodpi/"]
    subprocess.check_call(cmd)
    print("Pristine tilesets checked out successfully.")

def clean_dark_and_void_tiles(img, tile_w, tile_h, cols=40):
    w, h = img.size
    rows = h // tile_h
    total = cols * rows
    pix = img.load()
    is_rgba = (img.mode == "RGBA")
    white = (255, 255, 255, 255) if is_rgba else (255, 255, 255)
    
    cleaned = []
    for idx in range(total):
        col = idx % cols
        row = idx // cols
        x0 = col * tile_w
        y0 = row * tile_h
        
        dark_count = 0
        n_pixels = tile_w * tile_h
        for y in range(y0, y0 + tile_h):
            for x in range(x0, x0 + tile_w):
                p = pix[x, y]
                if is_rgba:
                    r, g, b, a = p
                else:
                    r, g, b = p[:3]
                    a = 255
                if max(r, g, b) < 40 and a > 128:
                    dark_count += 1
                    
        # Check stone, unexplored, nothing, or >= 90% dark pixels in environment/dungeon range (idx >= 1272)
        if idx in [1272, 1469, 1470] or (idx >= 1272 and dark_count >= 0.90 * n_pixels):
            cleaned.append(idx)
            for y in range(y0, y0 + tile_h):
                for x in range(x0, x0 + tile_w):
                    pix[x, y] = white
    print(f"Cleaned {len(cleaned)} void/stone/dark tiles: {cleaned}")
    return cleaned

def process_default(input_path, output_path):
    print(f"Processing {input_path} -> {output_path}...")
    img = Image.open(input_path).convert("RGBA")
    w, h = img.size
    pix = img.load()
    out = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    out_pix = out.load()
    
    is_bg = [[False]*w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            if pix[x, y][:3] == (71, 108, 108):
                is_bg[y][x] = True
                
    for y in range(h):
        for x in range(w):
            if is_bg[y][x]:
                touches_bright = False
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and not is_bg[ny][nx]:
                        nr, ng, nb = pix[nx, ny][:3]
                        lum = 0.299 * nr + 0.587 * ng + 0.114 * nb
                        if lum > 190:
                            touches_bright = True
                            break
                if touches_bright:
                    out_pix[x, y] = (0, 0, 0, 255)
                else:
                    out_pix[x, y] = (255, 255, 255, 255)
            else:
                r, g, b, a = pix[x, y]
                # Never darken white or near-white
                if min(r, g, b) > 220:
                    out_pix[x, y] = (255, 255, 255, 255)
                # Floor dot (108, 145, 182) -> crisp dark
                elif (r, g, b) == (108, 145, 182):
                    out_pix[x, y] = (40, 40, 40, 255)
                elif r > 200 and g > 200 and b < 80: # yellow
                    out_pix[x, y] = (180, 110, 0, 255)
                elif r < 150 and g > 180 and b > 180: # saturated cyan
                    out_pix[x, y] = (0, 130, 150, 255)
                else:
                    out_pix[x, y] = (r, g, b, 255)

    cols = w // 16
    # Convert dark room tile 1292 shadow pixels to pure white, keeping floor dot
    col = 1292 % cols
    row = 1292 // cols
    x0, y0 = col * 16, row * 16
    for y in range(y0, y0 + 16):
        for x in range(x0, x0 + 16):
            if out_pix[x, y] == (0, 0, 0, 255):
                out_pix[x, y] = (255, 255, 255, 255)

    clean_dark_and_void_tiles(out, 16, 16)
    out.save(output_path, "PNG")
    print(f"Saved {output_path}")

def process_geoduck(input_path, output_path):
    print(f"Processing {input_path} -> {output_path}...")
    img = Image.open(input_path)
    w, h = img.size
    pix = img.load()
    out = Image.new("RGB", (w, h), (255, 255, 255))
    out_pix = out.load()
    
    bg_set = {
        (32, 33, 72), (44, 43, 44), (52, 41, 36), (57, 41, 60), # room floor bg
        (46, 48, 82), (56, 56, 56), (63, 53, 50), (68, 54, 71), # corr bg
        (59, 62, 92), (66, 66, 66), (73, 66, 63), (78, 67, 81), # lit corr bg
    }
    
    is_bg = [[False]*w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            if pix[x, y][:3] in bg_set:
                is_bg[y][x] = True
                
    for y in range(h):
        for x in range(w):
            if is_bg[y][x]:
                touches_bright = False
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and not is_bg[ny][nx]:
                        nr, ng, nb = pix[nx, ny][:3]
                        lum = 0.299 * nr + 0.587 * ng + 0.114 * nb
                        if lum > 190:
                            touches_bright = True
                            break
                if touches_bright:
                    out_pix[x, y] = (0, 0, 0)
                else:
                    out_pix[x, y] = (255, 255, 255)
            else:
                r, g, b = pix[x, y][:3]
                # Never darken white or near-white
                if min(r, g, b) > 220:
                    out_pix[x, y] = (255, 255, 255)
                # Floor dots (160, 160, 160) or (100, 100, 100) -> crisp dark
                elif (r, g, b) in [(160, 160, 160), (100, 100, 100)]:
                    out_pix[x, y] = (40, 40, 40)
                elif r > 200 and g > 200 and b < 80: # yellow
                    out_pix[x, y] = (180, 110, 0)
                elif r < 120 and g < 120 and b > 200: # saturated blue
                    out_pix[x, y] = (50, 50, 180)
                elif r == 191 and g == 191 and b == 191: # mid gray
                    out_pix[x, y] = (100, 100, 100)
                else:
                    out_pix[x, y] = (r, g, b)

    clean_dark_and_void_tiles(out, 15, 25)
    out.save(output_path, "PNG")
    print(f"Saved {output_path}")

def process_nevanda(input_path, output_path):
    print(f"Processing {input_path} -> {output_path}...")
    img = Image.open(input_path).convert("RGBA")
    w, h = img.size
    pix = img.load()
    out = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    out_pix = out.load()
    
    is_bg = [[False]*w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            r, g, b, a = pix[x, y]
            if a < 30 or (abs(r - 70) <= 6 and abs(g - 109) <= 6 and abs(b - 108) <= 6):
                is_bg[y][x] = True
                
    for y in range(h):
        for x in range(w):
            if is_bg[y][x]:
                touches_bright = False
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and not is_bg[ny][nx]:
                        nr, ng, nb = pix[nx, ny][:3]
                        lum = 0.299 * nr + 0.587 * ng + 0.114 * nb
                        if lum > 190:
                            touches_bright = True
                            break
                if touches_bright:
                    out_pix[x, y] = (0, 0, 0, 255)
                else:
                    out_pix[x, y] = (255, 255, 255, 255)
            else:
                r, g, b, a = pix[x, y]
                # Never darken white or near-white
                if min(r, g, b) > 220:
                    out_pix[x, y] = (255, 255, 255, 255)
                # Floor dot (108, 145, 182) -> crisp dark
                elif (r, g, b) == (108, 145, 182):
                    out_pix[x, y] = (40, 40, 40, 255)
                elif r > 200 and g > 200 and b < 80: # yellow
                    out_pix[x, y] = (180, 110, 0, 255)
                elif r < 150 and g > 180 and b > 180: # saturated cyan
                    out_pix[x, y] = (0, 130, 150, 255)
                else:
                    out_pix[x, y] = (r, g, b, 255)

    cols = w // 32
    # Convert dark room tile 1292 shadow pixels to pure white, keeping floor dot
    col = 1292 % cols
    row = 1292 // cols
    x0, y0 = col * 32, row * 32
    for y in range(y0, y0 + 32):
        for x in range(x0, x0 + 32):
            if out_pix[x, y] == (0, 0, 0, 255):
                out_pix[x, y] = (255, 255, 255, 255)

    clean_dark_and_void_tiles(out, 32, 32)
    out.save(output_path, "PNG")
    print(f"Saved {output_path}")

def main():
    base_dir = "/home/vivien/src/nethack-eink/sys/android/app/res/drawable-nodpi"
    restore_pristine_tilesets(base_dir)
    process_default(os.path.join(base_dir, "default_16x16.png"), os.path.join(base_dir, "default_16x16.png"))
    process_geoduck(os.path.join(base_dir, "geoduck_15x25.png"), os.path.join(base_dir, "geoduck_15x25.png"))
    process_nevanda(os.path.join(base_dir, "nevanda_32x32.png"), os.path.join(base_dir, "nevanda_32x32.png"))
    print("All tilesets processed successfully.")

if __name__ == "__main__":
    main()

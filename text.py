#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Display a message fading into the console, using console text."""

import os
import sys
import time

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "Yes, hide it"
import pygame

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

CONSOLE_SIZE = (79,40)

FADE_STEPS = 12
FADE_TIME = 4

def build_intensity_map():
    """Create a mapping from letters to how strongly they glow with a
    monospace font."""
    letterfont = pygame.font.SysFont('Courier New', 12)
    letters = r"abcdefghihklimnopqrstuvxyzABCDEFGHIJKLMNOPQRSTUVWXYZ -=!#¤%&+*"
    # letters = r"LUDVIGludvig, "

    result = {}

    for letter in letters:
        lettersurface = letterfont.render(letter, False, WHITE, BLACK)
        pixels = pygame.PixelArray(lettersurface)
        rows, cols = pixels.shape
        pct = 0.0
        white = lettersurface.map_rgb(WHITE)
        for row in range(rows):
            for col in range(cols):
                if pixels[row, col] == white:
                    pct += 1 / (rows * cols)
        result[letter] = pct

    # Scale intensities so that they are 0 to 1
    max_intensity = max(result.values())
    for letter in result.keys():
        result[letter] /= max_intensity
    return result

BEST_LETTER_CACHE = {}
def get_best_letter(target_intensity, intensity_map):
    """Find the letter that looks most like a pixel of intensity |target_intensity|"""
    if target_intensity not in BEST_LETTER_CACHE:
        intensity_distances = ((abs(letter_intensity - target_intensity), letter)
                               for letter, letter_intensity in intensity_map.items())
        best_letter = sorted(intensity_distances)[0][1]
        BEST_LETTER_CACHE[target_intensity] = best_letter
    return BEST_LETTER_CACHE[target_intensity]

def check_quit():
    """pygame won't let the user kill with ctrl-c unless we confirm it."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

def clear_screen():
    """Try to clear the console."""
    os.system("cls")

def draw_image_on_console(image, intensity_map, alpha=1.0):
    """Draw an image on the console, using the letters in
    |intensity_map| and with an alpha of |alpha|."""
    surface = scale_image_to_console_fit(image, CONSOLE_SIZE)
    pixels = pygame.PixelArray(surface)
    cols, rows = pixels.shape
    for row in range(rows):
        line = []
        for col in range(cols):
            pixel = surface.unmap_rgb(pixels[col, row])
            r, g, b = pixel[:3]
            intensity = (0.2989 * r + 0.5870 * g + 0.1140 * b) / 255
            if len(pixel) == 4:  # Alpha channel?
                intensity *= pixel[3] / 255
            intensity *= alpha

            line.append(get_best_letter(intensity, intensity_map))
        print("".join(line))
    sys.stdout.flush()

def fade_in_text_in_console(text, intensity_map):
    textfont = pygame.font.SysFont('Comic Sans MS', min(30, 200 // len(text)))
    textsurface = textfont.render(text, True, WHITE, BLACK)

    for opaqueness in range(1, FADE_STEPS + 1):
        alpha = opaqueness / FADE_STEPS
        clear_screen()
        draw_image_on_console(textsurface, intensity_map, alpha)
        time.sleep(FADE_TIME / FADE_STEPS)
        check_quit()

def scale_image_to_console_fit(image, fit_size):
    console_font_aspect_ratio = 0.6  # Console letters are not square but rectangles.
    image_size = image.get_size()
    scale_factors = [1,
                     fit_size[0] / image_size[0],
                     fit_size[1] / image_size[1] / console_font_aspect_ratio]
    scale_factor = min(scale_factors)

    new_size = (int(image.get_size()[0] * scale_factor),
                int(image.get_size()[1] * scale_factor * console_font_aspect_ratio))
    return pygame.transform.scale(image, new_size)

def main():
    pygame.init()
    intensity_map = build_intensity_map()

    for text in (" Grattis ", " Ludvig ", "  på  ", "födelse-", "dagen"):
        time.sleep(0.3)
        check_quit()
        clear_screen()
        time.sleep(0.1)
        fade_in_text_in_console(text, intensity_map)


    for image_name in ["balloons.png",
                       "Nalle.jpg",
                       "fat cat.jpg", "jkjk"]:
        try:
            image = pygame.image.load(image_name)
        except pygame.error:
            # Probably a missing image file. Try the next one.
            continue
        check_quit()
        clear_screen()
        draw_image_on_console(image, intensity_map)
        time.sleep(4)
            
                                                

if __name__ == "__main__":
    main()

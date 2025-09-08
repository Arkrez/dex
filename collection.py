# add near the top with other imports
from enum import Enum
# collection.py
import pygame, os, textwrap
from pathlib import Path
import csv
from collections import OrderedDict
import json

od = OrderedDict()

# sample data
BASE_DIR = Path(__file__).parent
ANIMALS = []
with open(BASE_DIR / "models" / "animals.json", "r", encoding="utf-8") as f:
    ANIMALS = json.load(f)
SILHOUETTE = str(Path(__file__).parent / "assets" / "silhouette.jpg")  # add a silhouette image to repo

PANEL_BG = (24, 26, 32)
LIST_BG = (16, 18, 22)
HILITE = (60, 120, 250)
FG = (235, 235, 235)
MUTED = (180, 184, 192)
BORDER = (48, 52, 60)
# drop-in replacement for CollectionPage
# new small enum for clarity/reuse
class Focus(Enum):
    DESC = 0   # left panel: description
    LIST = 1   # right panel: rows

class CollectionPage:
    SCROLL_LINE_STEP = 1       # lines per up/down when in DESC focus
    LIST_ROW_H = 48
    LIST_PAD = 18
    DESC_SIDE_PAD = 16
    DESC_LINE_SPACING = 4

    def __init__(self, screen, discovered, db):
        self.screen = screen
        self.db = db
        self.discovered = discovered  # set[str] of discovered names
        self.font_title = pygame.font.SysFont("DejaVuSans", 34, bold=True)
        self.font_body = pygame.font.SysFont("DejaVuSans", 24)
        self.font_list = pygame.font.SysFont("DejaVuSans", 28)
        self.sel = 0
        self.scroll = 0
        self.cache = {}
        self.focus = Focus.LIST
        self.desc_scroll_lines = 0
        self._wrapped_cache = {}  # {(name,bool_discovered,wrap_w,desc_text)->[lines]}
        
    def draw(self):
        w, h = self.screen.get_size()
        left_w = w // 2
        right_x = left_w
        self.screen.fill(LIST_BG)
        pygame.draw.rect(self.screen, PANEL_BG, (0, 0, left_w, h))
        pygame.draw.line(self.screen, BORDER, (left_w, 0), (left_w, h), 2)

        item = ANIMALS[self.sel]
        discovered = (item["name"] in self.discovered)

        # image
        top_rect = pygame.Rect(0, 0, left_w, h // 2)
        if discovered:
            entry = self.db.get(item["name"])
            imgs = entry.get("images", []) if isinstance(entry, dict) else []
            img_path = imgs[-1] if imgs else SILHOUETTE
        else:
            img_path = SILHOUETTE
        key = (img_path, top_rect.size)
        if key not in self.cache:
            self.cache[key] = load_image(img_path, top_rect.size)
        self.screen.blit(self.cache[key], top_rect.topleft)

        # description panel
        bot_rect = pygame.Rect(0, h // 2, left_w, h // 2)
        pygame.draw.rect(self.screen, PANEL_BG, bot_rect)
        pygame.draw.line(self.screen, BORDER, (0, h // 2), (left_w, h // 2), 2)

        # focus ring for description when active
        if self.focus == Focus.DESC:
            pygame.draw.rect(self.screen, HILITE, bot_rect.inflate(-4, -4), width=2, border_radius=10)

        title = item["name"] if discovered else "???"
        desc = item["description"] if discovered else "???"
        title_surf = self.font_title.render(title, True, FG)
        self.screen.blit(title_surf, (bot_rect.x + self.DESC_SIDE_PAD, bot_rect.y + 14))

        wrap_w = left_w - self.DESC_SIDE_PAD * 2
        text_top_y = bot_rect.y + 14 + title_surf.get_height() + 10

        lines = self._wrap_desc(item["name"], discovered, wrap_w, desc)
        line_h = self.font_body.get_height() + self.DESC_LINE_SPACING
        max_visible = max(0, (bot_rect.bottom - text_top_y - 8) // line_h)
        self.desc_scroll_lines = max(0, min(self.desc_scroll_lines, max(0, len(lines) - max_visible)))

        # clip drawing to description text area
        clip_rect = pygame.Rect(bot_rect.x + self.DESC_SIDE_PAD, text_top_y, wrap_w, max_visible * line_h)
        prev_clip = self.screen.get_clip()
        self.screen.set_clip(clip_rect)

        y = text_top_y
        for i in range(self.desc_scroll_lines, min(len(lines), self.desc_scroll_lines + max_visible)):
            line_surf = self.font_body.render(lines[i], True, MUTED)
            self.screen.blit(line_surf, (bot_rect.x + self.DESC_SIDE_PAD, y))
            y += line_h

        self.screen.set_clip(prev_clip)

        # right list (show names if discovered, else ???)
        view_rows = (h - self.LIST_PAD * 2) // self.LIST_ROW_H
        self.scroll = max(0, min(self.scroll, max(0, len(ANIMALS) - view_rows)))
        start = self.scroll
        end = min(len(ANIMALS), start + view_rows)
        y = self.LIST_PAD
        for i in range(start, end):
            focused_row = (i == self.sel)
            a = ANIMALS[i]
            label = f"{i} : " + (a["name"] if a["name"] in self.discovered else "???")
            bg = pygame.Rect(right_x + self.LIST_PAD, y, w - right_x - self.LIST_PAD * 2, self.LIST_ROW_H - 8)
            if focused_row and self.focus == Focus.LIST:
                pygame.draw.rect(self.screen, HILITE, bg, border_radius=12)
            txt = self.font_list.render(label, True, (255, 255, 255) if (focused_row and self.focus == Focus.LIST) else FG)
            self.screen.blit(txt, (bg.x + 12, bg.y + (bg.height - txt.get_height()) // 2))
            y += self.LIST_ROW_H

        pygame.display.flip()

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                return False

            # focus switching
            if e.key in (pygame.K_RIGHT,):
                self.focus = Focus.LIST
                return True
            if e.key in (pygame.K_LEFT,):
                self.focus = Focus.DESC
                return True

            # behavior depends on focus
            if self.focus == Focus.LIST:
                if e.key in (pygame.K_UP, pygame.K_w):
                    self.sel = (self.sel - 1) % len(ANIMALS)
                    self._ensure_visible(-1)
                    self._reset_desc_scroll()
                elif e.key in (pygame.K_DOWN, pygame.K_s):
                    self.sel = (self.sel + 1) % len(ANIMALS)
                    self._ensure_visible(+1)
                    self._reset_desc_scroll()
            else:  # Focus.DESC -> scroll description
                if e.key in (pygame.K_UP, pygame.K_w):
                    self._scroll_desc(-self.SCROLL_LINE_STEP)
                elif e.key in (pygame.K_DOWN, pygame.K_s):
                    self._scroll_desc(+self.SCROLL_LINE_STEP)
        return True

    def _reset_desc_scroll(self):
        self.desc_scroll_lines = 0

    def _scroll_desc(self, delta_lines: int):
        # compute bounds based on current item and layout
        w, h = self.screen.get_size()
        left_w = w // 2
        bot_rect = pygame.Rect(0, h // 2, left_w, h // 2)
        wrap_w = left_w - self.DESC_SIDE_PAD * 2

        item = ANIMALS[self.sel]
        discovered = (item["name"] in self.discovered)
        desc = item["description"] if discovered else "???"
        lines = self._wrap_desc(item["name"], discovered, wrap_w, desc)

        title_h = self.font_title.get_height()
        text_top_y = bot_rect.y + 14 + title_h + 10
        line_h = self.font_body.get_height() + self.DESC_LINE_SPACING
        max_visible = max(0, (bot_rect.bottom - text_top_y - 8) // line_h)
        max_scroll = max(0, len(lines) - max_visible)

        self.desc_scroll_lines = max(0, min(self.desc_scroll_lines + delta_lines, max_scroll))

    def _wrap_desc(self, name: str, discovered: bool, wrap_w: int, desc_text: str):
        key = (name, discovered, wrap_w, desc_text)
        cached = self._wrapped_cache.get(key)
        if cached is not None:
            return cached
        # heuristic: characters per line based on width and average char width (~0.55em of font size)
        approx_chars = max(20, wrap_w // 12)
        lines = textwrap.wrap(desc_text, width=approx_chars)
        self._wrapped_cache[key] = lines
        return lines

    def _ensure_visible(self, _):
        h = self.screen.get_height()
        view_rows = (h - self.LIST_PAD * 2) // self.LIST_ROW_H
        if self.sel < self.scroll:
            self.scroll = self.sel
        elif self.sel >= self.scroll + view_rows:
            self.scroll = self.sel - view_rows + 1


def load_image(path, size):
    try:
        img = pygame.image.load(path).convert()
        return pygame.transform.smoothscale(img, size)
    except Exception:
        surf = pygame.Surface(size)
        surf.fill((40, 44, 52))
        return surf
def run(screen, discovered, db):
    clock = pygame.time.Clock()
    page = CollectionPage(screen, discovered, db)

    pygame.key.set_repeat(200, 25)

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return False
            running = page.handle_event(e)
        page.draw()
        clock.tick(60)
    return True
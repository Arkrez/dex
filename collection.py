# file: collection.py
import pygame, os, textwrap

# --- sample data (replace paths/descriptions as needed) ---
ANIMALS = [
    {"name": "Bald Eagle", "image": "assets/bald_eagle.jpg",
     "desc": "Large raptor found near coasts and rivers; white head/tail, yellow beak."},
    {"name": "Black Bear", "image": "assets/black_bear.jpg",
     "desc": "Omnivore of forests; color varies from black to cinnamon; short, curved claws."},
    {"name": "Roosevelt Elk", "image": "assets/roosevelt_elk.jpg",
     "desc": "Largest North American elk subspecies; rainforests of the Olympic Peninsula."},
    {"name": "Pacific Wren", "image": "assets/pacific_wren.jpg",
     "desc": "Tiny, energetic; explosive song; dense conifer undergrowth."},
    {"name": "Douglas Squirrel", "image": "assets/douglas_squirrel.jpg",
     "desc": "Small tree squirrel; sharp chatter; feeds on conifer seeds and fungi."},
]

PANEL_BG = (24, 26, 32)
LIST_BG  = (16, 18, 22)
HILITE   = (60, 120, 250)
FG       = (235, 235, 235)
MUTED    = (180, 184, 192)
BORDER   = (48, 52, 60)

def load_image(path, size):
    try:
        img = pygame.image.load(path).convert()
        return pygame.transform.smoothscale(img, size)
    except Exception:
        surf = pygame.Surface(size)
        surf.fill((40, 44, 52))
        pygame.draw.line(surf, (90, 95, 105), (0,0), (size[0], size[1]), 4)
        pygame.draw.line(surf, (90, 95, 105), (size[0],0), (0, size[1]), 4)
        return surf

class CollectionPage:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.SysFont("DejaVuSans", 34, bold=True)
        self.font_body  = pygame.font.SysFont("DejaVuSans", 24)
        self.font_list  = pygame.font.SysFont("DejaVuSans", 28)
        self.sel = 0
        self.scroll = 0
        self.cache = {}

    def draw(self):
        w, h = self.screen.get_size()
        left_w = w // 2
        right_x = left_w

        # panels
        self.screen.fill(LIST_BG)
        pygame.draw.rect(self.screen, PANEL_BG, (0, 0, left_w, h))
        pygame.draw.rect(self.screen, LIST_BG,  (right_x, 0, w - right_x, h))
        pygame.draw.line(self.screen, BORDER, (left_w, 0), (left_w, h), 2)

        # current item
        item = ANIMALS[self.sel]
        top_rect  = pygame.Rect(0, 0, left_w, h//2)
        bot_rect  = pygame.Rect(0, h//2, left_w, h//2)

        # image (cached)
        key = (item["image"], top_rect.size)
        if key not in self.cache:
            self.cache[key] = load_image(item["image"], top_rect.size)
        self.screen.blit(self.cache[key], top_rect.topleft)

        # description
        pygame.draw.rect(self.screen, PANEL_BG, bot_rect)
        pygame.draw.line(self.screen, BORDER, (0, h//2), (left_w, h//2), 2)

        title_surf = self.font_title.render(item["name"], True, FG)
        self.screen.blit(title_surf, (bot_rect.x + 16, bot_rect.y + 14))

        wrap_w = left_w - 32
        lines = textwrap.wrap(item["desc"], width=max(20, wrap_w // 12))
        y = bot_rect.y + 14 + title_surf.get_height() + 10
        for line in lines:
            line_surf = self.font_body.render(line, True, MUTED)
            self.screen.blit(line_surf, (bot_rect.x + 16, y))
            y += line_surf.get_height() + 4

        # right list
        list_pad = 18
        row_h = 48
        view_rows = (h - list_pad*2) // row_h
        self.scroll = max(0, min(self.scroll, max(0, len(ANIMALS) - view_rows)))
        start = self.scroll
        end = min(len(ANIMALS), start + view_rows)

        y = list_pad
        for i in range(start, end):
            focused = (i == self.sel)
            label = ANIMALS[i]["name"]
            bg_rect = pygame.Rect(right_x + list_pad, y, w - right_x - list_pad*2, row_h - 8)
            if focused:
                pygame.draw.rect(self.screen, HILITE, bg_rect, border_radius=12)
            txt = self.font_list.render(label, True, (255,255,255) if focused else FG)
            self.screen.blit(txt, (bg_rect.x + 12, bg_rect.y + (bg_rect.height - txt.get_height())//2))
            y += row_h

        pygame.display.flip()

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                return False
            elif e.key in (pygame.K_UP, pygame.K_w):
                self.sel = (self.sel - 1) % len(ANIMALS)
                self._ensure_visible(-1)
            elif e.key in (pygame.K_DOWN, pygame.K_s):
                self.sel = (self.sel + 1) % len(ANIMALS)
                self._ensure_visible(+1)
            elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                pass  # selection already reflected on left; hook action if needed
        return True

    def _ensure_visible(self, direction):
        # keep selection within visible window on right list
        h = self.screen.get_height()
        row_h = 48
        list_pad = 18
        view_rows = (h - list_pad*2) // row_h
        if self.sel < self.scroll:
            self.scroll = self.sel
        elif self.sel >= self.scroll + view_rows:
            self.scroll = self.sel - view_rows + 1

def run(screen):
    clock = pygame.time.Clock()
    page = CollectionPage(screen)
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return False
            running = page.handle_event(e)
        page.draw()
        clock.tick(60)
    return True

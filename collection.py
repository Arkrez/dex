# collection.py
import pygame, os, textwrap
from pathlib import Path

# sample data
ANIMALS = [
    {"name":"Bald Eagle","image":"assets/bald_eagle.jpg","desc":"Large raptor near coasts/rivers."},
    {"name":"Black Bear","image":"assets/black_bear.jpg","desc":"Omnivore of forests; color varies."},
    {"name":"Roosevelt Elk","image":"assets/roosevelt_elk.jpg","desc":"Largest elk; Olympic rainforests."},
    {"name":"Pacific Wren","image":"assets/pacific_wren.jpg","desc":"Tiny; explosive song; conifer undergrowth."},
    {"name":"Douglas Squirrel","image":"assets/douglas_squirrel.jpg","desc":"Tree squirrel; chatter; conifer seeds."},
]

SILHOUETTE = str(Path(__file__).parent / "assets" / "silhouette.jpg")  # add a silhouette image to repo

PANEL_BG=(24,26,32); LIST_BG=(16,18,22); HILITE=(60,120,250); FG=(235,235,235); MUTED=(180,184,192); BORDER=(48,52,60)

def load_image(path, size):
    try:
        img = pygame.image.load(path).convert()
        return pygame.transform.smoothscale(img, size)
    except Exception:
        surf = pygame.Surface(size); surf.fill((40,44,52))
        return surf

class CollectionPage:
    def __init__(self, screen, discovered):
        self.screen = screen
        self.discovered = discovered  # set[str] of discovered names
        self.font_title = pygame.font.SysFont("DejaVuSans", 34, bold=True)
        self.font_body  = pygame.font.SysFont("DejaVuSans", 24)
        self.font_list  = pygame.font.SysFont("DejaVuSans", 28)
        self.sel = 0; self.scroll = 0; self.cache = {}

    def draw(self):
        w,h = self.screen.get_size(); left_w=w//2; right_x=left_w
        self.screen.fill(LIST_BG)
        pygame.draw.rect(self.screen, PANEL_BG, (0,0,left_w,h))
        pygame.draw.line(self.screen, BORDER, (left_w,0),(left_w,h),2)

        item = ANIMALS[self.sel]
        discovered = (item["name"] in self.discovered)

        # image
        top_rect = pygame.Rect(0,0,left_w,h//2)
        img_path = item["image"] if discovered else SILHOUETTE
        key = (img_path, top_rect.size)
        if key not in self.cache: self.cache[key] = load_image(img_path, top_rect.size)
        self.screen.blit(self.cache[key], top_rect.topleft)

        # description panel
        bot_rect = pygame.Rect(0,h//2,left_w,h//2)
        pygame.draw.rect(self.screen, PANEL_BG, bot_rect)
        pygame.draw.line(self.screen, BORDER, (0,h//2),(left_w,h//2),2)

        title = item["name"] if discovered else "???"
        desc  = item["desc"] if discovered else "???"
        title_surf = self.font_title.render(title, True, FG)
        self.screen.blit(title_surf, (bot_rect.x+16, bot_rect.y+14))

        wrap_w = left_w-32
        lines = textwrap.wrap(desc, width=max(20, wrap_w//12))
        y = bot_rect.y + 14 + title_surf.get_height() + 10
        for line in lines:
            line_surf = self.font_body.render(line, True, MUTED)
            self.screen.blit(line_surf, (bot_rect.x+16, y)); y += line_surf.get_height()+4

        # right list (show names if discovered, else ???)
        list_pad=18; row_h=48
        view_rows = (h - list_pad*2)//row_h
        self.scroll = max(0, min(self.scroll, max(0, len(ANIMALS)-view_rows)))
        start=self.scroll; end=min(len(ANIMALS), start+view_rows)
        y=list_pad
        for i in range(start,end):
            focused=(i==self.sel); a=ANIMALS[i]
            label = a["name"] if a["name"] in self.discovered else "???"
            bg = pygame.Rect(right_x+list_pad, y, w-right_x-list_pad*2, row_h-8)
            if focused: pygame.draw.rect(self.screen, HILITE, bg, border_radius=12)
            txt = self.font_list.render(label, True, (255,255,255) if focused else FG)
            self.screen.blit(txt, (bg.x+12, bg.y+(bg.height-txt.get_height())//2))
            y += row_h

        pygame.display.flip()

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE): return False
            elif e.key in (pygame.K_UP, pygame.K_w):
                self.sel = (self.sel-1) % len(ANIMALS); self._ensure_visible(-1)
            elif e.key in (pygame.K_DOWN, pygame.K_s):
                self.sel = (self.sel+1) % len(ANIMALS); self._ensure_visible(+1)
        return True

    def _ensure_visible(self, _):
        h=self.screen.get_height(); row_h=48; list_pad=18
        view_rows=(h - list_pad*2)//row_h
        if self.sel < self.scroll: self.scroll=self.sel
        elif self.sel >= self.scroll+view_rows: self.scroll=self.sel - view_rows + 1

def run(screen, discovered):
    clock = pygame.time.Clock()
    page = CollectionPage(screen, discovered)
    running=True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return False
            running = page.handle_event(e)
        page.draw(); clock.tick(60)
    return True

import pygame, sys, os
from pathlib import Path
from classifier import SpeciesClassifier
import collection
from discovered import load_db, discovered_names   # use DB helpers
from camera import CameraView

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("DejaVuSans", 36, bold=True)
        self.items = [("Browse Collection", self.goto_collection),
                      ("Camera", self.goto_camera)]
        self.sel = 0
        # init discovered from DB
        self.db = load_db()
        self.discovered = discovered_names(self.db)

    def draw(self):
        self.screen.fill((0,0,0))
        for i, (text, _) in enumerate(self.items):
            color = (255,255,0) if i == self.sel else (200,200,200)
            label = self.font.render(text, True, color)
            self.screen.blit(label, (100, 100 + i*60))
        pygame.display.flip()

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_UP: self.sel = (self.sel-1) % len(self.items)
            elif e.key == pygame.K_DOWN: self.sel = (self.sel+1) % len(self.items)
            elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.items[self.sel][1]()

    def goto_collection(self):
        collection.run(self.screen, self.discovered)

    def goto_camera(self):
        base = Path(__file__).parent
        model_path = base / "models" / "inat.tflite"
        csv_path   = base / "models" / "taxonomy.csv"   # your CSV mapping
        clf = SpeciesClassifier(str(model_path), str(csv_path))

        # save raw captures anywhere (they’ll be copied into ./discovered/ by add_discovery)
        outdir = os.path.expanduser("~/Pictures")
        cam = CameraView(outdir, width=1024, height=768)
        cam.run(self.screen, clf)

        # refresh discovered after camera session (camera updates DB itself)
        from discovered import load_db, discovered_names
        self.db = load_db()
        self.discovered = discovered_names(self.db)

def run():
    pygame.init()
    screen = pygame.display.set_mode((1280, 800))  # windowed for dev; switch to FULLSCREEN on Pi
    pygame.display.set_caption("DEX")
    menu = MainMenu(screen)
    clock = pygame.time.Clock()
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                running = False
            else:
                menu.handle_event(e)
        menu.draw()
        clock.tick(30)
    pygame.quit(); sys.exit()

if __name__ == "__main__":
    run()

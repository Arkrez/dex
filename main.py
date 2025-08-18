import pygame, sys, os
from pathlib import Path
from classifier import SpeciesClassifier
import collection
from discovered import load as load_disc, save as save_disc
from camera import CameraView  # <-- new

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("DejaVuSans", 36, bold=True)
        self.items = [("Browse Collection", self.goto_collection),
                      ("Camera", self.goto_camera)]  # renamed/added
        self.sel = 0
        self.discovered = load_disc()

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
        BASE_DIR = Path(__file__).parent
        MODEL_PATH = BASE_DIR / "models" / "inat.tflite"
        LABELS_PATH = BASE_DIR / "models" / "labels.csv"
        clf = SpeciesClassifier(str(MODEL_PATH), str(LABELS_PATH))

        outdir = os.path.expanduser("~/Pictures")
        cam = CameraView(outdir, width=1024, height=768)
        cam.run(self.screen, clf)

        # if a confident result was produced in the last shot, record it
        if cam.last_result:
            label, prob = cam.last_result
            if prob >= 0.80 and label not in self.discovered:
                self.discovered.add(label)
                save_disc(self.discovered)

def run():
    pygame.init()
    screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
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
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    run()

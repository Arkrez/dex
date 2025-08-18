import pygame, sys, os, subprocess
from pathlib import Path
from classifier import SpeciesClassifier
import collection
from discovered import load as load_disc, save as save_disc

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("DejaVuSans", 36, bold=True)
        self.items = [("Browse Collection", self.goto_collection),
                      ("Take a Screenshot", self.action_take_screenshot)]
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

    def action_take_screenshot(self):
        BASE_DIR = Path(__file__).parent
        MODEL_PATH = BASE_DIR / "models" / "inat.tflite"
        LABELS_PATH = BASE_DIR / "models" / "labels.txt"
        CLF = SpeciesClassifier(str(MODEL_PATH), str(LABELS_PATH))

        outdir = os.path.expanduser("~/Pictures"); os.makedirs(outdir, exist_ok=True)
        img = os.path.join(outdir, "capture.jpg")

        # Use rpicam-still (replacement for libcamera-still)
        subprocess.run([
            "rpicam-still", "--nopreview",
            "--output", img, "--timeout", "1000",
            "--width", "1024", "--height", "768"
        ], check=True)

        label, prob = CLF.classify(img, top_k=1)[0]
        print(f"Top: {label}  {prob:.2%}")

        if prob >= 0.80 and label not in self.discovered:
            self.discovered.add(label)
            save_disc(self.discovered)
            print(f"Discovered: {label}")

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

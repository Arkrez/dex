import pygame
import sys
import collection  # your other page
import os, subprocess

from classifier import SpeciesClassifier

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("DejaVuSans", 36, bold=True)
        self.items = [("Browse Collection", self.goto_collection),
                      ("Take a Screenshot", self.action_take_screenshot)]
        self.sel = 0

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
        collection.run(self.screen)  # switch to collection page


    def action_take_screenshot(self):
        CLF = SpeciesClassifier("/home/pi/models/inat.tflite", "/home/pi/models/labels.txt")

        outdir = os.path.expanduser("~/Pictures"); os.makedirs(outdir, exist_ok=True)
        img = os.path.join(outdir, "capture.jpg")
        subprocess.run(["libcamera-still", "-n", "-o", img, "-t", "1000", "--width", "1024", "--height", "768"], check=True)
        preds = CLF.classify(img, top_k=3)
        print("Top:", preds[0])  # TODO: render on-screen in your UI


def run():
    pygame.init()
    screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
    menu = MainMenu(screen)
    clock = pygame.time.Clock()

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                running = False
            else:
                menu.handle_event(e)
        menu.draw()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    run()

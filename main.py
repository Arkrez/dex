import pygame, sys, os
from pathlib import Path
import collection
from discovered import load_db, discovered_names   # use DB helpers
from camera import CameraView
import argparse
import asyncio
import sys

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
        collection.run(self.screen, self.discovered, self.db)

    def goto_camera(self):
        # save raw captures anywhere (they’ll be copied into ./discovered/ by add_discovery)
        BASE = Path(__file__).resolve().parent
        outdir = os.path.expanduser(str(Path(__file__).parent / "assets"))
        cam = CameraView(outdir, width=800, height=480)
        cam.run(self.screen)

        # refresh discovered after camera session (camera updates DB itself)
        from discovered import load_db, discovered_names
        self.db = load_db()
        self.discovered = discovered_names(self.db)

def run():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)  # windowed for dev; switch to FULLSCREEN on Pi
    pygame.display.set_caption("DEX")
    menu = MainMenu(screen)
    clock = pygame.time.Clock()



# Define CLI arguments


# Main async loop
async def main():
    print(f"App started in mode: {args.mode or 'idle'}")
    loop = asyncio.get_event_loop()
    parser = argparse.ArgumentParser(description="Control a Python app via CLI.")
    parser.add_argument("--mode", choices=["start", "stop"], help="Initial mode")
    args = parser.parse_args()
    # Listen for stdin commands

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                running = False
            else:
                menu.handle_event(e)

        print("Waiting for command (type 'quit' to exit):")
        cmd = await loop.run_in_executor(None, sys.stdin.readline)
        cmd = cmd.strip()
        e = {}
        e.type = pygame.KEYDOWN
            
        if cmd == "w":
            e.key = pygame.K_UP
        elif cmd == "s":
            e.key = pygame.DOWN
        elif cmd == "c":
            e.key = pygame.RETURN
        elif cmd == " ":
            pygame.K_SPACE
        else:
            print(f"Unknown command: {cmd}")
        menu.handle_event(e)
        menu.draw()
        clock.tick(30)
    pygame.quit(); sys.exit()

if __name__ == "__main__":
    run()

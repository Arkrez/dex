# camera.py
import os, time
from pathlib import Path
import numpy as np
import pygame
from picamera2 import Picamera2, Preview

class CameraView:
    def __init__(self, outdir: str, width=1024, height=768):
        self.outdir = outdir
        Path(outdir).mkdir(parents=True, exist_ok=True)
        self.width, self.height = width, height
        self.picam = None
        self.last_photo_path = None
        self.last_result = None  # (label, prob) or None
        self.just_captured_ts = 0.0

    def _init_camera(self):
        if self.picam: return
        self.picam = Picamera2()
        config = self.picam.create_preview_configuration(
            main={"size": (self.width, self.height), "format": "RGB888"}
        )
        self.picam.configure(config)
        self.picam.start()

    def _frame_surface(self):
        # Get latest frame (RGB888 HxWx3) and convert to pygame surface
        frame = self.picam.capture_array()  # numpy array
        # Pygame expects (W,H); rotate if needed to match orientation
        surf = pygame.image.frombuffer(frame.tobytes(), (frame.shape[1], frame.shape[0]), "RGB")
        return surf

    def _flash_notification(self, screen):
        # subtle shutter flash for 150 ms
        if time.time() - self.just_captured_ts < 0.15:
            s = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            s.fill((255, 255, 255, 40))  # translucent white
            screen.blit(s, (0, 0))

    def run(self, screen, classifier):
        self._init_camera()
        clock = pygame.time.Clock()
        font = pygame.font.SysFont("DejaVuSans", 28, bold=True)

        showing_photo = False
        photo_surface = None

        running = True
        while running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        running = False
                    elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                        # capture still, save, classify, then show still and result overlay
                        ts = time.strftime("%Y%m%d_%H%M%S")
                        img_path = os.path.join(self.outdir, f"capture_{ts}.jpg")
                        self.picam.capture_file(img_path)
                        self.last_photo_path = img_path
                        self.just_captured_ts = time.time()

                        # Build pygame surface from saved image for stable orientation
                        photo = pygame.image.load(img_path)
                        photo = pygame.transform.smoothscale(photo, screen.get_size())
                        photo_surface = photo
                        showing_photo = True

                        label, prob = classifier.classify(img_path, top_k=1)[0]
                        self.last_result = (label, prob)

            screen.fill((0, 0, 0))

            if showing_photo and photo_surface is not None:
                screen.blit(photo_surface, (0, 0))
                # result badge
                if self.last_result:
                    label, prob = self.last_result
                    txt = f"{label}  {prob:.2%}"
                    pad = 10
                    t = font.render(txt, True, (255, 255, 255))
                    bg = pygame.Surface((t.get_width() + pad * 2, t.get_height() + pad * 2), pygame.SRCALPHA)
                    bg.fill((0, 0, 0, 150))
                    screen.blit(bg, (20, 20))
                    screen.blit(t, (20 + pad, 20 + pad))
                    # green check if >=0.80
                    if prob >= 0.80:
                        ok = font.render("✓", True, (0, 255, 0))
                        screen.blit(ok, (20 + bg.get_width() + 8, 20))
            else:
                # live view
                frame_surf = self._frame_surface()
                frame_surf = pygame.transform.smoothscale(frame_surf, screen.get_size())
                screen.blit(frame_surf, (0, 0))
                hint = font.render("Press ⏎ to capture • ESC to exit", True, (255, 255, 255))
                screen.blit(hint, (20, screen.get_height() - hint.get_height() - 20))

            self._flash_notification(screen)
            pygame.display.flip()
            clock.tick(30)

        if self.picam:
            self.picam.stop()
            self.picam.close()
            self.picam = None

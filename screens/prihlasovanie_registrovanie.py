import pygame
import pyrebase
import sys
from core.config import FONT_DIR
from core.auth_manager import set_user
import os

pygame.init()

# ---------------- Firebase ----------------
firebaseConfig = {
    'apiKey': "AIzaSyDBM55pRHOJRkPyE19YlSaIVuREb8VOuhY",
    'authDomain': "spacerider-78a3d.firebaseapp.com",
    "databaseURL": "",
    'projectId': "spacerider-78a3d",
    'storageBucket': "spacerider-78a3d.firebasestorage.app",
    'messagingSenderId': "721946961756",
    'appId': "1:721946961756:web:ecb0b1eb8960f888b74399",
    'measurementId': "G-PDYNK4743J"
}
from core.firebase_init import auth


# ---------------- Farby ----------------
WHITE = (255, 255, 255)
SPACE_TOP = (10, 0, 40)
SPACE_BOTTOM = (0, 0, 20)
GRAY_TEXT = (200, 200, 200)
RED_TEXT = (255, 100, 100)
SUCCESS_TEXT = (100, 255, 120)


# ---------------- InputBox ----------------
class InputBox:
    def __init__(self, x, y, w, h, placeholder='', font=None, is_password=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.base_width = w
        self.text = ''
        self.placeholder = placeholder
        self.font = font
        self.is_password = is_password
        self.active = False

        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_interval = 500

        self.show_text = False
        self.show_toggle = is_password

        # Pridáme pozíciu kurzora
        self.cursor_pos = 0

        BASE_DIR = os.path.dirname(os.path.dirname(__file__))
        IMG_DIR = os.path.join(BASE_DIR, "assets", "img")

        self.eye_image_visible = pygame.transform.scale(
            pygame.image.load(os.path.join(IMG_DIR, "vidim.png")).convert_alpha(), (30, 30)
        )
        self.eye_image_hidden = pygame.transform.scale(
            pygame.image.load(os.path.join(IMG_DIR, "nevidim.png")).convert_alpha(), (30, 30)
        )

        self.txt_surface = self.font.render('', True, WHITE)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)

            if self.show_toggle:
                eye_rect = pygame.Rect(
                    self.rect.right - 40,
                    self.rect.y + (self.rect.height - 25) // 2,
                    30, 30
                )
                if eye_rect.collidepoint(event.pos):
                    self.show_text = not self.show_text
                    self.update_surface()

        if event.type == pygame.KEYDOWN and self.active:

            # ⛔ OVLÁDACIE KLÁVESY
            if event.key == pygame.K_LEFT:
                self.cursor_pos = max(0, self.cursor_pos - 1)
                return

            if event.key == pygame.K_RIGHT:
                self.cursor_pos = min(len(self.text), self.cursor_pos + 1)
                return

            if event.key == pygame.K_BACKSPACE:
                if self.cursor_pos > 0:
                    self.text = self.text[:self.cursor_pos - 1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1
                    self.update_surface()
                return  # ⛔ ZABRÁNI PRIDANIU '\x08'

            if event.key == pygame.K_DELETE:
                if self.cursor_pos < len(self.text):
                    self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos + 1:]
                    self.update_surface()
                return

            # ⛔ ignoruj netlačiteľné znaky
            if event.unicode == "" or event.unicode == "\x08":
                return

            # ✅ VLOŽENIE ZNAKU
            self.text = self.text[:self.cursor_pos] + event.unicode + self.text[self.cursor_pos:]
            self.cursor_pos += 1
            self.update_surface()

    def update_surface(self):
        if self.is_password and not self.show_text:
            display = "*" * len(self.text)
        else:
            display = self.text

        # ✅ Ak je prázdny, použijeme medzeru, aby Pygame nespadol
        if display == "":
            display = " "

        self.txt_surface = self.font.render(display, True, WHITE)

        # DYNAMICKÉ ROZŠIROVANIE DO OBOCH STRÁN
        text_width = self.txt_surface.get_width() + 70
        new_width = max(self.base_width, text_width)

        # 🔥 uložíme stred aby sa box rozširoval symetricky
        center_x = self.rect.centerx
        self.rect.width = new_width
        self.rect.centerx = center_x

    def update(self, dt):
        if self.active:
            self.cursor_timer += dt
            if self.cursor_timer >= self.cursor_interval:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0
        else:
            self.cursor_visible = False

    def draw(self, screen):
        pygame.draw.rect(screen, (50, 0, 70), self.rect, border_radius=8)
        pygame.draw.rect(screen, WHITE, self.rect, 3, border_radius=8)

        text_x = self.rect.x + 10
        text_y = self.rect.y + (self.rect.height - self.font.get_height()) // 2

        if self.text == '' and not self.active:
            ph = self.font.render(self.placeholder, True, GRAY_TEXT)
            screen.blit(ph, (text_x, text_y))
        else:
            screen.blit(self.txt_surface, (text_x, text_y))
            if self.cursor_visible and self.active:
                # 🔹 pozícia kurzora podľa cursor_pos
                if self.is_password and not self.show_text:
                    cursor_x = text_x + self.font.size("*" * self.cursor_pos)[0]
                else:
                    cursor_x = text_x + self.font.size(self.text[:self.cursor_pos])[0]

                pygame.draw.line(
                    screen, WHITE,
                    (cursor_x, text_y),
                    (cursor_x, text_y + self.font.get_height()), 2
                )

        if self.show_toggle:
            eye_img = self.eye_image_visible if self.show_text else self.eye_image_hidden
            screen.blit(
                eye_img,
                (self.rect.right - 40, self.rect.y + (self.rect.height - 25)//2)
            )


# ---------------- UI ----------------
def draw_gradient_background(surface, top, bottom):
    w, h = surface.get_size()
    for y in range(h):
        r = top[0] + (bottom[0] - top[0]) * y / h
        g = top[1] + (bottom[1] - top[1]) * y / h
        b = top[2] + (bottom[2] - top[2]) * y / h
        pygame.draw.line(surface, (int(r), int(g), int(b)), (0, y), (w, y))

def draw_gradient_button(surface, rect, text, font, c1, c2):
    grad = pygame.Surface((rect.width, rect.height))
    for y in range(rect.height):
        r = c1[0] + (c2[0] - c1[0]) * y / rect.height
        g = c1[1] + (c2[1] - c1[1]) * y / rect.height
        b = c1[2] + (c2[2] - c1[2]) * y / rect.height
        pygame.draw.line(grad, (int(r), int(g), int(b)), (0, y), (rect.width, y))
    surface.blit(grad, rect)
    pygame.draw.rect(surface, WHITE, rect, 3, border_radius=8)
    txt = font.render(text, True, WHITE)
    surface.blit(txt, txt.get_rect(center=rect.center))

# ---------------- Login / Register Screen ----------------
def login_screen(screen, clock):
    voyager = FONT_DIR + "/VOYAGER.ttf"
    TITLE = pygame.font.Font(voyager, 80)
    FONT = pygame.font.Font(voyager, 45)
    SMALL = pygame.font.Font(voyager, 28)

    w, h = screen.get_size()
    offset = -50

    email_box = InputBox(0, h // 2 - 120 + offset, 700, 60, "Email", SMALL)
    email_box.rect.centerx = w // 2

    password_box = InputBox(0, h // 2 - 40 + offset, 700, 60, "Heslo", SMALL, True)
    password_box.rect.centerx = w // 2

    confirm_box = InputBox(0, h // 2 + 40 + offset, 700, 60, "Zopakuj heslo", SMALL, True)
    confirm_box.rect.centerx = w // 2

    login_btn = pygame.Rect(0, 0, 280, 60)
    back_btn = pygame.Rect(40, h-90, 150, 50)

    mode = "login"
    message = ""
    message_color = RED_TEXT

    register_text = "Este nemas ucet? Registruj sa hned!"
    register_surf = SMALL.render(register_text, True, WHITE)

    # ---------------- Funkcia na login/register ----------------
    def attempt_login_or_register():
        nonlocal message, message_color, mode

        message = ""  # reset správy pred pokusom
        message_color = RED_TEXT

        try:
            if mode == "login":
                user = auth.sign_in_with_email_and_password(
                    email_box.text,
                    password_box.text
                )

                set_user(user)
                return True

            else:  # register
                if password_box.text != confirm_box.text:
                    message = "Hesla sa nezhoduju!"
                    message_color = RED_TEXT
                    return False  # explicitne False

                auth.create_user_with_email_and_password(
                    email_box.text,
                    password_box.text
                )

                message = "Uspesne si sa zaregistroval!"
                message_color = SUCCESS_TEXT

                mode = "login"
                email_box.text = ""
                password_box.text = ""
                confirm_box.text = ""
                email_box.cursor_pos = 0
                password_box.cursor_pos = 0
                confirm_box.cursor_pos = 0
                email_box.update_surface()
                password_box.update_surface()
                confirm_box.update_surface()
                return False

        except Exception as e:
            err_str = str(e)
            message_color = RED_TEXT

            if "EMAIL_EXISTS" in err_str:
                message = "Email uz existuje!"
            elif "INVALID_EMAIL" in err_str:
                message = "Neplatny email!"
            elif "INVALID_PASSWORD" in err_str or "EMAIL_NOT_FOUND" in err_str:
                message = "Chybny email alebo heslo!"
            elif "MISSING_PASSWORD" in err_str:
                message = "Zadaj heslo!"
            else:
                message = "Chyba prihlasenia/registracie!"

            return False  # explicitne False, aby sa dalo skúsiť znovu

    while True:
        dt = clock.get_time()
        mouse = pygame.mouse.get_pos()
        click = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                click = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if mode == "login":
                        pygame.quit()
                        sys.exit()
                    else:
                        mode = "login"

                if event.key == pygame.K_RETURN:
                    result = attempt_login_or_register()
                    if result is True:
                        return True

            email_box.handle_event(event)
            password_box.handle_event(event)
            if mode == "register":
                confirm_box.handle_event(event)

        email_box.update(dt)
        password_box.update(dt)
        if mode == "register":
            confirm_box.update(dt)

        draw_gradient_background(screen, SPACE_TOP, SPACE_BOTTOM)

        title = "PRIHLASENIE" if mode == "login" else "REGISTRACIA"
        screen.blit(
            TITLE.render(title, True, WHITE),
            TITLE.render(title, True, WHITE).get_rect(center=(w//2, h//2-180+offset))
        )

        email_box.draw(screen)
        password_box.draw(screen)
        if mode == "register":
            confirm_box.draw(screen)

        last_box = password_box if mode == "login" else confirm_box
        login_btn.centerx = w//2
        login_btn.y = last_box.rect.bottom + 30

        draw_gradient_button(
            screen, login_btn,
            "LOGIN" if mode == "login" else "REGISTER",
            FONT, (50, 0, 70), (20, 0, 20)
        )

        # Klik na login/register
        if click and login_btn.collidepoint(mouse):
            result = attempt_login_or_register()
            if result is True:
                return True

        reg_rect = register_surf.get_rect(center=(w//2, last_box.rect.bottom + 140))
        if mode == "login":
            screen.blit(register_surf, reg_rect)
            if click and reg_rect.collidepoint(mouse):
                mode = "register"

        if mode == "register":
            draw_gradient_button(screen, back_btn, "BACK", SMALL, (70, 0, 50), (30, 0, 20))
            if click and back_btn.collidepoint(mouse):
                mode = "login"

        # ---------------- Správa ----------------
        if message:
            msg_surf = SMALL.render(message, True, message_color)
            msg_rect = msg_surf.get_rect(center=(w//2, login_btn.bottom + 140))
            screen.blit(msg_surf, msg_rect)

        pygame.display.flip()
        clock.tick(60)

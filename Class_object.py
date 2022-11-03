import pygame

class text_box:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.typing = False
        self.text = ""
    
    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(self.x, self.y, self.w, self.h), 3)
        font = pygame.font.Font('freesansbold.ttf', 32)
        text = font.render(self.text, True, (255, 255, 255), (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (self.x + self.w // 2, self.y + self.h // 2)
        screen.blit(text, textRect)

    def collision_with_mouse(self, mx, my):
        if(self.x + self.w > mx and self.x < mx and self.y + self.h > my and self.y < my):
            return True
        return False

class button:
    def __init__(self, x, y, width, height, text):
        self.text = text
        self.x = x
        self.y = y
        self.w = width
        self.h = height
        self.hover = False

    def draw(self, screen):
        font = pygame.font.Font('freesansbold.ttf', 32)
        if(not self.hover):
            pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(self.x, self.y, self.w, self.h))
            text = font.render(self.text, True, (255, 0, 0), (255, 255, 255))
        else:
            pygame.draw.rect(screen, (0, 0, 255), pygame.Rect(self.x, self.y, self.w, self.h))
            text = font.render(self.text, True, (255, 0, 0), (0, 0, 255))
        

        
        textRect = text.get_rect()
        textRect.center = (self.x + self.w // 2, self.y + self.h // 2)
        screen.blit(text, textRect)
    
    def collision_with_mouse(self, mx, my):
        if(self.x + self.w > mx and self.x < mx and self.y + self.h > my and self.y < my):
            return True
        return False
import pygame
import time

class Window:
    def __init__(self, size) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode(size)
        self.bindings = []
        self.KEYHOLD = 0
        self.MOUSELEFT = 1
        self.MOUSERIGHT = 2
        self.MOUSEWHEEL = 3

    def drawLine(self, p1, p2, color=(255, 255, 255)):
        pygame.draw.line(self.screen, color, p1, p2)
    
    def drawPoint(self, p, color=(255, 255, 255), radius=1):
        pygame.draw.circle(self.screen, color, p, radius)
    
    def drawRect(self, pos, width, height, color=(255, 255, 255)):
        pygame.draw.rect(self.screen, color, pygame.Rect(pos, (width, height)))

    def getMousePos(self):
        return pygame.mouse.get_pos()

    def bindFunction(self, key:int, function, eventType:list=[pygame.KEYDOWN]):
        self.bindings.append((key, function, eventType))

    def clear(self):
        self.screen.fill((0, 0, 0))

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pressedButtons = pygame.mouse.get_pressed(num_buttons=3)
                for binding in self.bindings:
                    if(binding[2].__contains__(pygame.MOUSEBUTTONDOWN)):
                        if(binding[0] == self.MOUSELEFT and pressedButtons[0]):
                            binding[1]()
                        if(binding[0] == self.MOUSEWHEEL and pressedButtons[1]):
                            binding[1]()
                        if(binding[0] == self.MOUSERIGHT and pressedButtons[2]):
                            binding[1]()
                    elif(binding[2].__contains__(pygame.MOUSEBUTTONUP)):
                        if(binding[0] == self.MOUSELEFT and pressedButtons[0]):
                            binding[1]()
                        if(binding[0] == self.MOUSEWHEEL and pressedButtons[1]):
                            binding[1]()
                        if(binding[0] == self.MOUSERIGHT and pressedButtons[2]):
                            binding[1]()
            keys = pygame.key.get_pressed()
            for binding in self.bindings:
                if keys[binding[0]] and binding[2].__contains__(self.KEYHOLD):
                    binding[1]()
            if event.type == pygame.KEYDOWN:
                for binding in self.bindings:
                    if event.key == binding[0] and binding[2].__contains__(pygame.KEYDOWN):
                        binding[1]()
            if event.type == pygame.KEYUP:
                for binding in self.bindings:
                    if event.key == binding[0] and binding[2].__contains__(pygame.KEYUP):
                        binding[1]()
        pygame.display.update()
        time.sleep(0.01)

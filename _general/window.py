from math import cos, radians, sin, sqrt
from numpy import asfortranarray
import bezier
import pygame
import time

# https://stackoverflow.com/questions/2259476/rotating-a-point-about-another-point-2d
def rotatePoint(center, point, angle):
    newPoint = point.copy()

    s = sin(angle)
    c = cos(angle)

    newPoint[0] -= center[0]
    newPoint[1] -= center[1]
    
    xnew = newPoint[0] * c - newPoint[1] * s
    ynew = newPoint[0] * s + newPoint[1] * c

    newPoint[0] = xnew + center[0]
    newPoint[1] = ynew + center[1]

    return newPoint

class Handle:
    def __init__(self, position, grab_radius, update_function=None, hidden=False) -> None:
        self.position = position
        self.grab_radius = grab_radius
        self.is_hidden = hidden
        self.is_grabbed = False
        self.update_function = update_function
    
    def draw(self, w):
        w.draw_point(self.position, (0, 0, 255), radius=self.grab_radius)

class Slider:
    def __init__(self, position, height, grab_radius, p_min, p_max, update_function=None, hidden=False) -> None:
        self.position = position
        self.handle_position = self.position
        self.height = height
        self.min = p_min
        self.max = p_max
        self.grab_radius = grab_radius
        self.is_grabbed = False
        self.is_hidden = hidden
        self.value = p_min
        self.value_per_percent = abs(p_max-p_min)
        self.update_function = update_function
    
    def draw(self, w):
        w.draw_point(self.handle_position, radius=self.grab_radius)
        w.draw_line(self.position, [self.position[0], self.position[1] + self.height], width=5)

class Window:
    def __init__(self, size) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode(size)
        self.bindings = []
        self.mouse_handles = []
        self.sliders = []
        self.last_mouse_position = None
        self.is_mb1_pressed = False
        self.is_mb2_pressed = False
        self.is_mb3_pressed = False
        self.KEYHOLD = 0
        self.MOUSELEFT = 1
        self.MOUSERIGHT = 2
        self.MOUSEWHEEL = 3

    def draw_line(self, p1, p2, color=(255, 255, 255), width=1):
        pygame.draw.line(self.screen, color, p1, p2, width=width)
    
    def draw_point(self, p, color=(255, 255, 255), radius=1):
        pygame.draw.circle(self.screen, color, p, radius)
    
    def draw_circle(self, p, color=(255, 255, 255), radius=1, border_width=1):
        pygame.draw.circle(self.screen, color, p, radius, width=border_width)
    
    def draw_rect(self, pos, width, height, color=(255, 255, 255)):
        pygame.draw.rect(self.screen, color, pygame.Rect(pos, (width, height)))

    def draw_polygon(self, edges, closed=True, color=(255, 255, 255)):
        for i in range(len(edges)-1):
            self.draw_line(edges[i], edges[i+1], color=color)
        if closed:
            self.draw_line(edges[0], edges[-1])

    def draw_bezier_from_points(self, p1, p2, cp1, cp2, step=1):
        control_points = [p1, cp1, cp2, p2]
        nodes = asfortranarray([
            [control_points[0][0], control_points[1][0], control_points[2][0], control_points[3][0]],
            [control_points[0][1], control_points[1][1], control_points[2][1], control_points[3][1]]
        ])
        curve = bezier.Curve(nodes, degree=3)
        
        points = []
        for x in range(int(curve.length/step)):
            p = curve.evaluate(x/int(curve.length/step)).tolist()
            points.append((p[0][0], p[1][0]))
        
        self.draw_polygon(points, closed=False)

    def draw_bezier_from_angles(self, p1, p2, angle1, angle2, step=1):
        delta = p2[0] - p1[0]
        control_points = [p1, [p1[0] + delta/2, p1[1]], [p1[0] + delta/2, p2[1]], p2]
        control_points[2] = rotatePoint(control_points[3], control_points[2], radians(angle2))
        control_points[1] = rotatePoint(control_points[0], control_points[1], radians(angle1))
        nodes = asfortranarray([
            [control_points[0][0], control_points[1][0], control_points[2][0], control_points[3][0]],
            [control_points[0][1], control_points[1][1], control_points[2][1], control_points[3][1]]
        ])
        curve = bezier.Curve(nodes, degree=3)
        
        points = []
        for x in range(int(curve.length/step)):
            p = curve.evaluate(x/int(curve.length/step)).tolist()
            points.append((p[0][0], p[1][0]))
        
        self.draw_polygon(points, closed=False)
    
    def draw_bezier_through_points(self, control_points:list):
        for i in range(len(control_points)-1):
            self.draw_bezier_from_points(control_points[i], control_points[i+1], (0, 0), (0, 0))

    def get_mouse_pos(self):
        return pygame.mouse.get_pos()

    def bind_function(self, key:int, function, eventType:list=[pygame.KEYDOWN]):
        self.bindings.append((key, function, eventType))

    def add_mouse_handle(self, handle:Handle):
        def move_handle():
            if self.is_mb1_pressed and not self._is_other_handle_grabbed(handle):
                m = self.get_mouse_pos()
                dist = sqrt((handle.position[0] - m[0])**2 + (handle.position[1] - m[1])**2)
                if not handle.is_grabbed:
                    if dist < handle.grab_radius:
                        handle.is_grabbed = True
                if handle.is_grabbed:
                    handle.position = m
                    if handle.update_function is not None:
                        handle.update_function()
            else:
                handle.is_grabbed = False
        self.bind_function(-1, move_handle, eventType=[pygame.MOUSEMOTION])
        self.mouse_handles.append(handle)

    def add_slider(self, slider:Slider):
        def interact():
            if self.is_mb1_pressed and not self._is_other_handle_grabbed():
                m = self.get_mouse_pos()
                dist = sqrt((slider.handle_position[0] - m[0])**2 + (slider.handle_position[1] - m[1])**2)
                if not slider.is_grabbed:
                    if dist < slider.grab_radius:
                        slider.is_grabbed = True
                if slider.is_grabbed:
                    if slider.position[1] <= m[1] <= slider.position[1] + slider.height:
                        slider.handle_position = [slider.position[0], m[1]]
                        slider.value = slider.min + (m[1] - slider.position[1])/(slider.height) * slider.value_per_percent
                        if slider.update_function is not None:
                            slider.update_function()
            else:
                slider.is_grabbed = False

        self.bind_function(-1, interact, eventType=[pygame.MOUSEMOTION])
        self.sliders.append(slider)

    def clear(self):
        self.screen.fill((0, 0, 0))

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            
            pressedButtons = pygame.mouse.get_pressed(num_buttons=3)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pressedButtons[0]:
                    self.is_mb1_pressed = True
                if pressedButtons[1]:
                    self.is_mb2_pressed = True
                if pressedButtons[2]:
                    self.is_mb3_pressed = True
            if event.type == pygame.MOUSEBUTTONUP:
                if not pressedButtons[0]:
                    self.is_mb1_pressed = False
                if not pressedButtons[1]:
                    self.is_mb2_pressed = False
                if not pressedButtons[2]:
                    self.is_mb3_pressed = False

            keys = pygame.key.get_pressed()
            for binding in self.bindings:
                if keys[binding[0]] and binding[2].__contains__(self.KEYHOLD):
                    binding[1]()
                    continue
                    
                if binding[2].__contains__(event.type):
                    if binding[0] != -1:
                        if event.key == binding[0]:
                            binding[1]()
                    else:
                        binding[1]()

        for handle in self.mouse_handles:
            if not handle.is_hidden:
                handle.draw(self)
        for slider in self.sliders:
            if not slider.is_hidden:
                slider.draw(self)

        self.last_mouse_position = self.get_mouse_pos()
        pygame.display.update()
    
    def _is_other_handle_grabbed(self, handle:Handle=None) -> bool:
        is_other_handle_grabbed = False
        for h in self.mouse_handles:
            if h is not handle and h.is_grabbed:
                is_other_handle_grabbed = True
        return is_other_handle_grabbed

    def mainloop(self, func=None, sleep=0.01, clear=True) -> None:
        while True:
            if clear:
                self.clear()
            if func is not None:
                func()
            self.update()
            time.sleep(sleep)

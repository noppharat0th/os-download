import random
import time
from imgui_bundle import imgui as ImGui, imspinner

class Particle:
    def __init__(self, width, height):
        self.pos = [random.uniform(0, width), random.uniform(0, height)]
        self.vel = [random.uniform(-0.5, 0.5), random.uniform(0.2, 0.8)]
        self.size = random.uniform(1.0, 3.0)
        self.color = ImGui.get_color_u32(ImGui.ImColor(255, 255, 255, random.randint(50, 150)).value)

    def update(self, width, height):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        
        if self.pos[1] > height: self.pos[1] = -5
        if self.pos[0] > width: self.pos[0] = 0
        if self.pos[0] < 0: self.pos[0] = width

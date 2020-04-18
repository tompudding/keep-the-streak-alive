import ui
import globals
from globals.types import Point
import drawing
import pymunk

box_level = 7
sf = 1

def to_world_coords(p):
    return p*sf

def to_screen_coords(p):
    return p/sf

class Box(object):
    def __init__(self, parent, bl, tr):
        self.parent = parent
        self.quad = drawing.Quad(globals.quad_buffer)
        self.quad.set_vertices(bl, tr, box_level)
        self.quad.set_texture_coordinates(parent.atlas.texture_coords('resource/sprites/box.png'))
        mass = 10.0
        centre = self.quad.get_centre()
        vertices = [Point(*v[:2]) - centre for v in self.quad.vertex[:4]]
        #vertices = [vertices[2],vertices[3],vertices[0],vertices[1]]
        moment = pymunk.moment_for_poly(mass, vertices)
        self.body = pymunk.Body(mass=mass, moment=moment)
        self.body.position = to_world_coords(self.quad.get_centre().to_float())
        self.body.force = 0,0
        self.body.torque = 0
        self.body.velocity = 0,0
        self.body.angular_velocity = 0
        print(self.body.position,self.body.velocity)
        print(vertices)
        self.shape = pymunk.Poly(self.body, vertices)
        self.shape.friction = 0.5
        globals.space.add(self.body, self.shape)

    def update(self, t):
        #print(self.body.position,self.body.velocity/sf)
        vertices = [0,0,0,0]
        for i,v in enumerate(self.shape.get_vertices()):
            vertices[(4-i)&3] = v.rotated(self.body.angle) + self.body.position

        self.quad.set_all_vertices(vertices, box_level)


class GameView(ui.RootElement):

    def __init__(self):
        #self.atlas = globals.atlas = drawing.texture.TextureAtlas('tiles_atlas_0.png','tiles_atlas.txt')
        #globals.ui_atlas = drawing.texture.TextureAtlas('ui_atlas_0.png','ui_atlas.txt',extra_names=False)
        super(GameView,self).__init__(Point(0,0),globals.screen)

        #We need to draw some pans
        self.atlas = drawing.texture.TextureAtlas('atlas_0.png','atlas.txt',extra_names=None)

        self.test_box = Box(self, Point(100,100), Point(200,200))
        self.test_box1 = Box(self, Point(160,210), Point(260,310))

    def update(self, t):
        self.test_box.update(t)
        self.test_box1.update(t)

    def draw(self):
        drawing.draw_all(globals.quad_buffer, self.atlas.texture)

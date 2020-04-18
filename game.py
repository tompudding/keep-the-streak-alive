import ui
import globals
from globals.types import Point
import drawing
import pymunk
import cmath

box_level = 7
ball_level = 8
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
        self.moment = pymunk.moment_for_poly(mass, vertices)
        self.body = pymunk.Body(mass=mass, moment=self.moment, body_type=pymunk.Body.STATIC)
        self.body.position = to_world_coords(self.quad.get_centre().to_float())
        self.body.force = 0,0
        self.body.torque = 0
        self.body.velocity = 0,0
        self.body.angular_velocity = 0
        print(self.body.position,self.body.velocity)
        print(vertices)
        self.shape = pymunk.Poly(self.body, vertices)
        self.shape.friction = 0.5
        self.shape.elasticity = 0.95
        globals.space.add(self.body, self.shape)

    def update(self, t):
        #print(self.body.position,self.body.velocity/sf)
        vertices = [0,0,0,0]
        for i,v in enumerate(self.shape.get_vertices()):
            vertices[(4-i)&3] = v.rotated(self.body.angle) + self.body.position

        self.quad.set_all_vertices(vertices, box_level)

class Ball(object):
    def __init__(self, parent, pos, radius):
        self.parent = parent
        self.quad = drawing.Quad(globals.quad_buffer)
        self.quad.set_texture_coordinates(parent.atlas.texture_coords('resource/sprites/ball.png'))
        self.centre = pos

        #We need some vertices for our quad
        l = radius
        self.vertices = [Point(-l,-l), Point(-l,l), Point(l,l), Point(l,-l)]
        self.quad.set_vertices(self.vertices[0] + self.centre, self.vertices[2] + self.centre, ball_level)

        mass = 0.1
        self.moment = pymunk.moment_for_circle(mass, 0, radius)
        self.body = pymunk.Body(mass=mass, moment=self.moment)
        self.body.position = to_world_coords(self.quad.get_centre().to_float())
        self.body.force = 0,0
        self.body.torque = 0
        self.body.velocity = 0,0
        self.body.angular_velocity = 0
        print(self.body.position,self.body.velocity)
        self.shape = pymunk.Circle(self.body, radius)
        self.shape.friction = 0.5
        self.shape.elasticity = 0.95
        globals.space.add(self.body, self.shape)
        self.polar_vertices = [cmath.polar(v[0] + v[1]*1j) for v in self.vertices]

    def update(self, t):
        #Don't worry about rotation for now, the sprite is symetrical. We could fix this though
        self.centre = self.body.position
        final_vertices = []
        for r,a in self.polar_vertices:
            c = cmath.rect(r, a+self.body.angle)
            final_vertices.append(Point(c.real, c.imag) + self.centre)
        self.quad.set_all_vertices(final_vertices, ball_level)

class Line(object):
    def __init__(self, parent, start, end):
        self.parent = parent
        self.line = drawing.Line(globals.line_buffer)
        self.line.set_colour( (1,0,0,1) )

        self.start = start
        self.end = end
        self.update()

    def set_start(self, start):
        self.start = start
        self.update()

    def set_end(self, end):
        self.end = end
        self.update()

    def update(self):
        if self.start and self.end:
            self.line.set_vertices(self.start, self.end, 6)

    def enable(self):
        self.line.enable()

    def disable(self):
        self.line.disable()


class GameView(ui.RootElement):

    def __init__(self):
        #self.atlas = globals.atlas = drawing.texture.TextureAtlas('tiles_atlas_0.png','tiles_atlas.txt')
        #globals.ui_atlas = drawing.texture.TextureAtlas('ui_atlas_0.png','ui_atlas.txt',extra_names=False)
        super(GameView,self).__init__(Point(0,0),globals.screen)

        #We need to draw some pans
        self.atlas = drawing.texture.TextureAtlas('atlas_0.png','atlas.txt',extra_names=None)

        self.test_box = Box(self, Point(100,100), Point(200,200))
        self.test_box1 = Box(self, Point(160,210), Point(260,310))

        #self.ball = Circle(self, globals.mouse_screen)
        self.ball = Ball(self, Point(150,400), 10)
        self.dragging_line = Line(self, None, None)


        self.thrown = False
        globals.cursor.disable()
        self.dragging = None
        self.thrown = False

    def update(self, t):
        self.test_box.update(t)
        self.test_box1.update(t)

        if not self.thrown:
            self.ball.body.position = globals.mouse_screen
            #self.ball.set_pos(globals.mouse_pos)
        else:
            #update the quad according to its trajectory
            pass
        self.ball.update(t)

    def draw(self):
        drawing.draw_all(globals.quad_buffer, self.atlas.texture)
        drawing.line_width(1)
        drawing.draw_no_texture(globals.line_buffer)

    def mouse_motion(self, pos, rel, handled):
        if self.dragging:
            self.dragging_line.set_end(pos)
            self.dragging_line.update()

    def mouse_button_down(self,pos,button):
        if button == 1:
            #Clicked the main mouse button. We shouldn't be dragging anything or somethings gone wrong
            if self.dragging:
                print('What')
                self.dragging = None
            #We start dragging
            self.dragging = pos
            self.dragging_line.start = pos
            self.dragging_line.end = pos
            self.dragging_line.update()
            self.dragging_line.enable()

        return False,False

    def mouse_button_up(self, pos, button):
        if button == 1 and self.dragging:
            #release!
            print(f'Drag release from {self.dragging=} to {pos=}')
            self.ball.body.position = pos
            self.ball.body.angle = 0
            self.ball.body.force = 0,0
            self.ball.body.torque = 0
            self.ball.body.velocity = 0,0
            self.ball.body.angular_velocity = 0
            self.ball.body.moment = self.ball.moment
            self.ball.body.apply_impulse_at_local_point(self.dragging - pos)
            self.thrown = True
            self.dragging = None
            self.dragging_line.disable()
        return False,False

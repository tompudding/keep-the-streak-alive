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

class CollisionTypes:
    BALL   = 1
    BOTTOM = 2
    BOX    = 3
    WALL   = 4
    CUP    = 5

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
        self.shape.collision_type = CollisionTypes.BOX
        globals.space.add(self.body, self.shape)

    def update(self):
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
        self.shape.collision_type = CollisionTypes.BALL
        globals.space.add(self.body, self.shape)
        self.polar_vertices = [cmath.polar(v[0] + v[1]*1j) for v in self.vertices]

    def update(self):
        #Don't worry about rotation for now, the sprite is symetrical. We could fix this though
        self.centre = self.body.position
        final_vertices = []
        for r,a in self.polar_vertices:
            c = cmath.rect(r, a+self.body.angle)
            final_vertices.append(Point(c.real, c.imag) + self.centre)
        self.quad.set_all_vertices(final_vertices, ball_level)

class Line(object):
    def __init__(self, parent, start, end, colour=(1, 0, 0, 1)):
        self.parent = parent
        self.line = drawing.Line(globals.line_buffer)
        self.line.set_colour( colour )

        self.set(start, end)

    def set_start(self, start):
        self.start = start
        self.update()

    def set_end(self, end):
        self.end = end
        self.update()

    def set(self, start, end):
        self.start = start
        self.end = end
        self.update()

    def update(self):
        if self.start and self.end:
            self.line.set_vertices(self.start, self.end, 6)

    def enable(self):
        self.line.enable()

    def disable(self):
        self.line.disable()

class Cup(object):
    def __init__(self, parent, pos):
        self.parent = parent
        self.centre = pos
        self.vertices = [(0,90),(20,3),(64,3),(85,90)]
        self.vertices = [pos + (((Point(*v) - Point(43,0))*0.7)) for v in self.vertices]
        self.segments = []
        self.line_quads = []

        for i in range(len(self.vertices) - 1):
            v = self.vertices
            segment = pymunk.Segment(globals.space.static_body, v[i], v[i+1], 0)
            segment.friction = 1000
            segment.elasticity = 0
            if i == 1:
                segment.collision_type = CollisionTypes.CUP
            else:
                segment.collision_type = CollisionTypes.WALL
            self.segments.append(segment)
            line_quad = drawing.Line(globals.line_buffer)
            line_quad.set_colour( (1,0,0,1) )
            line_quad.set_vertices(v[i], v[i+1], 6)
            self.line_quads.append(line_quad)
            print(v[i],v[i+1])

        globals.space.add(self.segments)


class NextLevel(ui.HoverableBox):
    line_width = 1
    def __init__(self, parent, bl, tr):
        self.border = drawing.QuadBorder(globals.ui_buffer, line_width=self.line_width)
        super(NextLevel, self).__init__(parent, bl, tr, (0,0,0,1))
        self.text = ui.TextBox(self, Point(0,0.5), Point(1,0.6), 'Well done!', 3, colour=drawing.constants.colours.white, alignment=drawing.texture.TextAlignments.CENTRE)
        self.border.set_colour(drawing.constants.colours.red)
        self.border.set_vertices(self.absolute.bottom_left, self.absolute.top_right)
        self.border.enable()
        self.replay_button = ui.TextBoxButton(self, 'Replay', Point(0.1, 0.1), size=2, callback=self.replay)
        self.continue_button = ui.TextBoxButton(self, 'Next Level', Point(0.7, 0.1), size=2, callback=self.next_level)

    def replay(self, pos):
        print('Replay')
        self.parent.replay()
        self.disable()

    def next_level(self, pos):
        print('Next level')

    def enable(self):
        if not self.enabled:
            self.root.register_ui_element(self)
            self.border.enable()
        super(NextLevel, self).enable()

    def disable(self):
        if self.enabled:
            self.root.remove_ui_element(self)
            self.border.disable()
        super(NextLevel, self).disable()


class GameView(ui.RootElement):
    text_fade_duration = 1000
    def __init__(self):
        #self.atlas = globals.atlas = drawing.texture.TextureAtlas('tiles_atlas_0.png','tiles_atlas.txt')
        #globals.ui_atlas = drawing.texture.TextureAtlas('ui_atlas_0.png','ui_atlas.txt',extra_names=False)
        super(GameView,self).__init__(Point(0,0),globals.screen)

        #We need to draw some pans
        self.atlas = drawing.texture.TextureAtlas('atlas_0.png','atlas.txt',extra_names=None)

        self.boxes = []
        #self.boxes.append(Box(self, Point(100,100), Point(200,200)))
        #self.boxes.append(Box(self, Point(160,210), Point(260,310)))

        #self.ball = Circle(self, globals.mouse_screen)
        self.ball = Ball(self, Point(150,400), 10)
        self.dragging_line = Line(self, None, None)
        self.old_line = Line(self, None, None, (0.2,0.2,0.2,1))
        self.level_text = ui.TextBox(self, Point(0,0.5), Point(1,0.6), 'Get the ball in the cup', 3, colour=drawing.constants.colours.white, alignment=drawing.texture.TextAlignments.CENTRE)
        self.text_fade = False

        #Make 100 line segments for a dotted trajectory line
        self.dotted_line = [Line(self, None, None, (0, 0, 0.4, 1)) for i in range(1000)]
        self.dots = 0

        globals.cursor.disable()
        self.dragging = None
        self.thrown = False

        self.bottom_handler = globals.space.add_collision_handler(CollisionTypes.BALL, CollisionTypes.BOTTOM)
        self.box_handler = globals.space.add_collision_handler(CollisionTypes.BALL, CollisionTypes.BOX)
        self.cup_handler = globals.space.add_collision_handler(CollisionTypes.BALL, CollisionTypes.CUP)

        self.bottom_handler.begin = self.bottom_hit
        self.box_handler.begin = self.box_hit
        self.cup_handler.begin = self.cup_hit
        #self.cup_handler.separate = self.cup_sep
        self.cup = Cup(self, Point(globals.screen.x/2,0))
        self.moving = None
        self.moving_pos = None
        self.current_level = 0
        self.game_over = False
        self.paused = False
        self.next_level = NextLevel(self, Point(0.2,0.2), Point(0.8,0.8))
        self.next_level.disable()

    def cup_hit(self, arbiter, space, data):
        self.current_level += 1
        #if self.current_level >= len(self.levels):
        #    self.game_over = True

        self.paused = True
        self.next_level.enable()
        self.level_text.disable()
        return True

    def box_hit(self, arbiter, space, data):
        if not self.thrown:
            return False

        print('Boop box')
        return True

    def replay(self):
        self.paused = False
        self.throw_ball(*self.last_throw)

    def bottom_hit(self, arbiter, space, data):
        if not self.thrown:
            return False
        print('KLARG bottom hit')
        self.stop_throw()
        return True

    def update(self, t):
        #for box in self.boxes:
        #    box.update()
        if self.paused:
            return

        if self.text_fade:
            if globals.t > self.text_fade:
                self.level_text.disable()
                self.text_fade = None
            else:
                colour = (1,1,1, (self.text_fade - globals.t)/self.text_fade_duration)
                self.level_text.set_colour(colour)

        if not self.thrown:
            self.ball.body.position = globals.mouse_screen
            #self.ball.set_pos(globals.mouse_pos)

        self.ball.update()

        if self.thrown:
            diff = self.ball.body.position - self.last_ball_pos
            if diff.get_length_sqrd() > 10:

                if (self.dots & 1) == 0 and self.dots < len(self.dotted_line):
                    self.dotted_line[self.dots].set(self.last_ball_pos, self.ball.body.position)
                    self.dotted_line[self.dots].enable()

                self.dots += 1
                self.last_ball_pos = self.ball.body.position

    def draw(self):
        drawing.draw_all(globals.quad_buffer, self.atlas.texture)
        drawing.draw_no_texture(globals.ui_buffer)
        drawing.line_width(1)
        drawing.draw_no_texture(globals.line_buffer)


    def mouse_motion(self, pos, rel, handled):
        if self.paused:
            return super(GameView, self).mouse_motion(pos, rel, handled)
        if self.dragging:
            self.dragging_line.set_end(pos)
            self.dragging_line.update()

        elif self.moving:
            self.moving.body.position = pos - self.moving_pos
            self.moving.update()
            globals.space.reindex_static()

    def stop_throw(self):
        self.thrown = False
        globals.cursor.disable()

    def mouse_button_down(self,pos,button):
        if self.paused:
            return super(GameView, self).mouse_button_down(pos, button)
        if button == 1:
            #Clicked the main mouse button. We shouldn't be dragging anything or somethings gone wrong
            if self.dragging:
                print('What')
                self.dragging = None
            if self.thrown:
                self.stop_throw()

            #We start dragging
            self.dragging = pos
            self.dragging_line.start = pos
            self.dragging_line.end = pos
            self.dragging_line.update()
            self.dragging_line.enable()


        elif button == 3 and not self.thrown and not self.dragging:
            #Perhaps we can move the blocks around
            for box in self.boxes:
                distance, info = box.shape.point_query(pos)
                if distance < 0:
                    print('In box',distance,info)
                    self.moving = box
                    self.moving_pos = (pos - box.body.position)

        return False,False

    def mouse_button_up(self, pos, button):
        if self.paused:
            return super(GameView, self).mouse_button_up(pos, button)
        if self.moving:
            if button == 3:
                self.moving = None
                self.moving_pos = None
                return False, False

        if button == 1 and self.dragging:
            #release!
            print(f'Drag release from {self.dragging=} to {pos=}')

            self.throw_ball(pos, self.dragging - pos)

            if self.text_fade == False:
                self.text_fade = globals.t + self.text_fade_duration

        elif button == 3 and self.thrown and not self.dragging:
            self.stop_throw()

        return False,False

    def throw_ball(self, pos, direction):
        self.last_throw = (pos, direction)
        self.ball.body.position = pos
        self.ball.body.angle = 0
        self.ball.body.force = 0,0
        self.ball.body.torque = 0
        self.ball.body.velocity = 0,0
        self.ball.body.angular_velocity = 0
        self.ball.body.moment = self.ball.moment
        self.ball.body.apply_impulse_at_local_point(direction)
        self.thrown = True
        globals.cursor.enable()
        for line in self.dotted_line[:self.dots]:
            line.disable()
        self.dots = 0

        self.dragging = None
        self.dragging_line.disable()
        self.last_ball_pos = self.ball.body.position
        self.old_line.set(self.dragging_line.start, self.dragging_line.end)

import ui
import globals
from globals.types import Point
import drawing
import pymunk
import cmath
import math
import pygame
import traceback

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
        self.normal_tc = parent.atlas.texture_coords('resource/sprites/box.png')
        self.touched_tc = parent.atlas.texture_coords('resource/sprites/touched_box.png')
        self.quad.set_texture_coordinates(self.normal_tc)
        self.touched = False
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
        self.shape.parent = self
        globals.space.add(self.body, self.shape)
        self.in_world = True

    def update(self):
        #print(self.body.position,self.body.velocity/sf)
        vertices = [0,0,0,0]
        for i,v in enumerate(self.shape.get_vertices()):
            vertices[(4-i)&3] = v.rotated(self.body.angle) + self.body.position

        self.quad.set_all_vertices(vertices, box_level)

    def delete(self):
        self.quad.delete()
        globals.space.remove(self.body, self.shape)
        self.in_world = False

    def set_touched(self, disappear=False):
        self.touched = True
        self.quad.set_texture_coordinates(self.touched_tc)
        if disappear:
            self.quad.disable()
            globals.space.remove(self.body, self.shape)
            self.in_world = False

    def reset_touched(self, disappear=False):
        if not self.touched:
            return
        self.touched = False
        self.quad.set_texture_coordinates(self.normal_tc)
        if not self.in_world:
            self.quad.enable()
            globals.space.add(self.body, self.shape)
            self.in_world = True

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

    def disable(self):
        self.quad.disable()

    def enable(self):
        self.quad.enable()

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
        self.dotted_line = []

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

    def disable(self):
        for quad in self.line_quads:
            quad.disable()

        for line in self.dotted_line:
            line.disable()

    def enable(self):
        for quad in self.line_quads:
            quad.enable()

        for line in self.dotted_line:
            line.enable()

    def reset_line(self):
        for line in self.dotted_line:
            line.delete()
        self.dotted_line = []

        # Finally we draw a dotted line around where you're allowed to throw from. That means starting over at
        # the left and going round
        num_segments = 200
        angle = math.pi/num_segments
        for dot in range(0, num_segments, 2):
            a = angle*dot
            b = angle*(dot+1)
            start = self.centre + (Point(math.cos(a), math.sin(a)) * self.parent.min_distance)
            end = self.centre + (Point(math.cos(b), math.sin(b)) * self.parent.min_distance)
            line = drawing.Line(globals.line_buffer)
            line.set_colour( (0.4,0.4,0.4,1) )
            line.set_vertices(start, end, 6)
            self.dotted_line.append(line)

    def remove_line(self):
        for line in self.dotted_line:
            line.delete()
        self.dotted_line = []


class NextLevel(ui.HoverableBox):
    line_width = 1
    def __init__(self, parent, bl, tr):
        self.border = drawing.QuadBorder(globals.ui_buffer, line_width=self.line_width)
        super(NextLevel, self).__init__(parent, bl, tr, (0.05,0.05,0.05,1))
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
        self.parent.next_level()
        self.disable()

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

class DottedBox(ui.UIElement):
    def __init__(self, parent, bl, tr):
        super(DottedBox, self).__init__(parent, bl, tr)
        #super(DottedBox, self).__init__(parent, bl, tr)
        self.lines = []
        seg_size = 5
        for start, end in ((self.absolute.bottom_left, self.absolute.bottom_right),
                           (self.absolute.bottom_right, self.absolute.top_right),
                           (self.absolute.top_right, self.absolute.top_left),
                           (self.absolute.top_left, self.absolute.bottom_left)):
            num_segs = ((end - start).length())/seg_size
            seg = (end - start)/num_segs
            for i in range(0, int(num_segs), 2):
                line = drawing.Line(globals.line_buffer)
                seg_start = start+seg*i
                seg_end = start+seg*(i+1)
                line.set_colour( (0.4,0.4,0.4,1) )
                line.set_vertices(seg_start, seg_end, 6)
                print(seg_start, seg_end)
                self.lines.append(line)

    def disable(self):
        for line in self.lines:
            line.disable()

    def enable(self):
        for line in self.lines:
            line.enable()

    def delete(self):
        for line in self.lines:
            line.delete()


def call_with(callback, arg):
    def caller(pos):
        return callback(pos, arg)
    return caller

class MainMenu(ui.HoverableBox):
    line_width = 1
    def __init__(self, parent, bl, tr):
        self.border = drawing.QuadBorder(globals.ui_buffer, line_width=self.line_width)
        self.level_buttons = []
        self.ticks = []
        super(MainMenu, self).__init__(parent, bl, tr, (0.05,0.05,0.05,1))
        self.text = ui.TextBox(self, Point(0,0.8), Point(1,0.95), 'Keep the Streak Alive', 3, colour=drawing.constants.colours.white, alignment=drawing.texture.TextAlignments.CENTRE)
        self.border.set_colour(drawing.constants.colours.red)
        self.border.set_vertices(self.absolute.bottom_left, self.absolute.top_right)
        self.border.enable()
        self.quit_button = ui.TextBoxButton(self, 'Quit', Point(0.45, 0.1), size=2, callback=self.parent.quit)
        #self.continue_button = ui.TextBoxButton(self, 'Next Level', Point(0.7, 0.1), size=2, callback=self.next_level)


        pos = Point(0.2,0.8)
        for i, level in enumerate(parent.levels):
            button = ui.TextBoxButton(self, f'{i}: {level.name}', pos, size=2, callback=call_with(self.start_level, i),)
            self.ticks.append(ui.TextBox(self, pos-Point(0.05,0.01), tr=pos+Point(0.1,0.04), text='\x9a', scale=3, colour=(0,1,0,1)))
            if not self.parent.done[i]:
                self.ticks[i].disable()

            pos.y -= 0.1
            self.level_buttons.append(button)

    def start_level(self, pos, level):
        self.disable()
        self.parent.current_level = level
        self.parent.init_level()
        self.parent.stop_throw()
        self.parent.paused = False

    def enable(self):
        if not self.enabled:
            self.root.register_ui_element(self)
            self.border.enable()
        for button in self.level_buttons:
            button.enable()
        super(MainMenu, self).enable()
        for i,tick in enumerate(self.ticks):
            if self.parent.done[i]:
                tick.enable()
            else:
                tick.disable()


    def disable(self):
        if self.enabled:
            self.root.remove_ui_element(self)
            self.border.disable()
        super(MainMenu, self).disable()
        for tick in self.ticks:
            tick.disable()


class GameOver(ui.HoverableBox):
    line_width = 1
    def __init__(self, parent, bl, tr):
        self.border = drawing.QuadBorder(globals.ui_buffer, line_width=self.line_width)
        super(GameOver, self).__init__(parent, bl, tr, (0,0,0,1))
        self.text = ui.TextBox(self, Point(0,0.5), Point(1,0.6), 'You Kept the Streak Alive! Amazing!', 2, colour=drawing.constants.colours.white, alignment=drawing.texture.TextAlignments.CENTRE)
        self.border.set_colour(drawing.constants.colours.red)
        self.border.set_vertices(self.absolute.bottom_left, self.absolute.top_right)
        self.border.enable()
        self.replay_button = ui.TextBoxButton(self, 'Replay', Point(0.1, 0.1), size=2, callback=self.replay)
        self.quit_button = ui.TextBoxButton(self, 'Quit', Point(0.7, 0.1), size=2, callback=parent.quit)

    def replay(self, pos):
        print('Replay')
        self.parent.replay()
        self.disable()

    def enable(self):
        if not self.enabled:
            self.root.register_ui_element(self)
            self.border.enable()
        super(GameOver, self).enable()

    def disable(self):
        if self.enabled:
            self.root.remove_ui_element(self)
            self.border.disable()
        super(GameOver, self).disable()

class Level(object):
    disappear = False
    min_distance = 300
    restricted_start = None
    boxes_pos_fixed = False

class LevelZero(Level):
    text = 'Get the ball in the cup'
    name = 'Introduction'
    subtext = 'Drag to shoot from outside the line'
    items = []
    min_distance = 200
    min_force = 50

class LevelOne(Level):
    text = 'Level 1: Bounce the ball off the box first'
    name = 'Box Bounce'
    subtext = 'Left drag to move the box, right drag to rotate'
    items = [(Box, Point(100, 100), Point(200,200))]
    min_distance = 300
    min_force = 50

class LevelTwo(Level):
    text = 'Level 2: Bounce the ball off both boxes. Keep the streak alive!'
    name = 'Two boxes'
    subtext = 'Left drag to move, right drag to rotate'
    items = [(Box, Point(100, 100), Point(200,200)),
             (Box, Point(300, 100), Point(400,200))]
    min_distance = 300
    min_force = 0

class LevelThree(Level):
    text = 'Level 3: Keep the streak alive!'
    name = 'Three boxes'
    subtext = 'Left drag to move, right drag to rotate'
    items = [(Box, Point(100, 100), Point(200,200)),
             (Box, Point(300, 100), Point(400,200)),
             (Box, Point(500, 100), Point(600,200))
    ]
    min_distance = 300
    min_force = 0

class LevelFour(Level):
    text = 'Level 4: Keep the streak alive!'
    name = 'Three Disappearing Boxes'
    disappear = True
    subtext = 'Boxes disappear when hit'
    items = [(Box, Point(100, 100), Point(200,200)),
             (Box, Point(300, 100), Point(400,200)),
             (Box, Point(500, 100), Point(600,200))]
    min_distance = 300
    min_force = 0

class LevelFive(Level):
    text = 'Level 5: Keep the streak alive!'
    name = 'Restricted Start'
    subtext = 'Shoot from the grey box'
    items = [(Box, Point(100, 100), Point(200,200)),
             (Box, Point(300, 100), Point(400,200)),
             (Box, Point(500, 100), Point(600,200))]
    min_distance = 300
    restricted_start = (Point(0.75,0.1),Point(0.97,0.25))
    min_force = 0

class LevelSix(Level):
    text = 'Level 5: Keep the streak alive!'
    name = 'Hardestest'
    disappear = False
    subtext = 'Now you can\'t move the boxes (only rotate). Good luck!'
    items = [(Box, Point(423, 619) - Point(50,50), Point(423, 619) + Point(50,50)),
             (Box, Point(912, 637) - Point(50,50), Point(912, 637) + Point(50,50)),
             (Box, Point(736, -7) - Point(50,50), Point(736, -7) + Point(50,50)),
             (Box, Point(518, -1) - Point(50,50), Point(518, -1) + Point(50,50)),
             (Box, Point(733, 560) - Point(50,50), Point(733, 560) + Point(50,50)),
    ]
    min_distance = 300
    min_force = 0
    restricted_start = (Point(0.75,0.1),Point(0.97,0.25))
    boxes_pos_fixed = True



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

        #Make 100 line segments for a dotted trajectory line
        self.dotted_line = [Line(self, None, None, (0, 0, 0.4, 1)) for i in range(1000)]
        self.dots = 0

        self.dragging = None
        self.thrown = False
        self.level_text = None
        self.sub_text = None

        self.bottom_handler = globals.space.add_collision_handler(CollisionTypes.BALL, CollisionTypes.BOTTOM)
        self.box_handler = globals.space.add_collision_handler(CollisionTypes.BALL, CollisionTypes.BOX)
        self.cup_handler = globals.space.add_collision_handler(CollisionTypes.BALL, CollisionTypes.CUP)

        self.bottom_handler.begin = self.bottom_hit
        self.box_handler.begin = self.box_hit
        self.cup_handler.begin = self.cup_hit
        #self.cup_handler.separate = self.cup_sep
        self.moving = None
        self.moving_pos = None
        self.current_level = 0
        self.game_over = False
        self.restricted_box = None
        self.start_level = None

        self.levels = [
            LevelZero(),
            LevelOne(),
            LevelTwo(),
            LevelThree(),
            LevelFour(),
            LevelFive(),
            LevelSix(),
            #LevelSeven(),
        ]
        self.done = [False for level in self.levels]

        self.last_throw = None
        self.next_level_menu = NextLevel(self, Point(0.25,0.3), Point(0.75,0.7))
        self.next_level_menu.disable()
        self.main_menu = MainMenu(self, Point(0.2,0.1), Point(0.8,0.9))
        self.paused = True
        self.rotating = None
        self.rotating_pos = None

        self.current_level = 0
        self.cup = Cup(self, Point(globals.screen.x/2,0))
        #self.init_level()
        self.cup.disable()
        self.ball.disable()

    def quit(self, pos):
        raise SystemExit()

    def init_level(self):
        if self.level_text:
            self.level_text.delete()
        self.start_level = globals.t
        level = self.levels[self.current_level]
        self.min_distance = level.min_distance
        self.level_text = ui.TextBox(self, Point(0,0.5), Point(1,0.6), level.text, 3, colour=drawing.constants.colours.white, alignment=drawing.texture.TextAlignments.CENTRE)
        if level.subtext:
            self.sub_text = ui.TextBox(self, Point(0,0.4), Point(1,0.5), level.subtext, 2, colour=drawing.constants.colours.white, alignment=drawing.texture.TextAlignments.CENTRE)
        else:
            self.sub_text = None
        self.text_fade = False
        for box in self.boxes:
            box.delete()

        for line in self.dotted_line[:self.dots]:
            line.disable()
        self.dots = 0

        self.boxes = []
        #jim = 0
        for item, bl, tr in level.items:
            box = item(self, bl, tr)
            #box.body.angle = [0.4702232572610111, -0.2761159031752114, 0.06794826568042156, -0.06845718620994479, 1.3234945990935332][jim]
            box.update()
            #jim += 1
            self.boxes.append(box)
        self.cup.enable()
        self.ball.enable()
        self.old_line.disable()

        globals.cursor.disable()
        self.paused = False
        self.last_throw = None
        if self.restricted_box:
            self.restricted_box.delete()
            self.restricted_box = None
        if level.restricted_start:
            self.restricted_box = DottedBox(self, level.restricted_start[0], level.restricted_start[1])
            self.cup.remove_line()
        else:
            self.cup.reset_line()

    def end_game(self):
        self.game_over = GameOver(self, Point(0.2,0.2), Point(0.8,0.8))
        self.paused = True

    def cup_hit(self, arbiter, space, data):
        #self.current_level += 1
        #if self.current_level >= len(self.levels):
        #    self.game_over = True
        if self.paused:
            return True

        if not all(box.touched for box in self.boxes):
            self.bottom_hit(arbiter, space, data)
            return True

        for i,box in enumerate(self.boxes):
            print(i,box.body.position,box.body.angle)
            print(self.last_throw)

        self.paused = True
        self.done[self.current_level] = True

        if self.current_level + 1 >= len(self.levels):
            self.end_game()
        else:
            self.next_level_menu.enable()
        self.level_text.disable()
        if self.sub_text:
            self.sub_text.disable()
        return True

    def box_hit(self, arbiter, space, data):
        if not self.thrown:
            return False

        print('Boop box')

        for shape in arbiter.shapes:
            if hasattr(shape, 'parent'):
                shape.parent.set_touched(self.levels[self.current_level].disappear)
        return True

    def replay(self):
        self.paused = False
        self.throw_ball(*self.last_throw)
        for box in self.boxes:
            box.reset_touched(self.levels[self.current_level].disappear)

    def next_level(self):
        self.stop_throw()
        self.current_level += 1
        self.init_level()
        self.paused = False

    def bottom_hit(self, arbiter, space, data):
        if not self.thrown or self.ball.body.velocity[1] > 0:
            return False
        print('KLARG bottom hit')
        self.stop_throw()
        return True

    def key_down(self, key):
        #        if key == pygame.locals.K_RETURN:
        #            if self.current_player.is_player():
        #                self.current_player.end_turn(Point(0,0))
        if key == pygame.locals.K_ESCAPE:
            if self.main_menu.enabled:
                return self.quit(0)
            self.main_menu.enable()
            self.paused = True
            globals.cursor.enable()
            self.level_text.disable()
            if self.sub_text:
                self.sub_text.disable()
            if self.next_level_menu:
                self.next_level_menu.disable()
        if key == pygame.locals.K_SPACE:
            #space is as good as the left button
            self.mouse_button_down(globals.mouse_screen, 1)

        elif key in (pygame.locals.K_RSHIFT,pygame.locals.K_LSHIFT):
            #shifts count as the right button
            self.mouse_button_down(globals.mouse_screen, 3)

        #This makes it super easy
        elif key == pygame.locals.K_r and self.last_throw:
            self.throw_ball(*self.last_throw)


    def key_up(self, key):
        if key == pygame.locals.K_SPACE:
            #space is as good as the left button
            self.mouse_button_up(globals.mouse_screen, 1)

        elif key in (pygame.locals.K_RSHIFT,pygame.locals.K_LSHIFT):
            #shifts count as the right button
            self.mouse_button_up(globals.mouse_screen, 3)


    def update(self, t):
        #for box in self.boxes:
        #    box.update()
        if self.paused:
            return

        if self.text_fade == False and self.start_level and globals.t - self.start_level > 5000:
            self.text_fade = globals.t + self.text_fade_duration

        if self.text_fade:
            if globals.t > self.text_fade:
                self.level_text.disable()
                if self.sub_text:
                    self.sub_text.disable()
                self.text_fade = None
            else:
                colour = (1,1,1, (self.text_fade - globals.t)/self.text_fade_duration)
                self.level_text.set_colour(colour)
                if self.sub_text:
                    self.sub_text.set_colour(colour)

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
        drawing.draw_no_texture(globals.ui_buffer)
        drawing.draw_all(globals.quad_buffer, self.atlas.texture)
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

        elif self.rotating:
            #old_r, old_a = cmath.polar(self.rotating_pos.x + self.rotating_pos.y*1j)
            p = pos - self.rotating.body.position
            new_r, new_a = cmath.polar(p.x + p.y*1j)
            #print(old_a, new_a, self.rotating.body.angle)
            self.rotating.body.angle = self.rotating_angle + new_a
            self.rotating.update()
            globals.space.reindex_static()

    def stop_throw(self):
        self.thrown = False
        globals.cursor.disable()
        for box in self.boxes:
            box.reset_touched()

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

            in_box = None
            if False == self.levels[self.current_level].boxes_pos_fixed:
                for box in self.boxes:
                    distance, info = box.shape.point_query(pos)
                    if distance < 0:
                        self.moving = box
                        self.moving_pos = (pos - box.body.position)
                        return False, False

            if self.restricted_box and pos not in self.restricted_box:
                return False, False

            throw_distance = (pos - self.cup.centre).length()
            if throw_distance < self.min_distance:
                return False, False

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
                    self.rotating = box
                    #self.rotating_pos = (pos - box.body.position)
                    diff = (pos - box.body.position)
                    r, a = cmath.polar(diff.x + diff.y*1j)
                    self.rotating_angle = box.body.angle - a

        return False,False

    def mouse_button_up(self, pos, button):
        if self.paused:
            return super(GameView, self).mouse_button_up(pos, button)

        if button == 1 and self.dragging:
            #release!
            print(f'Drag release from {self.dragging=} to {pos=}')
            diff = self.dragging - pos
            if diff.length() > 5:
                #pos, diff = Point(1084.00,13.00), Point(-41.00,149.00)
                self.throw_ball(pos, diff)

                if self.text_fade == False:
                    self.text_fade = globals.t + self.text_fade_duration
            else:
                self.dragging = None
                self.dragging_line.disable()

        elif button == 1 and self.moving:
            if self.moving:
                self.moving = None
                self.moving_pos = None
                return False, False
        elif button == 3 and self.rotating:
            self.rotating = None
            self.rotating_pos = None
            return False, False

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
        self.old_line.enable()

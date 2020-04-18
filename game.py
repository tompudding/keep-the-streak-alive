import ui
import globals
from globals.types import Point
import drawing

class GameView(ui.RootElement):

    def __init__(self):
        #self.atlas = globals.atlas = drawing.texture.TextureAtlas('tiles_atlas_0.png','tiles_atlas.txt')
        #globals.ui_atlas = drawing.texture.TextureAtlas('ui_atlas_0.png','ui_atlas.txt',extra_names=False)
        super(GameView,self).__init__(Point(0,0),globals.screen)

        #We need to draw some pans
        self.atlas = drawing.texture.TextureAtlas('atlas_0.png','atlas.txt',extra_names=None)

        self.test_box = drawing.Quad(globals.quad_buffer)
        self.test_box.set_vertices(Point(100,100),
                                   Point(200,200),
                                   7)
        self.test_box.set_texture_coordinates(self.atlas.texture_coords('resource/sprites/box.png'))

    def update(self, t):
        pass

    def draw(self):
        drawing.draw_all(globals.quad_buffer, self.atlas.texture)

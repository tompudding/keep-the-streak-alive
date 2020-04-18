import ui
import globals
from globals.types import Point

class GameView(ui.RootElement):

    def __init__(self):
        #self.atlas = globals.atlas = drawing.texture.TextureAtlas('tiles_atlas_0.png','tiles_atlas.txt')
        #globals.ui_atlas = drawing.texture.TextureAtlas('ui_atlas_0.png','ui_atlas.txt',extra_names=False)
        super(GameView,self).__init__(Point(0,0),globals.screen)

    def update(self, t):
        pass

    def draw(self):
        pass

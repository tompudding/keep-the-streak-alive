# -*- mode: python -*-
import PyInstaller
import pymunk

block_cipher = None

pymunk_dir = os.path.dirname(pymunk.__file__)

a = Analysis(
    ["keep_the_streak_alive.py"],
    pathex=["/home/pudding/Projects/ludum_dare_entries/keep_the_streak_alive"],
    # binaries=[(pymunk.chipmunk_path, ".")],
    datas=[],
    hiddenimports=PyInstaller.utils.hooks.collect_submodules("pkg_resources"),
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
# image_tree = Tree("/src/dinosmustdie/", prefix="resource")
shader_tree = Tree("drawing", prefix="drawing")
resource = Tree("resource", prefix="resource")
# a.datas += image_tree
a.datas += shader_tree
a.datas += resource

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name="keep_the_streak_alive",
    debug=False,
    strip=False,
    upx=True,
    console=True,
    exclude_binaries=0,
)

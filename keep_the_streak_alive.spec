# -*- mode: python -*-
import PyInstaller
import pymunk
block_cipher = None

pymunk_dir = os.path.dirname(pymunk.__file__)

a = Analysis(['keep_the_streak_alive.py', 'keep_the_streak_alive.spec'],
             pathex=['c:\\Users\\tom\\Documents\\keep-the-streak-alive'],
             binaries=[(pymunk.chipmunk_path, '.')],
             datas=None,
             hiddenimports=PyInstaller.utils.hooks.collect_submodules('pkg_resources'),
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
image_tree = Tree('c:\\Users\\tom\\Documents\\keep-the-streak-alive\\resource', prefix='resource')
shader_tree = Tree('c:\\Users\\tom\\Documents\\keep-the-streak-alive\\drawing', prefix='drawing')

a.datas += image_tree
a.datas += shader_tree

exe = EXE(pyz,
          a.scripts,
          #a.binaries,
          #a.zipfiles,
          #a.datas,
          name='keep_the_streak_alive',
          debug=False,
          strip=False,
          upx=True,
          console=True ,
          exclude_binaries =1
)
dist = COLLECT(exe, a.binaries, a.zipfiles, a.datas, name='keep_the_streak_alive')


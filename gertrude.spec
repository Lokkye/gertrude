# -*- mode: python -*-
a = Analysis(['gertrude.pyw'],
             pathex=['C:\\Perso\\Workspace\\Gertrude'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='gertrude.exe',
          debug=False,
          strip=None,
          upx=True,
          console=False,
          icon='bitmaps_dist\\gertrude.ico' )
coll = COLLECT(exe,
               a.binaries + [(x, x, 'DATA') for x in glob.glob("*.ini.dist") + glob.glob("demo.db") + glob.glob("*.php") + glob.glob("bitmaps_dist\\*.png") + glob.glob("bitmaps_dist\\pictos\\*.png") + glob.glob("bitmaps_dist\\*.ico") + glob.glob("templates_dist\\*.html") + glob.glob("templates_dist\\*.txt") + glob.glob("templates_dist\\*.od?")],
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name='gertrude')

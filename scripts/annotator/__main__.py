import sys
import os.path


# Reformat argv[0] like unittest
if sys.argv[0].endswith("__main__.py"):
    executable = os.path.basename(sys.executable)
    sys.argv[0] = executable + " -m " + __package__


# Pop argv[1] if it's the CWD (PyDev weirdness)
try:
    if sys.argv[1] == os.path.abspath(__package__):
        del sys.argv[1]
except IndexError:
    pass


if not 'dump' in sys.argv:
    from gi.repository import Gtk
    from . import AnnotatorWindow

    win = AnnotatorWindow()
    win.prep_show()
    Gtk.main()

else:
    from .config import PKL_TAGSTORE, TAG_STYLE
    from .tagger import TagStore
    ts = TagStore(PKL_TAGSTORE)
    ts.load()
    ts.dump('tagstore_dump.csv')
    #for



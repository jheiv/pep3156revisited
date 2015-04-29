import sys, os
# Ugly hack to allow running this as a module in a subdirectory through Eclipse
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import annotator
__package__ = 'annotator'
# /end hack

from gi.repository import Gtk

from . import AnnotatorWindow

win = AnnotatorWindow()
win.prep_show()
Gtk.main()
import re

from gi.repository import Gtk, Pango, Gdk, GtkSource

from .tagger import Tagger
from .common import *
from . import config

class AnnotatorWindow(Gtk.Window):

    def __init__(self):
        # Code completion hints, will be clobbered
        self.textbuff = Gtk.TextBuffer()

        # Init
        super().__init__(title="Annotator")
        self.set_border_width(5)
        self.set_default_size(400, 550)

        use_source_view = True
        if use_source_view:
            self.textview = GtkSource.View()
        else:
            self.textview = Gtk.TextView()
        self.textview = GtkSource.View()
        self.textview.set_border_width(10)
        self.textview.modify_font(Pango.font_description_from_string("Consolas 11"))
        self.textview.set_editable(False)


        if use_source_view:
            self.textview.set_show_line_numbers(True)
            gutter = self.textview.get_gutter(Gtk.TextWindowType.LEFT)

            def find_gutter_renderer():
                for x in range(-30,30):
                    for y in range(-30,30):
                        z = gutter.get_renderer_at_pos(x,y)
                        if z is not None: return z

            renderer = find_gutter_renderer()
            renderer.set_background(RGBA('#363636'))
            renderer.set_padding(7,-1)



        self.textbuff = self.textview.get_buffer()
        self.load_file(config.PEP_FILE)

        self.textswin = Gtk.ScrolledWindow()
        self.textswin.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)  # @UndefinedVariable
        self.textswin.add(self.textview)


        self.statusbar = Gtk.Statusbar()


        self.mainbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.mainbox.pack_start(self.textswin,    expand=True,  fill=True,  padding=0)
        self.mainbox.pack_start(Gtk.HSeparator(), expand=False, fill=False, padding=2)
        self.mainbox.pack_start(self.statusbar,   expand=False, fill=False, padding=0)


        self.add(self.mainbox)

        self.tagger = Tagger(self.textbuff)

        # CSS
        self.css_prov = Gtk.CssProvider()
        self.css_prov.load_from_data(bytes("""
        GtkTextView {
            color: #EEEEEE;
            background-color: #242424;
        }

        GtkTextView:selected {
            color: #000000;
            background-color: #898941;
        }


        """.encode()))

        screen = Gdk.Display.get_default().get_default_screen()
        Gtk.StyleContext.add_provider_for_screen(screen, self.css_prov, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        # Formatting?
        self.tag_code = self.textbuff.create_tag("code", foreground='#CAE682')
        self.tag_all(re.compile(r'``.*?``'), self.tag_code)


        self.status_push("Initialized.")

    def status_push(self, text, context_desc=None):
        context_id = self.statusbar.get_context_id(str(context_desc))
        return self.statusbar.push(context_id, text)


    def key_press(self, widget, event, user_data=None):
        #event = Gdk.EventKey()
        #print(event.get_state())
        #print(event.get_keycode()) # This will return the upper case version, regardless of shift
        #print(event.get_keyval())  # This will return the upper or lower case version depending
                                    #   (only on) shift (i.e. not caps lock)
        if event.get_state() & Gdk.ModifierType.CONTROL_MASK:
            keyval = event.get_keyval()[1]
            if keyval == ord('s'):
                res = self.tagger.tag()
                if res is None:
                    self.status_push("Created tag")
                else:
                    self.status_push(res[1])
                    self.raise_modal("Could not add tag: %s" % res[1],
                                     message_type = Gtk.MessageType.ERROR,
                                     buttons=Gtk.ButtonsType.OK)

            if keyval == ord('r'):
                self.tagger.rem()
                self.status_push("Removed tag")

            if keyval == ord('d'):
                print("Ctrl+D")
                print(self.textbuff.get_property('cursor-position'))



        # Return True no matter what the event, since the TextView is not editable and to suppress
        #  the bell sounds
        return True

    def load_file(self, filename):
        with open(filename, "r", encoding='utf-8') as f: cont = f.read()
        self.textbuff.set_text(cont)

    def tag_all(self, regex_obj, tag):
        offset = 0
        buff = self.textbuff
        text = buff.get_text(buff.get_start_iter(), buff.get_end_iter(), True)
        while True:
            mat = regex_obj.search(text, offset)
            if mat is None: break
            offset = mat.end()
            siter = buff.get_iter_at_offset(mat.start())
            eiter = buff.get_iter_at_offset(mat.end())
            buff.apply_tag(tag, siter, eiter)


    def prep_show(self):
        def shift_mouse_event(widget, event, user_data=None):
            wbw = widget.get_border_width()
            event.x -= wbw
            event.y -= wbw
            return False

        def event_info(widget, event, user_data=None):
            print(widget)
            print(event)
            print(type(event))
            return False

        self.connect("delete-event", Gtk.main_quit)
        self.connect("key-press-event", self.key_press)
        # Since our TextView has a border, the mouse event coordinates are offset (bug?)
        self.textview.connect("button-press-event",   shift_mouse_event)
        self.textview.connect("button-release-event", shift_mouse_event)
        self.textview.connect('motion-notify-event',  shift_mouse_event)

        self.show_all()


    def raise_modal(self, message, *,
                    message_type: Gtk.MessageType=None,
                    buttons: Gtk.ButtonsType=None,
                    title=None):
        # Handle defaults
        if buttons is None:      buttons      = Gtk.ButtonsType.OK
        if message_type is None: message_type = Gtk.MessageType.INFO
        if title is None:        title        = self.get_title()

        # Create and raise
        md = Gtk.MessageDialog(parent=self,
                               message_type=message_type,
                               buttons=buttons,
                               message_format=message)
        md.set_title(title)
        resp = md.run()
        md.destroy()
        return resp

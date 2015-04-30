import re
import sys
from enum import Enum

from gi.repository import Gtk, Pango, Gdk, GtkSource

from .tagger import Tagger
from .entrydialog import EntryDialog
from .selection import Selection
from .common import *
from . import config

class KeySequenceState(Enum):
    WaitingInitiator = 1
    FoundInitiator = 2



class AnnotatorWindow(Gtk.Window):

    def __init__(self):
        # Code completion hints, will be clobbered
        self.textbuff = Gtk.TextBuffer()

        # Init
        super().__init__(title="Annotator")
        self.set_border_width(5)
        self.set_default_size(800, 850)

        use_source_view = True
        if use_source_view:
            self.textview = GtkSource.View()
        else:
            self.textview = Gtk.TextView()
        self.textview = GtkSource.View()
        self.textview.set_border_width(10)
        self.textview.modify_font(Pango.font_description_from_string("Consolas 11"))
        self.textview.set_editable(False)
        #self.textview.set_size_request(800, 650)


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


        info_l = ("<b>Ctrl+a, c:</b>\t Add Claim\n"
                  "<b>Ctrl+a, e:</b>\t Add Edit\n"
                  "<b>Ctrl+r:</b>\t\t Remove tagged selection\n")

        info_r = ("<b>Ctrl+e, c:</b>\t Edit Claim (does nothing)\n"
                  "<b>Ctrl+e, e:</b>\t Edit Edit\n"
                  "<b>Ctrl+d:</b>\t\t Debug Hotkey - could do anything\n")

        self.help_info_l = Gtk.Label()
        self.help_info_l.set_markup(info_l)
        self.help_info_l.set_halign(Gtk.Align.START)
        self.help_info_l.set_valign(Gtk.Align.START)
        self.help_info_l.set_name("help_info_l")

        help_vsep = Gtk.VSeparator()

        self.help_info_r = Gtk.Label()
        self.help_info_r.set_markup(info_r)
        self.help_info_r.set_halign(Gtk.Align.START)
        self.help_info_r.set_valign(Gtk.Align.START)
        self.help_info_r.set_name("help_info_r")


        self.helpbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.helpbox.pack_start(self.help_info_l, expand=True,  fill=True,  padding=5)
        self.helpbox.pack_start(help_vsep,        expand=False, fill=False, padding=0)
        self.helpbox.pack_start(self.help_info_r, expand=True,  fill=True,  padding=5)

        self.statusbar = Gtk.Statusbar()

        self.mainbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.mainbox.pack_start(self.textswin,    expand=True,  fill=True,  padding=0)
        self.mainbox.pack_start(self.helpbox,     expand=False, fill=True,  padding=0)
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
        self.tag_all(re.compile(r'^.*\n\=+\n', re.MULTILINE), self.textbuff.create_tag("head1", foreground='#F0BE35'))
        self.tag_all(re.compile(r'^.*\n\-+\n', re.MULTILINE), self.textbuff.create_tag("head2", foreground='#35BBF0'))
        self.tag_all(re.compile(r'^.*\n\'+\n', re.MULTILINE), self.textbuff.create_tag("head3", foreground='#9F68F7'))

        self.key_seq_state = KeySequenceState.WaitingInitiator
        self.key_seq_hist  = None

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

        keyval = event.get_keyval()[1]
        keychr = chr(keyval)
        if self.key_seq_state == KeySequenceState.WaitingInitiator:
            if event.get_state() & Gdk.ModifierType.CONTROL_MASK:
                if keychr in 'ae':
                    self.key_seq_hist = keychr
                    self.key_seq_state = KeySequenceState.FoundInitiator

                elif keychr == 'r':
                    # Remove
                    self.tagger.rem_tagged_sel()
                    self.status_push("Removed tag")

                elif keychr == 'd':
                    print("Ctrl+D: DEBUG")
                    print(self.textbuff.get_property('cursor-position'))

                elif keychr == 'c':
                    # Allow "default" event handlers to handle these
                    return False




        elif self.key_seq_state == KeySequenceState.FoundInitiator:
            key_seq = (self.key_seq_hist, keychr)
            #------------------------------------------------------- # Do something with a CLAIM tag
            if key_seq == ('a','c'):
                res = self.tagger.add_tagged_sel('CLAIM')
                if res is None:
                    self.status_push("Created tag")
                else:
                    self.status_push(res[1])
                    self.raise_modal("Could not add tag: %s" % res[1],
                                     message_type = Gtk.MessageType.ERROR,
                                     buttons=Gtk.ButtonsType.OK)
            elif key_seq == ('e','c'):
                cp = self.textbuff.get_property('cursor-position')      # Get cursor position

                tag_sel_idx  = self.tagger.store.find_selection_index(cp, name_filter='CLAIM')
                if tag_sel_idx is not None:
                    tag_sel      = self.tagger.store[tag_sel_idx]
                    tag_sel_note = tag_sel.note

                    ed = EntryDialog(self,
                                     message_format="Enter edit note:",
                                     message_type=Gtk.MessageType.QUESTION,
                                     buttons=Gtk.ButtonsType.OK,
                                     default_value=tag_sel_note)
                    note = ed.run()
                    ed.destroy()
                    if note is not None: self.tagger.edit_tagged_sel(tag_sel_idx, note=note)

            #------------------------------------------------------- # Do something with an EDIT tag
            elif key_seq == ('a','e'):
                sel = Selection.from_buffer_selection(self.textbuff)    # Grab selection
                ed = EntryDialog(self,
                                 message_format="Enter edit note:",
                                 message_type=Gtk.MessageType.QUESTION,
                                 buttons=Gtk.ButtonsType.OK)
                note = ed.run()
                ed.destroy()
                res = self.tagger.add_tagged_sel('EDIT', note=note, sel=sel)

            elif key_seq == ('e','e'):
                cp = self.textbuff.get_property('cursor-position')      # Get cursor position

                tag_sel_idx  = self.tagger.store.find_selection_index(cp, name_filter='EDIT')
                if tag_sel_idx is not None:
                    tag_sel      = self.tagger.store[tag_sel_idx]
                    tag_sel_note = tag_sel.note

                    ed = EntryDialog(self,
                                     message_format="Enter edit note:",
                                     message_type=Gtk.MessageType.QUESTION,
                                     buttons=Gtk.ButtonsType.OK,
                                     default_value=tag_sel_note)
                    note = ed.run()
                    ed.destroy()
                    if note is not None: self.tagger.edit_tagged_sel(tag_sel_idx, note=note)

            # Reset key_seq stuff
            self.key_seq_hist = None
            self.key_seq_state = KeySequenceState.WaitingInitiator



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
        self.textview.connect_after('motion-notify-event', self.on_mouse_move)

        self.show_all()

    # Tagged Selection hover tooltip support
    def on_mouse_move(self, widget, event):
        print(widget)
        print(event)


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

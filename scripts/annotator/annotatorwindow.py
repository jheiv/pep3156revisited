import re
from enum import Enum

from gi.repository import Gtk, Pango, Gdk, GtkSource

from .tagger import Tagger
from .selection import Selection
from .dialog import *
from .common import *
from . import config



class EditTagDialog(InputDialog):
    def __init__(self, default_note, **kwargs):
        super().__init__(message="Enter edit note:",
                         default_value=default_note,
                         buttons=Gtk.ButtonsType.OK,
                         **kwargs)



class UpdateErrorDialog(MessageDialog):
    def __init__(self, error_message, **kwargs):
        super().__init__(message=error_message,
                         **kwargs)



class KeySequenceState(Enum):
    WaitingInitiator = 1
    FoundInitiator = 2



class AnnotatorWindow(Gtk.Window):
    def __init__(self):
        # Code completion hints, will be clobbered
        self.textbuff = Gtk.TextBuffer()

        #------------------------------------------------------------------- Begin UI Initialization
        # Init
        super().__init__(title="Annotator")
        self.set_border_width(5)
        self.set_default_size(800, 850)

        # Initialize TextView, TextBuffer, ScrolledWindow
        self.textview = GtkSource.View()
        self.textview.set_border_width(10)
        self.textview.modify_font(Pango.font_description_from_string(config.TEXTVIEW_FONTDESC))
        self.textview.set_editable(False)
        self.textview.set_show_line_numbers(True)
        #self.textview.set_highlight_current_line(True)
        gutter = self.textview.get_gutter(Gtk.TextWindowType.LEFT)

        def find_gutter_renderer():
            for x in range(-30,30):
                for y in range(-30,30):
                    z = gutter.get_renderer_at_pos(x,y)
                    if z is not None: return z

        renderer = find_gutter_renderer()
        renderer.set_background(RGBA(config.TEXTVIEW_GUTTER_BG))
        renderer.set_padding(7,-1)

        self.textbuff = self.textview.get_buffer()
        self.load_file(config.PEP_FILE)

        self.textswin = Gtk.ScrolledWindow()
        self.textswin.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)  # @UndefinedVariable
        self.textswin.add(self.textview)

        # Initialize Info Labels, container Box
        self.help_info_l = Gtk.Label(name="help_info_l", halign=Gtk.Align.START, valign=Gtk.Align.START)
        self.help_info_l.set_markup("<b>Ctrl+a, c:</b>\t Add Claim\n"
                                    "<b>Ctrl+a, e:</b>\t Add Edit\n"
                                    "<b>Ctrl+r:   </b>\t Remove tagged selection\n")

        self.help_info_r = Gtk.Label(name="help_info_r", halign=Gtk.Align.START, valign=Gtk.Align.START)
        self.help_info_r.set_markup("<b>Ctrl+e, c:</b>\t Edit Claim\n"
                                    "<b>Ctrl+e, e:</b>\t Edit Edit\n"
                                    "<b>Ctrl+d:   </b>\t Debug Hotkey - could do anything!\n")

        self.helpbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.helpbox.pack_start(self.help_info_l, expand=True,  fill=True,  padding=5)
        self.helpbox.pack_start(Gtk.VSeparator(), expand=False, fill=False, padding=0)
        self.helpbox.pack_start(self.help_info_r, expand=True,  fill=True,  padding=5)

        # Initialize Statusbar
        self.statusbar = Gtk.Statusbar()

        # Initialize main Box
        self.mainbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.mainbox.pack_start(self.textswin,    expand=True,  fill=True,  padding=0)
        self.mainbox.pack_start(self.helpbox,     expand=False, fill=True,  padding=0)
        self.mainbox.pack_start(Gtk.HSeparator(), expand=False, fill=False, padding=2)
        self.mainbox.pack_start(self.statusbar,   expand=False, fill=False, padding=0)

        self.add(self.mainbox)

        # CSS
        self.css_prov = Gtk.CssProvider()
        self.css_prov.load_from_data(config.APP_CSS.encode())

        screen = Gdk.Display.get_default().get_default_screen()
        Gtk.StyleContext.add_provider_for_screen(screen, self.css_prov, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        # Source Formatting?  Very basic!
        markup_patterns = {
            'code':  re.compile(r'``[^`]*``', re.MULTILINE),
            'head1': re.compile(r'^.*\n\=+\n', re.MULTILINE),
            'head2': re.compile(r'^.*\n\-+\n', re.MULTILINE),
            'head3': re.compile(r'^.*\n\'+\n', re.MULTILINE),
        }

        for (tag_name, pattern) in markup_patterns.items():
            style = config.MARKUP_STYLE[tag_name]
            self.tag_all(pattern, self.textbuff.create_tag(tag_name, **style))

        #--------------------------------------------------------------------- End UI Initialization
        self.tagger = Tagger(self.textbuff)

        # Key combination history
        self.key_seq_state = KeySequenceState.WaitingInitiator
        self.key_seq_hist  = None

        self.status_push("Initialized.")


    # Update status bar
    # TODO: Use this properly
    def status_push(self, text, context_desc=None):
        context_id = self.statusbar.get_context_id(str(context_desc))
        return self.statusbar.push(context_id, text)


    # This is pretty gross, but functional
    def key_press(self, widget, event, user_data=None):
        #event = Gdk.EventKey()
        #print(event.get_state())
        #print(event.get_keycode()) # This will return the upper case version, regardless of shift
        #print(event.get_keyval())  # This will return the upper or lower case version depending
                                    #   (only on) shift (i.e. not caps lock)
        #-------------------------------------------------------------------- Local Helper Functions
        def add_tagged_sel(tag_name, prompt_note):
            sel = Selection.from_buffer_selection(self.textbuff)
            note = self.raise_dialog(EditTagDialog, '') if prompt_note else None
            res = self.tagger.add_tagged_sel(tag_name, note=note, sel=sel)

            if res is None:
                self.status_push("Created tagged selection")
            else:
                self.status_push(res[1])
                self.raise_dialog(UpdateErrorDialog, "Could not add tagged selection: %s" % res[1])


        def edit_tagged_sel(tag_name):
            cp = self.textbuff.get_property('cursor-position')          # Get cursor position
            tag_sel_idx  = self.tagger.store.find_selection_index(cp, name_filter=tag_name)
            if tag_sel_idx is not None:
                note = self.raise_dialog(EditTagDialog, self.tagger.store[tag_sel_idx].note)
                if note is not None:
                    self.tagger.edit_tagged_sel(tag_sel_idx, note=note)


        #------------------------------------------------------------------------------- Begin Logic
        keyval = event.get_keyval()[1]
        keychr = chr(keyval)
        if self.key_seq_state == KeySequenceState.WaitingInitiator:
            if event.get_state() & Gdk.ModifierType.CONTROL_MASK:
                if keychr in 'ae':                                      # Check for initiator keys
                    self.key_seq_hist = keychr
                    self.key_seq_state = KeySequenceState.FoundInitiator

                elif keychr == 'r':                                     # Remove tag
                    err = self.tagger.rem_tagged_sel()
                    if err: self.status_push(err)
                    else:   self.status_push("Removed tag")

                elif keychr == 'j':                                     # Jump dialog
                    jline = 750
                    jiter = self.textbuff.get_iter_at_line(jline)
                    self.textview.scroll_to_iter(jiter, 0, True, 0.5, 0.5)

                elif keychr == 'd':                                     # Debug hotkey
                    print("Ctrl+D: DEBUG")
                    resp = self.raise_dialog(MessageDialog, "Message")
                    print(resp)
                    resp = self.raise_dialog(InputDialog, "Message", default_value="default")
                    print(resp)

                elif keychr == 'c':
                    # Allow "default" event handlers to handle these
                    return False

        elif self.key_seq_state == KeySequenceState.FoundInitiator:
            key_seq = (self.key_seq_hist, keychr)
            #----------------------------------------------------------------------------- Add a tag
            if   key_seq == ('a','c'): add_tagged_sel('CLAIM', prompt_note=False)
            elif key_seq == ('a','d'): add_tagged_sel('PROTO', prompt_note=False)
            elif key_seq == ('a','e'): add_tagged_sel('EDIT',  prompt_note=True)
            #---------------------------------------------------------------------------- Edit a tag
            elif key_seq == ('e','c'): edit_tagged_sel('CLAIM')
            elif key_seq == ('e','d'): edit_tagged_sel('PROTO')
            elif key_seq == ('e','e'): edit_tagged_sel('EDIT')
            #------------------------------------------------------------------- Reset key_seq stuff
            self.key_seq_hist = None
            self.key_seq_state = KeySequenceState.WaitingInitiator

        # Return True no matter what the event, since the TextView is not editable and to suppress
        #  the bell sounds
        return True


    # Load a file's contents into the TextView TextBuffer
    def load_file(self, filename):
        with open(filename, "r", encoding='utf-8') as f: cont = f.read()
        self.textbuff.set_text(cont)


    # Tag all matches of regex_obj with tag
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


    # Prepare the window by connecting event handlers and showing it
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
        self.textview.connect('motion-notify-event',  self.on_mouse_move)
        # Since our TextView has a border, the mouse event coordinates are offset (bug?)
        #   (Must be connected after (logic-wise) any handlers that hook these events)
        self.textview.connect("button-press-event",   shift_mouse_event)
        self.textview.connect("button-release-event", shift_mouse_event)
        self.textview.connect('motion-notify-event',  shift_mouse_event)

        self.show_all()


    # Tagged Selection hover tooltip support
    def on_mouse_move(self, widget, event):
        window_type = self.textview.get_window_type(event.window)
        bx, by = self.textview.window_to_buffer_coords(window_type, event.x, event.y)
        (view_iter, _) = self.textview.get_iter_at_position(bx, by)
        iter_offset = view_iter.get_offset()
        tagged_sels = self.tagger.store.find_all_tagged_selections(iter_offset)

        if tagged_sels:
            tooltip_text = '\n---\n'.join([ts.note for ts in tagged_sels])
            if tooltip_text.strip() == '': tooltip_text = '<i>No note specified</i>'
        else:
            tooltip_text = None

        self.textview.set_tooltip_markup(tooltip_text)


    # Create a dialog (with this as its parent), and run it
    def raise_dialog(self, dialog, *args, **kwargs):
        kwargs['parent'] = self
        return dialog(*args, **kwargs).run()


from gi.repository import Gtk

class EntryDialog(Gtk.MessageDialog):
    def __init__(self, *args, **kwargs):
        '''
        Creates a new EntryDialog. Takes all the arguments of the usual
        MessageDialog constructor plus one optional named argument
        "default_value" to specify the initial contents of the entry.
        '''
        if 'default_value' in kwargs:
            default_value = kwargs.pop('default_value')
        else:
            default_value = ''

        super().__init__(*args, **kwargs)
        entry = Gtk.Entry()
        entry.set_width_chars(50)
        #entry = Gtk.TextView()
        entry.set_text(str(default_value))
        entry.connect("activate",
                      lambda ent, dlg, resp: dlg.response(resp),
                      self, Gtk.ResponseType.OK)
        self.vbox.pack_end(entry, True, True, 0)
        self.vbox.show_all()
        self.entry = entry


    def set_value(self, text):
        self.entry.set_text(text)


    def run(self):
        result = super().run()
        if result == Gtk.ResponseType.OK:
            text = self.entry.get_text()
        else:
            text = None
        return text
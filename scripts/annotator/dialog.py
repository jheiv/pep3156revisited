from gi.repository import Gtk

__all__ = ['MessageDialog', 'InputDialog']

class Defaults(dict):
    def apply_to(self, kwargs_dict):
        for (k,v) in self.items():
            if k not in kwargs_dict:
                kwargs_dict[k] = v



class BaseDialog:
    pass


class MessageDialog(BaseDialog):
    def __init__(self, message, *, title=None, **kwargs):
        '''
        message_type:  Gtk.MessageType = Gtk.MessageType.INFO,
        buttons:       Gtk.ButtonsType = Gtk.ButtonsType.OK,
        '''
        Defaults(
            message_type = Gtk.MessageType.INFO,
            buttons      = Gtk.ButtonsType.OK,
        ).apply_to(kwargs)

        self.dialog = Gtk.MessageDialog(message_format=message, **kwargs)
        if title is not None: self.dialog.set_title(title)

    def run(self):
        response = self.dialog.run()
        self.dialog.destroy()
        return response



class InputDialog(BaseDialog):
    def __init__(self, message, *, title=None, default_value=None, **kwargs):
        '''
        message_type:  Gtk.MessageType = Gtk.MessageType.QUESTION,
        buttons:       Gtk.ButtonsType = Gtk.ButtonsType.OK,
        '''
        Defaults(
            message_type = Gtk.MessageType.QUESTION,
            buttons      = Gtk.ButtonsType.OK,
        ).apply_to(kwargs)

        self.dialog = Gtk.MessageDialog(message_format=message, **kwargs)
        if title is not None: self.dialog.set_title(title)

        self.entry = Gtk.Entry()
        self.entry.set_width_chars(50)
        if default_value is not None: self.entry.set_text(default_value)

        self.entry.connect("activate", self.handle_activate)

        self.dialog.vbox.pack_end(self.entry, True, True, 0)
        self.dialog.vbox.show_all()

    def handle_activate(self, widget):
        self.dialog.response(Gtk.ResponseType.OK)

    def run(self):
        response = self.dialog.run()
        response = self.entry.get_text() if response == Gtk.ResponseType.OK else None
        self.dialog.destroy()
        return response



import pickle

from gi.repository import Gtk

from . import config
from .selection import Selection
from .taggedselection import TaggedSelection
from .entrydialog import EntryDialog

class TagStore:
    def __init__(self, path):
        self.path = path
        self.sels = []

    # Loads a pickled tagstore
    def load(self, buff):
        try:
            with open(self.path, 'rb') as f:
                self.sels = pickle.load(f)
                print("Loaded tagstore (%d tagged selections)" % len(self.sels))
                for ts in self.sels: print("  ", ts, sep='')
                # Set buff attribute (it's not pickled)
                for ts in self.sels:
                    ts.buff = buff
        except FileNotFoundError:
            print("Couldn't load tagstore")


    # Saves the local tagstore to file
    def save(self):
        with open(self.path, 'wb') as f:
            pickle.dump(self.sels, f)

    #===============================================================================================
    # Magic Methods
    #===============================================================================================
    def __getitem__(self, key):
        return self.sels[key]


    #===============================================================================================
    # Helper Methods
    #===============================================================================================
    # Helper method to find a tagged selection in the tagstore that contains a cursor position
    def find_selection_index(self, cp, name_filter=None):
        for (i,sel) in enumerate(self):
            if name_filter is not None and name_filter != sel.name: continue
            if cp in sel: return i
        return None

    def selection_conflicts(self, test, name_filter=None):
        for (i,sel) in enumerate(self):
            if name_filter is not None and name_filter != sel.name: continue
            if sel.conflicts_with(test): return True
        return False

    def find_all_tagged_selections(self, cp):
        tagged_selections = []
        for sel in self:
            if cp in sel: tagged_selections.append(sel)
        return tagged_selections



class Tagger:
    def __init__(self, buffer):
        self.buff = buffer
        self.tags = {}
        for (tag_name, tag_style) in config.TAG_STYLE:
            self.tags[tag_name] = self.buff.create_tag(tag_name, **tag_style)

        # Load tags from tagstore
        self.store = TagStore(config.PKL_TAGSTORE)
        self.store.load(buffer)

        self.apply_tags()





    #===============================================================================================
    # Helper Methods
    #===============================================================================================


    #===============================================================================================
    # Tag "Painter" Methods
    #===============================================================================================
    # Clear all instances of a single tag from the TextBuffer
    def clear_tag(self, tag):
        if isinstance(tag, str): tag = self.tags[tag]
        self.buff.remove_tag(tag, self.buff.get_start_iter(), self.buff.get_end_iter())


    # Clears all instances of all our tags from the TextBuffer
    def clear_tags(self):
        for tag in self.tags.values(): self.clear_tag(tag)


    # Applies all tags from the loaded tagstore
    def apply_tags(self):
        for tagged_sel in self.store.sels:
            tagged_sel.apply()


    def refresh(self):
        self.clear_tags()
        self.apply_tags()

    #===============================================================================================
    # Add / Remove Tagged Selections
    #===============================================================================================
    # Called from a keypress event
    def add_tagged_sel(self, tag_name, *, note=None, sel=None):
        if sel is None: sel = Selection.from_buffer_selection(self.buff)

        if self.store.selection_conflicts(sel, name_filter=tag_name):
            print("Tag collision.")
            return (False, "Tag collision.")


        if note is None: note = ''
        tagged_sel = TaggedSelection(self.buff, tag_name, sel, note)
        self.store.sels.append(tagged_sel)

        print("Created tag: %s" % tagged_sel)

        self.store.save()
        self.refresh()


    # Called from a keypress event
    def rem_tagged_sel(self):
        cp = self.buff.get_property('cursor-position')
        i = self.store.find_selection_index(cp)
        tagged_sel = self.store.sels.pop(i)
        print("Removed tag: %s" % tagged_sel)

        self.store.save()
        self.refresh()

    # Called from a keypress event
    def edit_tagged_sel(self, tag_sel_idx, *, note=None):
        tagged_sel = self.store[tag_sel_idx]
        old_note = tagged_sel.note
        tagged_sel.note = note
        print("Updated note: %s -> %s" % (repr(old_note), repr(note)))

        self.store.save()




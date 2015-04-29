import pickle

from . import config
from .selection import Selection


class Tagger:
    def __init__(self, buffer):
        self.buff = buffer
        self._tag = self.buff.create_tag("tag_bg", background="#314A94")

        # Load tags from tagstore
        try:
            with open(config.PKL_TAGSTORE,'rb') as f:
                self.tags = pickle.load(f)
                print("Loaded tagstore")
                for t in self.tags: print("  ", t, sep='')

                self.apply_tags()
        except FileNotFoundError:
            self.tags = []


    # Clears all of our tags from the textbuffer
    def clear_tags(self):
        self.buff.remove_tag(self._tag, self.buff.get_start_iter(), self.buff.get_end_iter())


    # Applies all tags from the loaded tagstore
    def apply_tags(self):
        for (so,eo) in self.tags:
            sel = Selection.from_buffer_offsets(self.buff, so, eo)
            self.buff.apply_tag(self._tag, sel.siter, sel.eiter)


    # Saves the local tagstore to file
    def update_tagstore(self):
        with open(config.PKL_TAGSTORE, 'wb') as f:
            pickle.dump(self.tags, f)


    # Helper method to find a tag in the tagstore that wraps a cursor position
    def _find_tag_index(self, cp):
        for (i,(so,eo)) in enumerate(self.tags):
            if so <= cp <= eo:
                return i
        return None

    # Called from a keypress event
    def tag(self):
        sel = Selection.from_buffer_selection(self.buff)


        def check_sel(sel):
            for (tso, teo) in self.tags:
                # Make sure neither end of our selection is inside an existing tag
                if tso in sel: return False
                if teo in sel: return False
                # Make sure our selection isn't wholly contained inside an existing tag
                if (tso < sel.so < teo) and (tso < sel.eo < teo): return False
            return True

        if not check_sel(sel):
            print("Tag collision.")
            return (False, "Tag collision.")

        self.tags.append((sel.siter.get_offset(), sel.eiter.get_offset()))
        print("Created tag: [%d:%d]" % (sel.siter.get_offset(), sel.eiter.get_offset()))

        self.update_tagstore()
        self.clear_tags()
        self.apply_tags()


    # Called from a keypress event
    def rem(self):
        cp = self.buff.get_property('cursor-position')
        i = self._find_tag_index(cp)
        (so, eo) = self.tags[i]
        del self.tags[i]
        print("Removed tag: [%d:%d]" % (so, eo))

        self.update_tagstore()
        self.clear_tags()
        self.apply_tags()


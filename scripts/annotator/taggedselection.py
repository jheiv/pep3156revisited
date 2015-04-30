from .selection import Selection

class TaggedSelection:
    def __init__(self, buffer, tag_name, sel, note=None):
        self.buff = buffer
        self.name = tag_name
        self.sel  = sel
        self.note = note


    #===============================================================================================
    # Properties
    #===============================================================================================
    @property
    def so(self): return self.sel.so

    @property
    def eo(self): return self.sel.eo

    @property
    def si(self): return self.buff.get_iter_at_offset(self.sel.so)

    @property
    def ei(self): return self.buff.get_iter_at_offset(self.sel.eo)


    #===============================================================================================
    # Alternate Constructors
    #===============================================================================================
    @classmethod
    def from_iters(cls, buffer, tag_name, siter, eiter):
        sel = Selection.from_iters(siter, eiter)
        return cls(buffer, tag_name, sel)

    @classmethod
    def from_buffer_selection(cls, buffer, tag_name):
        sel = Selection.from_buffer_selection(buffer)
        return TaggedSelection.from_iters(buffer, tag_name, sel)


    #===============================================================================================
    # Magic Methods
    #===============================================================================================
    def __repr__(self):
        args = [repr(self.name), str(self.so), str(self.eo)]
        if self.note is not None: args.append(repr(self.note))
        return "TaggedSelection(%s)" % ', '.join(args)


    def __getstate__(self):
        # Don't pickle buffer (self.buff)
        state = {
            'name': self.name,
            'sel':  self.sel,
            'note': self.note,
        }
        return state

    # Test whether a given cursor position is inside this selection range
    def __contains__(self, cp):
        return (cp in self.sel)


    #===============================================================================================
    # Helper Methods
    #===============================================================================================
    def conflicts_with(self, sel):
        return self.sel.conflicts_with(sel)


    #===============================================================================================
    # Painters
    #===============================================================================================
    def apply(self):
        self.buff.apply_tag_by_name(self.name, self.si, self.ei)

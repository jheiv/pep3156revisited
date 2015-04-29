
class Selection:
    @classmethod
    def from_buffer_selection(cls, buffer):
        self = cls()
        si, ei = buffer.get_selection_bounds()
        self.siter = si
        self.eiter = ei
        return self

    @classmethod
    def from_buffer_offsets(cls, buffer, so, eo):
        self = cls()
        self.siter = buffer.get_iter_at_offset(so)
        self.eiter = buffer.get_iter_at_offset(eo)
        return self

    @property
    def so(self): return self.siter.get_offset()
    @property
    def eo(self): return self.eiter.get_offset()

    def __contains__(self, cp):
        return self.siter.get_offset() <= cp <= self.eiter.get_offset()

    def __repr__(self):
        return "Selection(%d:%d)" % (self.siter.get_offset(), self.eiter.get_offset())
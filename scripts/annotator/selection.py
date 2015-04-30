
class Selection:
    def __init__(self, soffset, eoffset):
        self.so = soffset
        self.eo = eoffset


    #===============================================================================================
    # Alternate Constructors
    #===============================================================================================
    @classmethod
    def from_iters(cls, siter, eiter):
        so = siter.get_offset()
        eo = eiter.get_offset()
        return cls(so, eo)

    @classmethod
    def from_buffer_selection(cls, buffer):
        si, ei = buffer.get_selection_bounds()
        return cls.from_iters(si, ei)


    #===============================================================================================
    # Magic Methods
    #===============================================================================================
    def __repr__(self):
        return "Selection(%d:%d)" % (self.so, self.eo)

    def __contains__(self, cp):
        return self.so <= cp < self.eo


    #===============================================================================================
    # Helpers
    #===============================================================================================
    def conflicts_with(self, that):
        # Test whether either of that's endpoints are inside this's endpoints
        if that.so in self: return True
        if that.eo in self: return True
        # Test whether either of this's endpoints are inside that's endpoints
        if self.so in that: return True
        if self.eo in that: return True
        # Else, return False
        return False

    def si(self, buffer): buffer.get_iter_at_offset(self.so)
    def ei(self, buffer): buffer.get_iter_at_offset(self.eo)
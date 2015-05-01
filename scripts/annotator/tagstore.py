import pickle
import itertools
from datetime import datetime


class TagStore:
    def __init__(self, path):
        self.path = path
        self.sels = []


    # Loads a pickled tagstore
    def load(self, buff=None):
        try:
            with open(self.path, 'rb') as f:
                self.sels = pickle.load(f)
                print("Loaded tagstore (%d tagged selections)" % len(self.sels))
                for ts in self.sels: print("  ", ts, sep='')
                # Set buff attribute (it's not pickled)
                if buff is not None:
                    for ts in self.sels: ts.buff = buff
        except FileNotFoundError:
            print("Couldn't load tagstore")


    # Saves the local tagstore to file
    def save(self):
        with open(self.path, 'wb') as f:
            pickle.dump(self.sels, f)


    # Dump tagstore contents to a .csv file
    def dump(self, csvfile):
        with open(csvfile, 'w') as f:
            print("# Generated: %s" % datetime.utcnow().ctime(), file=f)
            ssels = sorted(self.sels, key=lambda s:(s.name, s.sel.so))
            for (name,items) in itertools.groupby(ssels, key=lambda s:s.name):
                for ts in items:
                    row = ts.to_list()
                    print(','.join(row), file=f)


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
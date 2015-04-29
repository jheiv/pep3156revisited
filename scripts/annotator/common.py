from gi.repository import Gdk

def d(obj):
    print(type(obj))
    for k in dir(obj): print(k)

def RGBA(s):
    obj = Gdk.RGBA()
    obj.parse(s)
    return obj


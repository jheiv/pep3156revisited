#===================================================================================================
# # File Locations
#===================================================================================================
PEP_FILE     = '../pep/pep-3156.txt'
PKL_TAGSTORE = 'tagstore.pkl'


#===================================================================================================
# # UI Settings
#===================================================================================================
TAG_STYLE = [                                   # The order of list entries is important here,
    ('CLAIM', dict(background="#043B12")),      #   later entries will mask earlier ones if they're
    ('PROTO', dict(background="#314A94")),      #   "on top" of each other -- try to list these in
    ('EDIT',  dict(background="#9E2650")),      #   order from "longest" to "shortest" width.
]

MARKUP_STYLE = {
    'code':  dict(foreground='#CAE682'),
    'head1': dict(foreground='#F0BE35'),
    'head2': dict(foreground='#35BBF0'),
    'head3': dict(foreground='#9F68F7'),
}

TEXTVIEW_FONTDESC = "Consolas 11"

APP_CSS = """
GtkTextView {
    color: #EEEEEE;
    background-color: #242424;
}

GtkTextView:selected {
    color: #000000;
    background-color: #898941;
}


"""

TEXTVIEW_GUTTER_BG = '#363636'
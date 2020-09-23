from getData import df


from bokeh.io import curdoc
from bokeh.models.widgets import Tabs


from IntraPM import IntraPM_tab
from IntraConversation import IntraConversation_tab

tab1 = IntraPM_tab(df)
tab2 = IntraConversation_tab(df)

tabs = Tabs(tabs = [tab1, tab2])

curdoc().add_root(tabs)


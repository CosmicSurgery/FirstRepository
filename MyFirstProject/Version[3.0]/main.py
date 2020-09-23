from scripts.getData import df


from bokeh.io import curdoc
from bokeh.models.widgets import Tabs
from bokeh.themes import built_in_themes


from scripts.groupchat_by_author import groupchat_by_author
from scripts.pm_by_author import pm_by_author
from scripts.groupchat_by_conversation import groupchat_by_conversation
from scripts.pm_by_conversation import pm_by_conversation

tab1 = groupchat_by_author(df)
tab2 = groupchat_by_conversation(df)
tab3 = pm_by_author(df)
tab4 = pm_by_conversation(df)

tabs = Tabs(tabs = [tab1, tab2, tab3, tab4])

curdoc().theme = 'dark_minimal'
curdoc().add_root(tabs)


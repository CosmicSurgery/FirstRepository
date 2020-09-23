'''
Intra-Conversation Tab looks at data between different PM conversations. essentially comparing me to the recipient
for every PM conversation. 

Interesting Column's that I will compare: 'Sent Messages' 'Sent Words' and 'WPM'
Will follow the exact same format Intra-

'''
from getData import df
from bokeh.io import show, output_notebook, output_file, curdoc
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, CDSView, GroupFilter, Legend, LegendItem, Panel
from bokeh.models.widgets import RadioButtonGroup, Select, CheckboxGroup
from bokeh.layouts import column, row
from bokeh.palettes import turbo
from bokeh.embed import server_document








def IntraPM_tab(df):
    pm_df = df.drop(df[~df.Conversation.isin(list(df.Author.unique()))].index)

    metric_selection = ['Sent Messages', 'Sent Words','WPM']
    conversations = list(pm_df.Conversation.unique())
    authors = []

    height = 300
    width = 1000
    #Create Figures

    top = figure(x_axis_type='datetime', frame_height=height, frame_width=width)
    bot = figure(x_axis_type='datetime', frame_height=height, frame_width=width)
    #leaderboard = []

    #Create Widgets

    metric_radio = RadioButtonGroup(labels= metric_selection,
                                   active=1)
    conversation_select = Select(title='Conversation',
                                value =conversations[0],
                                options=conversations)


    subset = pm_df[pm_df.Conversation == conversations[0]]
    authors = list(subset.Author.unique())

    # Create Checkbox Widget

    checkbox = CheckboxGroup(labels=authors, active=[])
    
    global old_conversation
    old_conversation = [conversations[0]]
    


    def generateR(subset):
        r_group = {}
        colors = turbo(len(subset.Author.unique()))
        authors = list(subset.Author.unique())
        

        for i, key in enumerate(authors):


            
            src = ColumnDataSource(subset[subset.Author == key])

            r_group[key] = top.line(name = key,x='Datetime',y=metric_radio.labels[metric_radio.active],
                                     source=src, visible = False, legend_label=key, line_width=2,
                                     color=colors[i])
            
            

        return r_group
    
    
    # initialize render_group dictionary
    r_dict ={conversation_select.value : generateR(subset)}
    top.legend.location = 'top_left'
    legend_group = {old_conversation[0] : top.legend.items}
    
    def displayMetric(attr, old, new):
        newval = metric_radio.labels[new]
        for group in r_dict:
            for key in r_dict[group]:
                r_dict[group][key].glyph.y = newval
                

    def displayConversation(attr, old, new):
        old_conversation[0] = old
        checkbox.active = []
        subset = pm_df[pm_df.Conversation == new]
        authors = list(subset.Author.unique())
        
        top.legend.items = []
        if new not in r_dict:
            r_dict[new] = generateR(subset)
            legend_group[new] = top.legend.items
        else:
            top.legend.items= legend_group[new]
            print()
        old_conversation[0] = new
        checkbox.labels = authors

    def displayAuthor(attr, old, new):
        for i, key in enumerate(checkbox.labels):
            r_dict[old_conversation[0]][key].visible = i in checkbox.active

    conversation_select.on_change('value', displayConversation)
    checkbox.on_change('active', displayAuthor)
    metric_radio.on_change('active', displayMetric)
    layout = column(metric_radio, 
                    row(column(conversation_select, checkbox), top))
    
    #Make a tab with the layout
    tab = Panel(child=layout, title = 'Intra-PM Analysis')
    
    return tab
    
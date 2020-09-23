'''
This tab will focus on conversations of more than 2 people. All data will be a comparison between all authors
in the conversation.

Ideas
#Should I combine both graphs and overlay the data?
#Should I use range tool?
#


Widget Locations:
Global Metric Option Radio: Top Center
Global Author Select Checkbox Group: Very Left
Fig 1 SMA Radio: above fig1

(top left) Figure 1, will come with moving average options {Hourly, Daily, Weekly, Monthly}
checbkox group to select which authors in the chat to show

(bottom left) Figure 2, will display raw data through tiny circles

(rightFigure 3, will display a chart sorting authors by various metrics

Analytic metrics:

All authors sent messages (by author)
All authors sent Words
All authors cumulative Words per Messages
Emoji usage
Possible analyze media sent
'''

from getData import df
from bokeh.io import show, output_notebook, output_file, curdoc
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, CDSView, GroupFilter, Legend, LegendItem, Panel
from bokeh.models.widgets import RadioButtonGroup, Select, CheckboxGroup
from bokeh.layouts import column, row
from bokeh.palettes import turbo
from bokeh.embed import server_document



def IntraConversation_tab(df):
    group_df = df.drop(df[df.Conversation.isin(list(df.Author.unique()))].index)
    metric_selection = ['Sent Messages', 'Sent Words','WPM']
    conversations = list(group_df.Conversation.unique())
    authors = []


    height = 300
    width = 1000
    #Create Figures

    top = figure(x_axis_type='datetime', frame_height = height, frame_width = width)
    bot = figure(x_axis_type='datetime')
    #leaderboard = []

    #Create Widgets

    metric_radio = RadioButtonGroup(labels= metric_selection,
                                   active=1)
    conversation_select = Select(title='Conversation',
                                value =conversations[0],
                                options=conversations)


    subset = group_df[group_df.Conversation == conversations[0]]
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

            r_group[key] = top.circle(name = key,x='Datetime',y=metric_radio.labels[metric_radio.active],
                                     source=src, visible = False, legend_label=key,
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
        subset = group_df[group_df.Conversation == new]
        authors = list(subset.Author.unique())

        top.legend.items = []
        if new not in r_dict:
            r_dict[new] = generateR(subset)
            legend_group[new] = top.legend.items
        else:
            top.legend.items= legend_group[new]
        old_conversation[0] = new
        print(top.min_border_left)
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
    tab = Panel(child=layout, title = 'Intra-Conversation Analysis')
    
    return tab



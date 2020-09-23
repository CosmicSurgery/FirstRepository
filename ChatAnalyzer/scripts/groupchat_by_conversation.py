from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, Legend, Panel
from bokeh.models.widgets import RadioButtonGroup, CheckboxGroup
from bokeh.layouts import column, row
from bokeh.palettes import turbo, Category20_20, Category10_10

def groupchat_by_conversation(df):
    df = df.drop(df[df.Conversation.isin(list(df.Author.unique()))].index)
    df = df[['Datetime', 'Author','Conversation', 'Total Messages', 'Total Words']]
    
    me = 'Miles Keating'
    reset_data={x:[] for x in df.columns.unique()}
    conversations = list(df.Conversation.unique())

    if len(conversations) > 20:
        colors = turbo(len(subset.Conversation.unique()))
    elif len(conversations) > 10:
        colors = Category20_20
    else:
        colors = Category10_10
    
    #Create Figures
    height = 300
    width = 1000
    
    top = figure(x_axis_type='datetime', frame_height=height, frame_width=width)
    legend = Legend(items=[])
    top.add_layout(legend, 'right')
    bot = figure(x_axis_type='datetime', frame_height=height, frame_width=width)

    def update_conversation(attr, old, new): #Updates conversation from checkbox group
        subset = df
        if len(old) > len(new): #signifies unchecking a box
            change = checkbox.labels[list(set(old) - set(new))[0]]
            new_data = reset_data
        else: #signifies checking a box
            index = list(set(new) - set(old))[0]
            change = checkbox.labels[list(set(new) - set(old))[0]]
            new_data = subset[subset.Conversation == change]
            renders[change].glyph.line_color=colors[index]
        items=[]
        for x in checkbox.active:
            x= checkbox.labels[x]
            items.append((x,[renders[x]]))
        top.legend.items=items

        src[change].data.update(new_data)
        

    def update_column(attr, old, new):
        newval = column_radio.labels[new]
        for r in renders:
            renders[r].glyph.y = newval
            
        #Create Widgets
    column_selection = ['Total Messages', 'Total Words']
    column_radio = RadioButtonGroup(labels= column_selection,
                                   active=0)

    

    subset = df

    # Create Checkbox Widget

    checkbox = CheckboxGroup(labels=conversations, active=[])
    
    legend_items =[]
    #Populate the src and tie each one to a render
    src = {} #Dictionary of CDS' where each author maps to a CDS
    renders = {} # Dictionary of renderers where each author maps to a renderer
    for conversation in conversations:
        src[conversation] = ColumnDataSource(reset_data)
        renders[conversation] = top.line(source=src[conversation],
                           x='Datetime', y = column_radio.labels[column_radio.active])
        legend_items.append([(conversation,[renders[conversation]])])
        
    
    top.legend.items = []

    checkbox.on_change('active', update_conversation)
    column_radio.on_change('active', update_column)
    
    layout = column(column_radio, row(checkbox, top))
    
    
    #Make a tab
    tab = Panel(child=layout, title = 'Groupchats by Conversation')
       
    return tab
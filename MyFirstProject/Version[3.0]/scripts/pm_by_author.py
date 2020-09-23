from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, Legend, Panel
from bokeh.models.widgets import RadioButtonGroup, Select, CheckboxGroup
from bokeh.layouts import column, row


def pm_by_author(df):
    
    me = 'Miles Keating'
    reset_data = {x:[] for x in df.columns.unique()}
    
    colors = ['navy','firebrick']
    
    #Create Figures
    height = 300
    width = 1000
    
    top = figure(x_axis_type='datetime', frame_height=height, frame_width=width)
    legend = Legend(items=[])
    top.add_layout(legend, 'right')
    bot = figure(x_axis_type='datetime', frame_height=height, frame_width=width)
    
    df = df.drop(df[~df.Conversation.isin(list(df.Author.unique()))].index)
    


    def update_author(attr, old, new):
        subset = df[df.Conversation == conversation_select.value]
        
        if len(old) > len(new): #signifies unchecking a box
            change = checkbox.labels[list(set(old) - set(new))[0]]
            new_data = reset_data
        else: #signifies checking a box
            index = list(set(new) - set(old))[0]
            change = checkbox.labels[list(set(new) - set(old))[0]]
            new_data = subset[subset.Author == change]
            renders[change].glyph.line_color=colors[index]

        top.legend.items=reset_legend([checkbox.labels[x] for x in checkbox.active])
        src[change].data.update(new_data)
        
    def update_conversation(attr, old, new):
        subset = df[df.Conversation == new]
        
        for author in all_authors:
            src[author].data.update(reset_data)
            if author in subset.Author.unique():
                src[author].data.update(subset[subset.Author == author])
            
        checkbox.active = [0,1]
        checkbox.labels = list(subset.Author.unique())
        top.legend.items=reset_legend([checkbox.labels[x] for x in checkbox.active])
        
    def reset_legend(authors):
        items = []
        for author in authors:
            items.append((author,[renders[author]]))
        return items
        

    def update_column(attr, old, new):
        newval = column_radio.labels[new]
        for r in renders:
            renders[r].glyph.y = newval

    all_authors = df.Author.unique()
    conversations = list(df.Conversation.unique())
    
    #Create Widgets
    column_selection = ['Sent Messages', 'Sent Words','WPM']
    column_radio = RadioButtonGroup(labels= column_selection,
                                   active=1)
    conversation_select = Select(title='Conversation',
                                value =conversations[0],
                                options=conversations)
    
    subset = df[df.Conversation == conversation_select.value]
    authors = list(subset.Author.unique())

    # Create Checkbox Widget

    checkbox = CheckboxGroup(labels=authors, active=[0,1])
    
    #Populate the src and tie each one to a render
    src = {} #Dictionary of CDS' where each author maps to a CDS
    renders = {} # Dictionary of renderers where each author maps to a renderer
    items = []
    for author in all_authors:
        src[author] = ColumnDataSource(reset_data)
        renders[author] = top.line(source=src[author],
                           x='Datetime', y = column_radio.labels[column_radio.active], line_color=colors[1])
        if author in authors:
            src[author].data.update(subset[subset.Author == author])
            if author == me:
                renders[me].glyph.line_color=colors[0]
            items.append((author,[renders[author]]))
    top.legend.items=items
    
    checkbox.on_change('active', update_author)
    conversation_select.on_change('value', update_conversation)
    column_radio.on_change('active', update_column)
    
    layout = column(column_radio,
                    row(column(conversation_select, checkbox), top))


    #Make a tab
    tab = Panel(child=layout, title = 'Private Messages ByAuthor')

    
    return tab
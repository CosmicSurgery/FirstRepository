from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, Legend, Panel
from bokeh.models.widgets import RadioButtonGroup, Select, CheckboxGroup
from bokeh.layouts import column, row
from bokeh.palettes import turbo, Category20_20, Category10_10

def groupchat_by_author(df):
    
    reset_data = {x:[] for x in df.columns.unique()}
    global colors
    colors = Category20_20
    
    #Create Figures
    height = 300
    width = 1000
    
    top = figure(x_axis_type='datetime', frame_height=height, frame_width=width)
    legend = Legend(items=[])
    top.add_layout(legend, 'right')
    bot = figure(x_axis_type='datetime', frame_height=height, frame_width=width)
    
    group_df = df.drop(df[df.Conversation.isin(list(df.Author.unique()))].index)

    all_authors = group_df.Author.unique()
    conversations = list(group_df.Conversation.unique())
    global old_conversation
    old_conversation = [conversations[0]]
    
    legend_items =[]



    def update_author(attr, old, new):
        subset = group_df[group_df.Conversation == conversation_select.value]
        
        if len(old) > len(new): #signifies unchecking a box
            change = checkbox.labels[list(set(old) - set(new))[0]]
            new_data = reset_data
        else: #signifies checking a box
            index = list(set(new) - set(old))[0]
            change = checkbox.labels[list(set(new) - set(old))[0]]
            new_data = subset[subset.Author == change]
            renders[change].glyph.line_color=colors[index]
        items=[]
        for x in checkbox.active:
            x= checkbox.labels[x]
            items.append((x,[renders[x]]))
        top.legend.items=items

        src[change].data.update(new_data)
        
    def update_conversation(attr, old, new):
        subset = group_df[group_df.Conversation == new]
        
        for author in all_authors:
            src[author].data.update(reset_data)

            
        checkbox.active = []
        checkbox.labels = list(subset.Author.unique())
        
        global colors
        if len(subset.Author.unique()) > 20:
            colors = turbo(len(subset.Author.unique()))
        elif len(subset.Author.unique()) > 10:
            colors = Category20_20
        else:
            colors = Category10_10

        
        
        
    def update_column(attr, old, new):
        newval = column_radio.labels[new]
        for r in renders:
            renders[r].glyph.y = newval
            
    #Create Widgets
    column_selection = ['Sent Messages', 'Sent Words','WPM']
    column_radio = RadioButtonGroup(labels= column_selection,
                                   active=1)
    conversation_select = Select(title='Conversation',
                                value =conversations[0],
                                options=conversations)
    

    subset = group_df[group_df.Conversation == conversation_select.value]
    authors = list(subset.Author.unique())

    # Create Checkbox Widget

    checkbox = CheckboxGroup(labels=authors, active=[])
    
    #Populate the src and tie each one to a render
    src = {} #Dictionary of CDS' where each author maps to a CDS
    renders = {} # Dictionary of renderers where each author maps to a renderer
    for author in all_authors:
        src[author] = ColumnDataSource(reset_data)
        renders[author] = top.line(source=src[author],
                           x='Datetime', y = column_radio.labels[column_radio.active])
        legend_items.append([(author,[renders[author]])])
        
    
    top.legend.items = []

    checkbox.on_change('active', update_author)
    conversation_select.on_change('value', update_conversation)
    column_radio.on_change('active', update_column)
    
    layout = column(column_radio,
                    row(column(conversation_select, checkbox), top))
    
    #Make a tab
    tab = Panel(child=layout, title = 'Groupchats ByAuthor')

    
    return tab
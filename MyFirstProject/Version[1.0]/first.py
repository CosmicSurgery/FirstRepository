import pandas as pd
import numpy as np

from bokeh.io import show, output_notebook, push_notebook
from bokeh.plotting import figure

from bokeh.models import CategoricalColorMapper, HoverTool, ColumnDataSource, Panel
from bokeh.models.widgets import CheckboxGroup, Slider, RangeSlider, Tabs

from bokeh.layouts import column, row, WidgetBox
from bokeh.palettes import Category20_16

from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application

def modify_doc(doc):
    
    def make_dataset(author_list):



        by_author = pd.DataFrame(columns=df.columns.tolist())



        for i, author in enumerate(author_list):



            # Subset to the author

            subset = df[df.Author == author].copy()


            # Color each author differently

            subset['color'] = Category20_16[i]

            # Add to the overall dataframe


            by_author = by_author.append(subset)

        # Convert dataframe to column data source


        return ColumnDataSource(by_author)

    def make_plot(src):
        # Blank plot with correct labels

        p = figure(plot_width = 700, plot_height = 700,
                  title = 'Messages with Bird Up', x_axis_label = 'index', y_axis_label = 'Datetime')

        p.circle(source=src,x='Datetime',y='counts', color='color', line_width=2, legend_field ='Author')

        # Hover tool with vline mode
        '''hover = HoverTool(tooltips=[('Author', '@Author'),
                                   ('Messages', '@counts')],
                                   mode='vline')'''
        # TOO MUCH DATA IS CRASHING HOVER

        #p.add_tools(hover)

        # Styling
        #p = style(p)

        return p


    def update(attr, old, new):

        # Get the list of authors for the graph

        author_to_plot = [author_selection.labels[i] for i in

                         author_selection.active]



        # Make a new dataset based on the selected carriers and the 

        # make_dataset function defind earlier

        new_src = make_dataset(author_to_plot)



        # Convert dataframe to column data source




        # Update the source used the

        src.data.update(new_src.data)

    available_authors = ['Bird Up', 'Miles Keating']
    author_selection = CheckboxGroup(labels=available_authors, active = [0, 1])
    author_selection.on_change('active', update)

    controls = WidgetBox(author_selection)
    
    initial_authors = [author_selection.labels[i] for i in author_selection.active]

    src = make_dataset(initial_authors)

    p = make_plot(src)
    
    controls = WidgetBox(author_selection)

    layout = row(controls, p)
    
    doc.add_root(layout)
    
# Set up an application
handler = FunctionHandler(modify_doc)
app = Application(handler)

if __name__ == '__main__':
    app.run(port=8080)
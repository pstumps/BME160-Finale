from math import pi
import pandas as pd
import numpy as np
from bokeh.plotting import figure, output_notebook, output_file, show
from bokeh.models.sources import ColumnDataSource
from bokeh.models import HoverTool
import collections


class DendroHeat:
    
    def __init__ (self):
        self.heatsource = ''
        self.heatmap = ''
        self.dendrogram = ''
    
    def addHeatmapData(self, file='', index_col=0):
        if not file: return
        if file.endswith(".xlsx"): self.heatdata = pd.read_excel(file, index_col=index_col)
        elif file.endswith(".csv"): self.heatdata = pd.read_csv(file, index_col=index_col)
        
        self.normheatdata = (self.heatdata - self.heatdata.min(axis=0)) / (self.heatdata.max(axis=0) - self.heatdata.min(axis=0))

        molecule = []
        attribute = []
        xs = []
        ys = []
        alpha = []
        value = []

        for i, m in enumerate(self.heatdata.index):
            molecule = molecule + [m]*len(self.heatdata.columns)
            attribute = attribute + self.heatdata.columns.tolist()
            xs = xs + list(np.arange(0.5, len(self.heatdata.columns)+0.5))
            ys = ys + [i+0.5]*len(self.heatdata.columns)
            value = value + self.heatdata.loc[m].tolist()
            alpha = alpha + self.normheatdata.loc[m].tolist()

        data = dict(
                molecule = molecule,
                attribute = attribute, 
                xs = xs,
                ys = ys,
                value = value,
                alpha = alpha
                    )

        self.heatsource = ColumnDataSource(data)
    
    def addDendrogramData(self, file='', index_col=0, parent_col='parent', child_col='child'):
        if not file: return
        if file.endswith(".xlsx"): df = pd.read_excel(file, index_col=0)
        elif file.endswith(".csv"): df = pd.read_csv(file, index_col=0)
        
        parents = df[parent_col].tolist()
        children = df[child_col].tolist()
        self.forwardtree = collections.defaultdict(list)
        self.reversetree = {}
        for x,y in zip(parents,children):
            self.reversetree[y] = x
            self.forwardtree[x].append(y)
        
    def createHeatmap (self, addHoverTool=True):
        if not self.heatsource:
            return
        
        hm = figure(x_range=self.heatdata.columns.tolist(), y_range=[0, self.heatdata.shape[0]])
        hm.rect(x='xs', y='ys', height=1, width=1, source=self.heatsource, fill_alpha='alpha', line_alpha=0.1)
        
        if addHoverTool:
            hover = HoverTool()
            hover.tooltips = [("Molecule", "@molecule"), ("Attribute", "@attribute"), ("Value", "@value")]
            hm.add_tools(hover)

        hm.xaxis.major_label_orientation = pi/2
        hm.xaxis.major_label_text_font_size = '7pt'
        hm.axis.major_tick_line_color = None
        hm.axis.minor_tick_line_color = None
        hm.yaxis.major_label_text_color = None
        hm.grid.grid_line_color = None
        hm.axis.axis_line_color = None

        self.heatmap = hm
    
    def createDendrogram (self, addHoverTool=True):
        pass
    
    def show (self, output='notebook', heatmap=True, dendrogram=False):
        if heatmap and not self.heatmap or dendrogram and not self.dendrogram:
            #error, figure(s) have not been created
            return

        if output == 'notebook':
            output_notebook()
        elif output == 'html':
            if heatmap and dendrogram:
                output_file("dendroheat.html", "Heatmap with Dendrogram")
            elif heatmap:
                output_file("heatmap.html", "Heatmap")
            elif dendrogram:
                output_file("dendrogram.html", "Dendrogram")
        
        if heatmap:
            show(self.heatmap)
        elif dendrogram:
            show(self.dendrogram)
        elif heatmpa and dendrogram:
            #combine and show
            pass
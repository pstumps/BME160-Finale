from math import pi
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import pairwise_distances
from scipy.cluster.hierarchy import linkage, dendrogram, leaves_list
from bokeh.plotting import figure, output_notebook, output_file, show
from bokeh.models.sources import ColumnDataSource
from bokeh.models import HoverTool
import collections
import sys


class DendroHeat:
    
    def __init__ (self, hmData, dendroData):
        self.hmData = hmData
        self.dendroData = dendroData
        self.heatsource = ''
        self.heatmap = ''
        self.dendrogram = ''
    
    def addHeatmapData(self, file, index_col=0):
        if not file: return
        if file.endswith(".xlsx"): self.heatdata = pd.read_excel(file, index_col=index_col)
        elif file.endswith(".csv"): self.heatdata = pd.read_csv(file, index_col=index_col)
        
        self.normheatdata = (self.heatdata - self.heatdata.min(axis=0)) / (self.heatdata.max(axis=0) - self.heatdata.min(axis=0))

        name = []
        attribute = []
        xs = []
        ys = []
        alpha = []
        value = []

        for i, m in enumerate(self.heatdata.index):
            name = name + [m]*len(self.heatdata.columns)
            attribute = attribute + self.heatdata.columns.tolist()
            xs = xs + list(np.arange(0.5, len(self.heatdata.columns)+0.5))
            ys = ys + [i+0.5]*len(self.heatdata.columns)
            value = value + self.heatdata.loc[m].tolist()
            alpha = alpha + self.normheatdata.loc[m].tolist()

        data = dict(
                name = name,
                attribute = attribute, 
                xs = xs,
                ys = ys,
                value = value,
                alpha = alpha
                    )

        self.heatsource = ColumnDataSource(data)
    
    def addDendrogramData(self, file, index_col=0, parent_col='parent', child_col='child'):
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

    def clustering(self, file):
        if not file: return
        if file.endswith(".xlsx"): cdf = pd.read_excel(file, index_col=0)
        elif file.endswith(".csv"): cdf = pd.read_csv(file, index_col=0)

        X = pairwise_distances(cdf, metric= 'euclidean')
        Z = linkage(X, method='complete')
        dendo = dendrogram(Z, no_plot=True)
        icoord, dcoord = dendo['icoord'], dendo['dcoord']
        labels = list(map(int, dendo['ivl']))
        self.dendroData = cdf.iloc[labels]

        return icoord, dcoord
        
    def _createHeatmap (self, addHMHoverTool=True, addDendroHoverTool=False):
        if not self.heatsource:
            return
        
        hm = figure(x_range=self.heatdata.columns.tolist(), y_range=[0, self.heatdata.shape[0]])
        hm.rect(x='xs', y='ys', height=1, width=1, source=self.heatsource, fill_alpha='alpha', line_alpha=0.1)
        
        icoord, dcoord = clustering(self.dendroData)
        icoord = pd.DataFrame(icoord)
        icoord = icoord*(data['ys'].max()/icoord.max().max())  
        dcoord = pd.DataFrame(dcoord)
        dcoord = dcoord*(data['xs'].max()/dcoord.max().max())

        for i, d in zip(icoord, dcoord):
            d = list(map(lambda x: -x, d))
            hm.line(x=d, y=i, line_color = 'black', name='denhover')

        if addHMHoverTool:
            hover = HoverTool()
            hover.tooltips = [("Name", "@name"), ("Attribute", "@attribute"), ("Value", "@value")]
            hm.add_tools(hover)

        if addDendroHoverTool:
            parent = []
            children = []
            denvalue = []
            #This will be for the dendrogram hover tool when I can figure out how the hell it works
            ldf = pd.DataFrame()

            for i, n in enumerate(ldf.index):
                parent = parent + [n]*len(ldf.columns)
                children = children + ldf.columns.tolist()
                denvalue = denvalue + ldf.loc[n].tolist()

            denData = pd.DataFrame(dict(
                parent = parent,
                children = children,
                denvalue = denvalue
            ))

            denhover = HoverTool(names=['denhover'])
            denhover.tooltips = [("Parent", "@parent"), ("Children", "@children"), ("Value", "@denvalue")]
            hm.add_tools(denhover)
            #hm.line(x=d, y=i, line_color = 'black', name='denhover') #we'll need this somewhere if we get the dendrogram up and running in order to add a hovertool for the dendrogram
        

        hm.xaxis.major_label_orientation = pi/2
        hm.xaxis.major_label_text_font_size = '7pt'
        hm.axis.major_tick_line_color = None
        hm.axis.minor_tick_line_color = None
        hm.yaxis.major_label_text_color = None
        hm.grid.grid_line_color = None
        hm.axis.axis_line_color = None

        return hm
    
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
        elif heatmap and dendrogram:
            #combine and show
            pass

def main():
    dh = DendroHeat()
    dh.addHeatmapData(sys.argv[1], sys.argv[2])
    dh._createHeatmap()
    dh.show(output='html')
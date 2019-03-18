from math import pi
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import pairwise_distances
from scipy.cluster.hierarchy import linkage, dendrogram, leaves_list
from bokeh.plotting import figure, output_notebook, output_file, show
from bokeh.models.sources import ColumnDataSource
from bokeh.models import HoverTool
import collections
import argparse
import sys


class DendroHeat:
    
    def __init__ (self, hmData, dendroData, cluster, hmHover, height=None, width=None):
        self.clustering = cluster
        self.HMHover = hmHover
        self.hmdf, self.kindle, self.heatsource = self.addHeatmapData(hmData)
        self.addDendrogramData(dendroData)
        self.fireHeight = height
        self.fireWidth = width
        self.icoords = None
        self.dcoords = None
        self.heatmap = None
        self.dendrogram = None
    
    def addHeatmapData(self, file, index_col=0):
        if not file: return
        if file.endswith(".xlsx"): heatdata = pd.read_excel(file, index_col=index_col)
        elif file.endswith(".csv"): heatdata = pd.read_csv(file, index_col=index_col)
        
        normheatdata = (heatdata - heatdata.min(axis=0)) / (heatdata.max(axis=0) - heatdata.min(axis=0))

        name = []
        attribute = []
        xs = []
        ys = []
        alpha = []
        value = []

        for i, m in enumerate(heatdata.index):
            name = name + [m]*len(heatdata.columns)
            attribute = attribute + heatdata.columns.tolist()
            xs = xs + list(np.arange(0.5, len(heatdata.columns)+0.5))
            ys = ys + [i+0.5]*len(heatdata.columns)
            value = value + heatdata.loc[m].tolist()
            alpha = alpha + normheatdata.loc[m].tolist()

        data = pd.DataFrame(dict(
                name = name,
                attribute = attribute, 
                xs = xs,
                ys = ys,
                value = value,
                alpha = alpha
                    ))
        
        return heatdata, data, ColumnDataSource(data)
    
    def addDendrogramData(self, file, index_col=0, parent_col='parent', child_col='child'):
        if not file: return
        if file.endswith(".xlsx"): df = pd.read_excel(file, index_col=0)
        elif file.endswith(".csv"): df = pd.read_csv(file, index_col=0)

        if not self.clustering:

            parents = df[parent_col].tolist()
            children = df[child_col].tolist()
            self.forwardtree = collections.defaultdict(list)
            self.reversetree = {}
            for x,y in zip(parents,children):
                self.reversetree[y] = x
                self.forwardtree[x].append(y)

        elif self.clustering:
            print('Clustering kindle...')
            X = pairwise_distances(df, metric= 'euclidean')
            Z = linkage(X, method='complete')
            dendro = dendrogram(Z, no_plot=True)
            self.icoord, self.dcoord = dendro['icoord'], dendro['dcoord']
            labels = list(map(int, dendro['ivl']))
            self.dendroData = df.iloc[labels]
        
    def _createHeatmap (self, addDendroHoverTool=False):
        #if not self.heatsource:
        #    print("Heatsource not hot enough! Exiting. (Heatmap data not accepted)")
        #    return
        if not self.fireHeight or self.fireWidth:
            hm = figure(x_range=self.hmdf.columns.tolist(), y_range=[0, self.hmdf.shape[0]])
        elif not self.fireWidth:
            hm = figure(x_range=self.hmdf.columns.tolist(), y_range=[0, self.hmdf.shape[0]], height = int(self.fireHeight))
        elif not self.fireHeight:
            hm = figure(x_range=self.hmdf.columns.tolist(), y_range=[0, self.hmdf.shape[0]], width = int(self.fireWidth))
        elif self.fireHeight and self.fireWidth:
            hm = figure(x_range=self.hmdf.columns.tolist(), y_range=[0, self.hmdf.shape[0]], width= int(self.fireWidth), height = int(self.fireHeight))
        
        self.icoord = pd.DataFrame(self.icoord)
        self.dcoord = pd.DataFrame(self.dcoord)
        self.icoord = self.icoord*(self.kindle['ys'].max()/self.icoord.max().max())  
        self.dcoord = self.dcoord*(self.kindle['xs'].max()/self.dcoord.max().max())
        ycoord = self.icoord.values
        xcoord = self.dcoord.values

        for i, d in zip(ycoord, xcoord):
            d = list(map(lambda x: -x, d))
            hm.line(x=d, y=i, line_color = 'black', name='denhover')

        if self.HMHover:
            hover = HoverTool(names=['heat'])
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
        
        hm.rect(x='xs', y='ys', height=1, width=1, source=self.heatsource, fill_alpha='alpha', line_alpha=0.1, name='heat')

        hm.xaxis.major_label_orientation = pi/2
        hm.xaxis.major_label_text_font_size = '7pt'
        hm.axis.major_tick_line_color = None
        hm.axis.minor_tick_line_color = None
        hm.yaxis.major_label_text_color = None
        hm.grid.grid_line_color = None
        hm.axis.axis_line_color = None
        print('Lighting heatsource...')
        self.heatmap = hm
    
    def visualize (self, output='html', heatmap=True, dendrogram=False):
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
        print('BONFIRE LIT')

class CommandLine(): 
    '''
    Handle the command line, usage and help requests.
    CommandLine uses argparse, now standard in 2.7 and beyond.
    it implements a standard command line argument parser with various
    argument options, a standard usage and help.
    attributes:
    all arguments received from the commandline using .add_argument will be
    avalable within the .args attribute of object instantiated from CommandLine.
    For example, if myCommandLine is an object of the class, and requiredbool was
    set as an option using add_argument, then myCommandLine.args.requiredbool will
    name that option.
    '''
    def __init__(self, inOpts) : 
        '''
        Implement a parser to interpret the command line argv string using argparse.
        '''

        self.parser = argparse.ArgumentParser(description = 'Produces a heatmap as well as a dendrogram. This program will accept heatmap and distance matrix data in the form of an excel or csv file and visualize both using Bokeh.',
                                            epilog = 'Note: The current version of this program does NOT accept clustering data from other sources for dendrogram construction.',
                                            add_help = True, #default prefix_chars = '-',
                                            usage = '%(prog)s heatmapFile clusterFile -cluster [boolean; default=True] -HMtt [boolean] -hmht [int] -hmwd [int]')
        self.parser.add_argument('hmFile', action = 'store', help='Heatmap data file')
        self.parser.add_argument('clusterFile', action = 'store', default=None, help='Provide own clustering data or distance matrix for dendrogram creation.')
        self.parser.add_argument('-cluster', action = 'store', default=True, help='Use True if you want this program to cluster your data or false if you would like to provide your own.')
        self.parser.add_argument('-HMtt', action = 'store', default=True, help='Specify if you would like a hoverTool tooltip display for your heatmap.')
        self.parser.add_argument('-hmht', action = 'store', nargs='?', help='Specify designated height you would like for Heatmap figure if desired. (If you generated a heatmap before and did not like the height, you can edit that here. Note: This will interfere with the axis when panning.)')
        self.parser.add_argument('-hmwd', action = 'store', nargs='?', help='Specify designated width you would like for the heatmap figure if desired. (If you generated a heatmap before and did not like the width, you can edit that here. Note: This will interfere with the axis when panning.)')

        self.args = self.parser.parse_args(inOpts)
        
def main(inCL = None): 
    argsParse = CommandLine(inCL)
    hmFile = argsParse.args.hmFile
    cFile = argsParse.args.clusterFile
    cluster = argsParse.args.cluster
    HMhoverTool = argsParse.args.HMtt
    hmfigureHeight = argsParse.args.hmht
    hmfigureWidth = argsParse.args.hmwd

    dh = DendroHeat(hmFile, cFile, cluster, HMhoverTool, hmfigureHeight, hmfigureWidth)
    dh._createHeatmap()
    dh.visualize()
    

if __name__ == "__main__": main()
from math import pi
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import pairwise_distances
from scipy.cluster.hierarchy import linkage, dendrogram, leaves_list
from bokeh.plotting import figure, output_notebook, output_file, show
from bokeh.models.sources import ColumnDataSource
from bokeh.models import HoverTool
import argparse
import sys


class DendroHeat:
    '''
    Creates a Bokeh figure of a dendrogram and a heatmap. User only needs to worry about adding data and which figure(s) they want to show


    instantiation:
        fig = Dendroheat()
    usage:
        fig.addData(file='rawdata.csv', type='raw')
        fig.show(output=html, heatmap=True, dendrogram=True)
    '''
    
    def __init__ (self):
        '''Create the class with essential componenets'''
        self.heatmap = ''
        self.cluster = ''
        self.icoord = ''
        self.dcoord = ''
    
    def addData(self, file='', index_col=0, type=''):
        '''Checks if the file exists and what type of data is being added.'''
        if not file:
            raise FileNotFoundError('file does not exist')
        if file.endswith(".xlsx"): df = pd.read_excel(file, index_col=index_col)
        elif file.endswith(".csv"): df = pd.read_csv(file, index_col=index_col)
        
        if not type:
            raise AssertionError("Please designate dataype - raw or cluster")
        
        if type == "raw":
            ndf = (df - df.min(axis=0)) / (df.max(axis=0) - df.min(axis=0))

            name = []
            attribute = []
            crange = ['#66ff66', '#00ffff', '#000099', '#6600ff', '#ff00ff', '#990099', '#ff0066', '#993333', '#ff9933', '#ffff00']
            colors = []
            xs = []
            ys = []
            alpha = []
            value = []

            for i, m in enumerate(df.index):
                name = name + [m]*len(df.columns)
                attribute = attribute + df.columns.tolist()
                colors = colors + crange*2
                xs = xs + list(np.arange(0.5, len(df.columns)+0.5))
                ys = ys + [i+0.5]*len(df.columns)
                value = value + df.loc[m].tolist()
                alpha = alpha + ndf.loc[m].tolist()

            self.data = dict(name = name, attribute = attribute, colors = colors, xs = xs, ys = ys, value = value, alpha = alpha)
            self.source = ColumnDataSource(self.data)
            self.heatmap = df

        if type == "cluster":
            self.cluster = df
            X = pairwise_distances(self.cluster, metric= 'euclidean')
            Z = linkage(X, method='complete')
            dendro = dendrogram(Z, no_plot=True)
            self.icoord, self.dcoord = dendro['icoord'], dendro['dcoord']
            self.heatmap = self.heatmap.loc[dendro['ivl']]
    
    def _cluster(self, parent_col='parent', child_col='child'):
        '''No cluster data was given, so cluster the data.'''
        X = pairwise_distances(self.heatmap.fillna(0), metric= 'euclidean')
        Z = linkage(X, method='complete')
        dendro = dendrogram(Z, no_plot=True)
        self.icoord, self.dcoord = dendro['icoord'], dendro['dcoord']
        labels = list(map(int, dendro['ivl']))
        self.dendroData = self.heatmap.iloc[labels]
        
    def _createHeatmap (self, tool=True):
        '''Create the Heatmap'''
        # if no clustering data was given, cluster the data.
        # if not self.cluster:
        #     self._cluster()

        hm = figure(x_range=self.heatmap.columns.tolist(), y_range=[0, self.heatmap.shape[0]])

        if tool:
            hover = HoverTool(names=['Heatmap'])
            hover.tooltips = [("Name", "@name"), ("Attribute", "@attribute"), ("Value", "@value")]
            hm.add_tools(hover)
        
        hm.rect(x='xs', y='ys', height=1, width=1, source=self.source, fill_alpha='alpha', line_alpha=0.1, name='Heatmap', fill_color='colors')

        hm.xaxis.major_label_orientation = pi/2
        hm.xaxis.major_label_text_font_size = '7pt'
        hm.axis.major_tick_line_color = None
        hm.axis.minor_tick_line_color = None
        hm.yaxis.major_label_text_color = None
        hm.grid.grid_line_color = None
        hm.axis.axis_line_color = None
        self.heatmap = hm
    
    def _createDendrogram(self):
        self.icoord = pd.DataFrame(self.icoord)
        self.dcoord = pd.DataFrame(self.dcoord)
        self.icoord = self.icoord*(self.data['ys'].max()/self.icoord.max().max())  
        self.dcoord = self.dcoord*(self.data['xs'].max()/self.dcoord.max().max())
        ycoord = self.icoord.values
        xcoord = self.dcoord.values

        for i, d in zip(ycoord, xcoord):
            d = list(map(lambda x: -x, d))
            self.heatmap.line(x=d, y=i, line_color = 'black', name='denhover')

        # if addDendroHoverTool:
        #     parent = []
        #     children = []
        #     denvalue = []
        #     #This will be for the dendrogram hover tool when I can figure out how the hell it works
        #     ldf = pd.DataFrame()

        #     for i, n in enumerate(ldf.index):
        #         parent = parent + [n]*len(ldf.columns)
        #         children = children + ldf.columns.tolist()
        #         denvalue = denvalue + ldf.loc[n].tolist()

        #     denData = pd.DataFrame(dict(
        #         parent = parent,
        #         children = children,
        #         denvalue = denvalue
        #     ))

        #     denhover = HoverTool(names=['denhover'])
        #     denhover.tooltips = [("Parent", "@parent"), ("Children", "@children"), ("Value", "@denvalue")]
        #     hm.add_tools(denhover)
            #hm.line(x=d, y=i, line_color = 'black', name='denhover') #we'll need this somewhere if we get the dendrogram up and running in order to add a hovertool for the dendrogram

    def show(self, output='html', heatmap=True, dendrogram=True):
        '''Outputs the Heatmap and Dendrogram'''

        # create figures based on user input
        if heatmap:
            self._createHeatmap()
        if dendrogram:
            self._createDendrogram()

        # configure output file
        if output == 'notebook':
            output_notebook()
        elif output == 'html':
            if heatmap and dendrogram:
                output_file("dendroheat.html", "Heatmap with Dendrogram")
            elif heatmap:
                output_file("heatmap.html", "Heatmap")
        
        show(self.heatmap)

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

        self.parser = argparse.ArgumentParser(description = 'Produces a heatmap with or without a dendrogram. This program will accept raw data and pre-clustered data in the form of an excel or csv file and visualize both using Bokeh.',
                                            epilog = 'Note: Program cannot run with only clustered data',
                                            add_help = True, #default prefix_chars = '-',
                                            usage = '%(prog)s heatmapFile clusterFile')
        self.parser.add_argument('raw', action = 'store', help='Heatmap data file')
        self.parser.add_argument('cluster', action = 'store', nargs='?', default='', help='Provide own clustering data or distance matrix for dendrogram creation.')
        self.parser.add_argument('-v, --version', action='version', version='%(prog)s 0.2')
        # self.parser.add_argument('--HMtt', action = 'store', default=True, help='Specify if you would like a hoverTool tooltip display for your heatmap.')
        # self.parser.add_argument('-hmht', action = 'store', default=False, nargs='?', help='Specify designated height you would like for Heatmap figure if desired. (If you generated a heatmap before and did not like the height, you can edit that here. Note: This will interfere with the axis when panning.)')
        # self.parser.add_argument('-hmwd', action = 'store', default=False, nargs='?', help='Specify designated width you would like for the heatmap figure if desired. (If you generated a heatmap before and did not like the width, you can edit that here. Note: This will interfere with the axis when panning.)')

        self.args = self.parser.parse_args(inOpts)
        
def main(inCL = None): 
    argsParse = CommandLine(inCL)
    raw = argsParse.args.raw
    cluster = argsParse.args.cluster

    dh = DendroHeat()
    dh.addData(file=raw, type='raw')
    if cluster: dh.addData(file=cluster, type='cluster')
    dh.show()
    

if __name__ == "__main__": main()
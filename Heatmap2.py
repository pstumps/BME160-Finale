#get packages we will use
from math import pi
import pandas as pd
import numpy as np
from scipy.cluster.hierarchy import linkage, dendrogram, leaves_list
from sklearn.metrics.pairwise import pairwise_distances
#import matplotlib
from bokeh.plotting import figure, output_notebook, show
from bokeh.models.sources import ColumnDataSource
from bokeh.models import HoverTool
import hdbscan
#import data and make a normalized copy of it
df = pd.read_excel('HexaPropsAssay.xlsx', index_col=0)
cdf = pd.read_csv('HexaLow_matrix.csv', index_col=0)
ndf = (df - df.min(axis=0)) / (df.max(axis=0) - df.min(axis=0))
cdf_std = (cdf - cdf.min(axis=0))/(cdf.max(axis=0)-cdf.min(axis=0))
cdf_scaled = cdf_std*(1.0 - 0.0) + 0.0
cdf_tree = cdf.to_records(index = False)
#print(repr(cdf_tree))

X = pairwise_distances(cdf_scaled, metric= 'euclidean')
Z = linkage(X, method='complete')
print(len(leaves_list(Z)))
dendo = dendrogram(Z)

ldf = pd.DataFrame(Z)

icoord, dcoord = dendo['icoord'], dendo['dcoord']
labels = list(map(int, dendo['ivl']))
cdf = cdf.iloc[labels]
cdf_scaled = cdf_scaled.iloc[labels]

#reshape the data to be easily understood by bokeh
molecule = []
attribute = []
xs = []
ys = []
colors = []
alpha = []
value = []

for i, m in enumerate(df.index):
    molecule = molecule + [m]*len(df.columns)
    attribute = attribute + df.columns.tolist()
    xs = xs + list(np.arange(0.5, len(df.columns)+0.5))
    ys = ys + [i+0.5]*len(df.columns)
    value = value + df.loc[m].tolist()
    alpha = alpha + ndf.loc[m].tolist()

data = pd.DataFrame(dict(
        molecule = molecule,
        attribute = attribute, 
        xs = xs,
        ys = ys,
        value = value,
        alpha = alpha
              ))

parent = []
children = []
denvalue = []

for i, n in enumerate(ldf.index):
    parent = parent + [n]*len(ldf.columns)
    children = children + ldf.columns.tolist()
    denvalue = denvalue + ldf.loc[n].tolist()

denData = pd.DataFrame(dict(
    parent = parent,
    children = children,
    denvalue = denvalue
    ))
#print(denData)
source = ColumnDataSource(data)
#create tooltip and heatmap
hmhover = HoverTool(names=['molecule'])

hmhover.tooltips = [("Molecule", "@molecule"), ("Attribute", "@attribute"), ("Value", "@value")]

denhover = HoverTool(names=['denhover'])

denhover.tooltips = [("Parent", "@parent"), ("Children", "@children"), ("Value", "@denvalue")]

icoord = pd.DataFrame(icoord)
icoord = icoord*(data['ys'].max()/icoord.max().max())
icoord = icoord.values

dcoord = pd.DataFrame(dcoord)
dcoord = dcoord*(data['xs'].max()/dcoord.max().max())
dcoord = dcoord.values

hm = figure(x_range=df.columns.tolist(), y_range=[0, df.shape[0]], height = 3000)
hm.rect(x='xs', y='ys', height=1, width=1, source=source, fill_alpha='alpha', line_alpha=0.1, name='molecule')

for i, d in zip(icoord, dcoord):
    d = list(map(lambda x: -x, d))
    hm.line(x=d, y=i, line_color = 'black', name='denhover')


hm.xaxis.major_label_orientation = pi/2
hm.xaxis.major_label_text_font_size = '7pt'
hm.axis.major_tick_line_color = None
hm.axis.minor_tick_line_color = None
hm.yaxis.major_label_text_color = None
hm.grid.grid_line_color = None
hm.axis.axis_line_color = None

hm.add_tools(hmhover)
hm.add_tools(denhover)
show(hm)
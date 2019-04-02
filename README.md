# DendroHeatmap

Created by Patrick Stumps and Malav Dipankar

DendroHeat.py creates a visualization of an interactive heatmap and dendrogram using libraries from both Bokeh and MatPlotLib.
This program will cluster a user provided distance matrix using matplotlib to create a dendrogram in parallel with a heatmap using Bokeh. Creation of the heatmap allows efficient visualization of any trends that may be correlated with the users clustering data and has a wide array of applications including determining gene expression to releative membrance permeability of cyclic peptides. 

If you would like to see a demonstration of this program, see the "Demonstration" folder and run the bash script. If you would like to use this program for your own data, usage of this program is as follows:

Input: python DendroHeat.py [heatmap data].xlsx [distancematrix].xlsx

Output: HTML file of Heatmap with dendrogram.

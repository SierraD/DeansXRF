# DeansXRF
# Copyright (C) 2024  Sierra Dean

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import pandas
import plotly
import numpy
import plotly.express
numpy.seterr(divide = 'ignore') 

class DeansXRF(object):
    """
    This file is part of the DeansXRF software.
    
    File author(s): Sierra Dean <ccnd@live.com>
    
    Distributed under the GPLv3 Licence.
    See accompanying file LICENSE.txt or copy at
        http://www.gnu.org/licenses/gpl-3.0.html
        
    source: https://github.com/SierraD/MAXWELL
    
    Last Updated: July 25 2024
    """
    
    def __init__(self, path):
        """
        A technique to prepare and analyze a two-dimensional X-ray Fluorescence Scan 
        to determine the distribution of the emission of a specified energy range using
        both spectrum and raster analysis.
        
        This method requires both a CSV type StageTable file, as well as MCA type
        scan files containing the PMCA spectrum from Amptek silicon drift detectors (SDD). 
        The files from three different SDDs are summed to ensure coverage over a large
        capture angle. 
        
        The spectrum files are then visualized, and a user specified energy designating 
        an X-ray emission line is used to determine a range of summation around the 
        desired emission energy. Once the energy and summation range is confirmed, 
        a raster-style colormap is created from the collected emission from the energy
        at the X-ray emission line. 
        
        Attributes:
            path:
                The operating system path to the folder containing the scan files.
                This must be formatted with an r before the path. 
                Example: r"C:\\Users\\User\\Desktop\\Folder"
                        (Please change \\ to \ for the actual path)
        
        Return:
            None.
        """
        self.path = path
        return
    
    def Initiate(self):
        """
        A technique to open the stage file and scan files to prepare for analysis.
        
        Attributes:
            None.
        Return:
            None. Will modify the data in place. 
        """
        self.stage = pandas.read_csv(self.path+"\\StageTable.csv", 
                                header=None, 
                                usecols=[0,1,2],
                                names=['Step', 'Z [Pulse]', "X [Pulse]"])
        self.z_steps = self.stage["X [Pulse]"].value_counts()[self.stage["X [Pulse]"][0]]
        self.x_steps = int(max(self.stage["Step"])/self.z_steps)
        for i in range(1, max(self.stage["Step"])+1): 
            a = pandas.read_csv(self.path+"\\"+str(i)+"-1.mca", header=None, usecols=[0], names=["Counts 1"])
            b = pandas.read_csv(self.path+"\\"+str(i)+"-2.mca", header=None, usecols=[0], names=["Counts 2"])
            c = pandas.read_csv(self.path+"\\"+str(i)+"-3.mca", header=None, usecols=[0], names=["Counts 3"])
            starting_info = 0
            starting_info_end = 11
            ending_info = 2060
            ending_info_end = 2128
            a.drop(a.loc[starting_info:starting_info_end].index, inplace=True)
            a.drop(a.loc[ending_info:ending_info_end].index, inplace=True)
            a.reset_index(inplace=True, drop=True)
            b.drop(b.loc[starting_info:starting_info_end].index, inplace=True)
            b.drop(b.loc[ending_info:ending_info_end].index, inplace=True)
            b.reset_index(inplace=True, drop=True)
            c.drop(c.loc[starting_info:starting_info_end].index, inplace=True)
            c.drop(c.loc[ending_info:ending_info_end].index, inplace=True)
            c.reset_index(inplace=True, drop=True)
            summed = pandas.concat([a, b, c], axis=1)
            summed["Sum"] = summed[["Counts 1", "Counts 2", "Counts 3"]].astype(int).sum(axis=1)
            globals()[f'df{i}'] = summed
            if i == 1:
                dfn = globals()[f'df{i}']["Sum"]
            else:
                dfn = pandas.concat([dfn, globals()[f'df{i}']["Sum"]], axis=1)
        All_Ave = dfn.mean(axis=1)
        for i in range(0, len(All_Ave)):
             if 0 < All_Ave[i] < 1:
                All_Ave[i] = 0
        self.All_Ave = All_Ave
        return self
    
    def Spectrum(self, show_ave=True, show_all=False, log_plot=True, show_legend=False, energy=8700, width=150):
        """
        A technique to visualize the spectrum files as a Counts vs Energy plot. 
        
        Attributes:
            show_ave: True or False
                Selection to show an average of all scan files.
            show_all: True or False
                Selection to show all scan files (Note; this is computationally heavy if there are many files).
            log_plot: True or False
                Selection to display the counts as obtained or in a log format.
            show_legend: True or False
                Selection to turn off the legend of all displayed traces.
            energy: int (in eV)
                Selection for the energy which is to be used in the raster image. This energy in addition to the 
                specified range will be highlighted on the spectrum plot as a region outlined in gray. 
            width: int (in eV)
                Selection for the range surrounding the specified energy which is to be summed for the raster image. 
                This region will be highlighted on the spectrum plot as a region outlined in gray. 
        Return:
            None. Will modify the data in place.
        """
        self.energy = int(energy)
        self.width = int(width)
        fig = plotly.graph_objects.Figure()
        fig.add_vrect(x0=(self.energy-self.width), 
                      x1=(self.energy+self.width),
                      opacity=0.25, fillcolor="gray", line_width=0)
        if log_plot == False:
            fig.update_layout(yaxis_title="Counts")
            if show_ave == True:
                fig.add_trace(plotly.graph_objects.Scatter(x=self.All_Ave.index*10, 
                                                           y=self.All_Ave, 
                                                           mode="lines", 
                                                           name="Average", 
                                                           marker=dict(color="Black")))
            if show_all == True:
                for j in range(1, max(self.stage["Step"])+1):
                    fig.add_trace(plotly.graph_objects.Scatter(x=globals()[f'df{j}']["Sum"].index*10, 
                                                               y=globals()[f'df{j}']["Sum"], 
                                                               mode="lines", 
                                                               name="Trace"+str(j)))
        else:
            fig.update_layout(yaxis_title="Counts (log)")
            if show_ave == True:
                fig.add_trace(plotly.graph_objects.Scatter(x=self.All_Ave.index*10, 
                                                           y=numpy.nan_to_num(numpy.log(self.All_Ave), neginf=0, nan=0), 
                                                           mode="lines",
                                                           name="Average", 
                                                           marker=dict(color="Black")))
            if show_all == True:
                for j in range(1, max(self.stage["Step"])+1):
                    fig.add_trace(plotly.graph_objects.Scatter(x=globals()[f'df{j}']["Sum"].index*10, 
                                                               y=numpy.nan_to_num(numpy.log(globals()[f'df{j}']["Sum"]), 
                                                                                  neginf=0, nan=0), 
                                                               mode="lines", 
                                                               name="Trace"+str(j)))
        fig.update_traces(showlegend=show_legend)  
        fig.update_layout(title="Spectrum Scan",
                          xaxis_title="Energy (keV)",
                          legend_title="Traces Displayed",
                          height=800,
                          width=1250)
        fig.show()
        return self
    
    def Raster(self, x_step_size=1000, z_step_size=25, max_counts=False):
        """
        A technique to visualize the distribution of a specified energy range over a two-dimensional
        raster iamge.
        
        Attributes: 
            x_step_size: int (microns)
                The physical step size in microns used to correct the X axis step size. 
            z_step_size: int (microns)
                The physical step size in microns used to correct the Z axis step size. 
            max_counts: False or int (counts)
                Selection for limiting the maximum number of counts on the raster image to better visualize
                the count distribution.
        Return:
            None. Will modify the data in place. 
        """
        var_e = int(self.energy/10)
        var_w = int(self.width/10)
        arr = []
        for k in range(1, max(self.stage["Step"])+1):
            summation = sum(globals()[f'df{k}']["Sum"][var_e-var_w:var_e+var_w])
            arr.append(summation)
        arr = numpy.array(arr)
        matrix = arr.reshape((self.x_steps, self.z_steps))
        xs = numpy.arange(0, self.x_steps)*x_step_size
        zs = numpy.arange(0, self.z_steps)*z_step_size
        if max_counts == False:
            fig1 = plotly.express.imshow(matrix.T, x=xs, y=zs, 
                                         color_continuous_scale="Turbo", 
                                         aspect=10,  
                                         labels=dict(x="X [um]", y="Z [um]", color="Sum of Counts"))
        else:
            fig1 = plotly.express.imshow(matrix.T, x=xs, y=zs, 
                                         color_continuous_scale="Turbo", 
                                         aspect=9,  
                                         zmax=max_counts, 
                                         labels=dict(x="X [um]", y="Z [um]", color="Sum of Counts"))
        
        fig1.update_layout(title={'text': str(self.energy)+" ± "+str(self.width)+" eV Emission Distribution"}, 
                           height=800, width=1250) 
        fig1.show()
        return self
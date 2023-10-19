# Imports
import streamlit as st
import numpy as np
import pandas as pd
import scipy
import plotly
import plotly.express
import plotly.graph_objects 

# Formatting and Information
st.set_page_config(layout="wide")
st.title("X-Ray Fluorescence Spectrum Scan Analysis Software") 
st.text("Written by Sierra Dean \n dean.s@spring8.or.jp \n Last updated: 10.19.2023 1:30 pm")
    
st.write("This application endeavors to provide fast XRF analysis from various scan files with a large degree of freedom by offering users analysis tools to accomodate a variety of experimental conditions. To begin, please upload the .csv files obtained from the XRF scan. ")

# Definitions
def nearest_index(array, item):
    return [idx for idx, value in enumerate(array) if value == item]

# Obtain the .csv files of Counts/Channel 
files = st.sidebar.file_uploader(":chart_with_upwards_trend: Please upload the XRF Spectrum Scan here:", accept_multiple_files=True)
Assist = st.sidebar.toggle("Display Help")
if Assist == True:
    st.sidebar.warning("Please upload .csv files containing a single column of XRF data, formatted as counts per eV. The first cell should be a header titled 'Counts'. Each file should have a maximum size of 200 MB per file.")

# AMTEK Emission Data
Element = ["Zinc", "Calcium"]
Energy = [864, 369] 

# Read the file and establish the scan range
if len(files)>0:
    for i in range (0, len(files)):
        globals()["df%s"%i] = pd.read_csv(files[i])
    x=np.arange(0,len(df0),1)    

# Formatting
colL, colML, colMR, colR = st.columns(4)

# Determine if log(y) plotting and Elemental Analysis is desired
LogScale = colL.checkbox("Log Plot")
ElementAnalysis = colML.checkbox("Elemental Analysis")

# Element Selection
if ElementAnalysis == True:
    ElementSelected = st.selectbox("Please choose the desired element", Element)
    SelectedIndex = nearest_index(Element, ElementSelected)
    SelectedEnergy = Energy[SelectedIndex[0]]
    st.success("Selected Energy: "+str(SelectedEnergy)+" eV")

# Plot formatting
fig = plotly.express.line()
fig.update_layout(title="Raw Data")

# Plot the spectrum data
if len(files)>0:
    for j in range(0, len(files)):
        if LogScale == True:
            fig.add_trace(plotly.graph_objects.Scatter(x=x, 
                                                       y=np.nan_to_num(np.log(globals()["df%s"%j]["Counts"]), neginf=0),
                                                       name=str(files[j].name)))
            fig.update_layout(xaxis=dict(title="Energy (ev)"), 
                                       yaxis=dict(title="Counts (log)"))
        else:
            fig.add_trace(plotly.graph_objects.Scatter(x=x, 
                                                       y=globals()["df%s"%j]["Counts"], 
                                                       name=str(files[j].name)))
            fig.update_layout(xaxis=dict(title="Energy (ev)"), 
                                       yaxis=dict(title="Counts"))
            
    # Formatting
    BeforeBoundaries = st.container ()        
    AfterBoundaries = st.container()
    
    if ElementAnalysis == True:
        # Allow the user to change the boundaries defined by the element selected
        boundaries = BeforeBoundaries.slider("Please adjust the boundaries for the peak analysis",
                               SelectedEnergy-100, SelectedEnergy+100, (SelectedEnergy-15, SelectedEnergy+15))
        left_boundary = boundaries[0] 
        right_boundary = boundaries[1] 
        left_boundary_index = nearest_index(x, left_boundary)
        right_boundary_index = nearest_index(x, right_boundary)
        fig.add_vrect(x0=x[left_boundary_index[0]], x1=x[right_boundary_index[0]], opacity=0.25, fillcolor="Red", line_width=0)
        
        # Determine if element peak analysis is desired
        ElementPeak = st.checkbox("Element Peak Analysis")
        if ElementPeak == True:
            # Formatting and user input for scan information
            colL, colR = st.columns(2)
            StepSize = colL.number_input("Scan Step Size")
            Unit = colR.text_input("Scan Step Unit")
            fig2 = plotly.express.line()
            fig2.update_layout(title=str(ElementSelected)+" Analysis for Emission Peak")
            fig3 = plotly.express.line()
            fig3.update_layout(title=str(ElementSelected)+" Analysis for Scan")
            
            all_peaks = []
            all_peaks_x = []
            all_sections = []
            width = x[right_boundary_index[0]] - x[left_boundary_index[0]]
            for k in range(0, len(files)):
                # Determine the peak inside of the emission range
                if LogScale == True:
                    section = np.nan_to_num(np.log(globals()["df%s"%k]["Counts"]), neginf=0)
                    section = section[left_boundary_index[0]:right_boundary_index[0]+1]
                    peaks, _ = scipy.signal.find_peaks(section, distance=max(section))
                    if (len(peaks)>1):
                        index = nearest_index(section[peaks], max(section[peaks]))
                        peaks = peaks[index]
                        if (len(peaks)>1):
                            index = nearest_index(section[peaks], max(section[peaks]))
                            peaks = peaks[index[0]]
                    # Plot the peak information
                    fig2.update_layout(xaxis=dict(title="Energy (eV)"), yaxis=dict(title="Counts at "+str(ElementSelected)+" Peak (Log)"))
                    fig2.add_trace(plotly.graph_objects.Scatter(x=[int(x[peaks+left_boundary_index[0]])],
                                                                y=[float(section[peaks])], 
                                                                mode="markers", name=str(files[k].name)))
#                     fig2.add_trace(plotly.graph_objects.Scatter(x=x[left_boundary_index[0]:right_boundary_index[0]+1],
#                                                                 y=section, 
#                                                                 name=str(files[k].name)))
                    all_peaks.append(float(section[peaks]))
                    all_peaks_x.append(int(x[peaks+left_boundary_index[0]]))
                    all_sections.append(section)
                else:
                    # Determine the peak inside of the emission range
                    section = globals()["df%s"%k]["Counts"][left_boundary_index[0]:right_boundary_index[0]+1]
                    peaks, _ = scipy.signal.find_peaks(section, distance=max(section))
                    if (len(peaks)>1):
                        index = nearest_index(section[peaks+left_boundary_index[0]], max(section[peaks+left_boundary_index[0]]))
                        peaks = peaks[index]
                    # Plot the peak information
                    fig2.update_layout(xaxis=dict(title="Energy (eV)"), yaxis=dict(title="Counts at "+str(ElementSelected)+" Peak"))
                    fig2.add_trace(plotly.graph_objects.Scatter(x=[int(x[peaks+left_boundary_index[0]])],
                                                                y=[int(section[peaks+left_boundary_index[0]])], 
                                                                mode="markers", name=str(files[k].name)))
#                     fig2.add_trace(plotly.graph_objects.Scatter(x=x[left_boundary_index[0]:right_boundary_index[0]+1],
#                                                                 y=section, 
#                                                                 name=str(files[k].name)))
                    all_peaks.append(int(section[peaks+left_boundary_index[0]]))
                    all_peaks_x.append(int(x[peaks+left_boundary_index[0]]))
                    all_sections.append(section)
                
                # If user input for step size has been provided, change the plotting specifics
                if StepSize != 0:
                    fig3.add_trace(plotly.graph_objects.Scatter(x=[k*StepSize], y=[all_peaks[k]], mode="markers", name=str(files[k].name)))
                else:
                    fig3.add_trace(plotly.graph_objects.Scatter(x=[k], y=[all_peaks[k]], mode="markers", name=str(files[k].name)))
            
            # Plot the average scan calculated from all available information
            ave_peak = np.average(all_sections, axis=0)
            fig2.add_trace(plotly.graph_objects.Scatter(x=x[left_boundary_index[0]:right_boundary_index[0]+1],y=ave_peak, name="Average"))
            
            # Plot Formatting
            points = np.arange(0, len(files)+1)
            if StepSize != 0:
                fig3.add_trace(plotly.graph_objects.Scatter(x=points*StepSize, y=all_peaks, opacity=0.5))
                if Unit != "":
                    fig3.update_layout(xaxis=dict(title="Distance ["+str(Unit)+"]"), 
                                       yaxis=dict(title="Counts at "+str(ElementSelected)+" Peak"))
                else:
                    fig3.update_layout(xaxis=dict(title="Distance [Scan Step Size]"), 
                                       yaxis=dict(title="Counts at "+str(ElementSelected)+" Peak"))
            else:
                fig3.add_trace(plotly.graph_objects.Scatter(x=points, y=all_peaks, opacity=0.5))
                fig3.update_layout(xaxis=dict(title="Scan Number"), yaxis=dict(title="Counts at "+str(ElementSelected)+" Peak"))
                
            st.plotly_chart(fig2)
            st.plotly_chart(fig3)
    AfterBoundaries.plotly_chart(fig)
    
# Formatting and Information
st.text("XRF Values provided by AMETEK \n https://www.amptek.com/resources/periodic-table-and-x-ray-emission-line-lookup-chart")

# Update Information
UpdateLog = st.checkbox(":clipboard: Would you like to view the update log?")
if UpdateLog == True:
    st.balloons()
    st.text("10.19.2023 1:30 pm, Added the element analysis plots and added to github.")
    st.text("10.17.2023 9:00 am, Wrote the software")
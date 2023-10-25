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
st.title("DeansXRF Scan")
st.header("A fast X-ray fluorescence spectroscopy scan analysis application")
st.text("Written by Sierra Dean \n dean.s@spring8.or.jp \n Last updated: 10.24.2023 12:00 pm")
    
st.write("This application endeavors to provide fast XRF analysis from various scan files with a large degree of freedom "
         "by offering users analysis tools to accomodate a variety of experimental conditions. To begin, please upload the "
         ".csv files obtained from the XRF scan. ")

# Definitions
def nearest_index(array, item):
    """Searches an array for an item known to be contained within the array.
    
    Args:
    array: An array or list of items.
    item: An item.
    
    Returns: The index of array which contains the item.
    """
    return [idx for idx, value in enumerate(array) if value == item]

def find_nearest(a, a0):
    idx = np.abs(a - a0).argmin()
    return a.flat[idx]

# Obtain the .csv files of Counts/Channel 
files = st.sidebar.file_uploader(":chart_with_upwards_trend: Please upload the XRF Spectrum Scan here:", accept_multiple_files=True)
Assist = st.sidebar.toggle("Display Help")
if Assist == True:
    st.sidebar.warning("Please upload .csv files containing a single column of XRF data, formatted as counts per eV. "
                       "The first cell should be a header titled 'Counts'. Each file should have a maximum size of 200 MB per file.")

# AMTEK Emission Data
Element = ["Sulfur", "Calcium", "Iron", "Copper", "Zinc", "Bromine", "Inelastic Scattering", "Elastic Scattering"]
Energy = [2307.84, 3691.68, 6403.84, 8047.78, 8638.86, 11924.2, 16800, 17500]
Scale = [0.98625641025641025641025641025641, 0.98972654155495978552278820375335, 0.99438509316770186335403726708075, 0.99478121137206427688504326328801, 0.99526036866359447004608294930876, 0.99617376775271512113617376775272, 1, 1]

# Read the file and establish the scan range
if len(files)>0:
    for i in range (0, len(files)):
        globals()["df%s"%i] = pd.read_csv(files[i])
    x=np.arange(0,len(df0),1)*10
    
# Formatting
colL, colML, colMR, colR = st.columns(4)
colL.subheader("Plotting Options")
colML.subheader("Analysis Options")

# Options
LogScale = colL.checkbox("Log Plot")
ElementAnalysis = colML.checkbox("Elemental Analysis")

if ElementAnalysis == True:
    ElementSelected = st.selectbox("Please choose the desired element", Element)
    SelectedIndex = nearest_index(Element, ElementSelected)
    SelectedEnergy = Energy[SelectedIndex[0]]
    st.success("Selected Energy: "+str(SelectedEnergy)+" eV")
    cont = st.container()
    x=x*Scale[SelectedIndex[0]]
    
fig = plotly.express.line()
fig2 = plotly.express.line()

hidelegend = colL.checkbox("Hide Legend")
largeformat = colL.checkbox("Fullscreen Format")
    
if len(files)>0:
    for j in range(0, len(files)):
        if LogScale == True:
            fig.add_trace(plotly.graph_objects.Scatter(x=x,
                                                       y=np.nan_to_num(np.log(globals()["df%s"%j]["Counts"]), neginf=0),
                                                       name=str(files[j].name)))
            fig.update_layout(xaxis=dict(title="Energy (eV)"), 
                                       yaxis=dict(title="Counts (log)"))
        else:
            fig.add_trace(plotly.graph_objects.Scatter(x=x,
                                                       y=globals()["df%s"%j]["Counts"],
                                                       name=str(files[j].name)))
            fig.update_layout(xaxis=dict(title="Energy (eV)"), 
                                       yaxis=dict(title="Counts"))
            
    # Formatting
    BeforeBoundaries = st.container()        
    AfterBoundaries = st.container()
    
    if ElementAnalysis==True:
        colL, colR = st.columns(2)
        StepSize = colL.number_input("Scan Step Size")
        Unit = colR.text_input("Scan Step Unit")
        fig2.update_layout(title=str(ElementSelected)+" Analysis")
        
        input_range = cont.number_input("Please choose a summation range", value=100)
        fig.add_vline(x=SelectedEnergy, opacity=0.5, line_dash="dash")
        left_boundary = SelectedEnergy-input_range
        right_boundary = SelectedEnergy+input_range
        a = find_nearest(x, left_boundary)
        a_index = nearest_index(x, a)
        b = find_nearest(x, right_boundary)
        b_index = nearest_index(x, b)
        fig.add_vrect(x0=x[a_index[0]], 
                      x1=x[b_index[0]], 
                      opacity=0.25, 
                      fillcolor="Red", 
                      line_width=0)
        
        all_sums = []
        for k in range(0, len(files)):
            if LogScale == True:
                all_sums.append(np.sum(np.nan_to_num(np.log(globals()["df%s"%k]["Counts"][a_index[0]:b_index[0]+1]), neginf=0)))
            else:
                all_sums.append(np.sum(globals()["df%s"%k]["Counts"][a_index[0]:b_index[0]+1]))
        x2 = np.arange(0, len(all_sums), 1)
        if StepSize != 0:
            x2 = x2*StepSize
        if largeformat == True:
            fig2.add_trace(plotly.graph_objects.Scatter(x=x2, 
                                                        y=all_sums,
                                                        marker=dict(color="Black", size=10),
                                                        mode="lines+markers", name="Scan"))
        else:
            fig2.add_trace(plotly.graph_objects.Scatter(x=x2, y=all_sums, marker=dict(color="Black"),
                                                        mode="lines+markers", name="Scan"))
        if Unit != "":
            fig2.update_layout(xaxis=dict(title="Distance ["+str(Unit)+"]"), 
                                       yaxis=dict(title="Sum of counts in  "+str(ElementSelected)+" emission range"))
        else:
            fig2.update_layout(xaxis=dict(title="Distance [Scan Step Size]"), 
                                       yaxis=dict(title="Sum of counts in  "+str(ElementSelected)+" emission range"))
        
        if hidelegend == True:
            fig2.update_layout(showlegend=False)
        if largeformat == True:
            fig2.update_xaxes(title_font={"size":30}, tickfont=dict(size=25))
            fig2.update_yaxes(title_font={"size":30}, tickfont=dict(size=25))
        st.plotly_chart(fig2)
    if hidelegend == True:
        fig.update_layout(showlegend=False)
    if largeformat == True:
        fig.update_xaxes(title_font={"size":30}, tickfont=dict(size=25))
        fig.update_yaxes(title_font={"size":30}, tickfont=dict(size=25))
    AfterBoundaries.plotly_chart(fig)


# Formatting and Information
st.text("XRF Values provided by https://xdb.lbl.gov/Section1/Table_1-2.pdf")

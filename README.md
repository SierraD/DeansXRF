# About DeansXRF
DeansXRF is an interactive application for fast X-ray Fluorescence Spectroscopy analysis, designed for automated processing, analysis, and visualization for charactertistic X-ray fluorescence spectrum taken over a two dimensional scan.

## Instructions for DeansXRF:

> [!IMPORTANT]  
> Must have Python, Anaconda powershell, or Jupyter Notebook, etc installed.

- Download DeansXRF.py from Github
- Open python command line
- cd into the folder containing the downloaded file
- Type "python" to open the python environment
- Type the following then click enter:
  - ```ruby
    from DeansXRF import DeansXRF
    ```
- Type the following then click enter: (The path should be the operating system path to your two-dimensional scan files. It is important to include the r outside of the quotation marks)
  - ```ruby
    a = DeansXRF(r"C:\Users\User\Desktop\Folder")
    ```
- Type the following then click enter: 
  - ```ruby
    a.Initiate()
    ```
- To view the spectrum, type the following then click enter: (Please change the variables to reflect the desired outcome. The energy and width should be in eV.)
  - ```ruby
    a.Spectrum(show_ave=True, show_all=False, log_plot=True, show_legend=False, energy=8700, width=150)
    ```
- Ensure that the energy and width encompasses the characteristic fluorescent peak that you would like to generate the distribution for.
- To view the raster image, type the following then click enter: (Please change the variables to reflect the desired outcome. The X and Z step size should be in micrometers.)
  - ```ruby
    a.Raster(x_step_size=1000, z_step_size=25, max_counts=False)
    ```
- Finished. Both plots are interactive and enable download.
  
DeansXRF developed by Sierra Dean @ RIKEN SPring-8 Center (Japan) 2024 <br />
Email: ccnd@live.com

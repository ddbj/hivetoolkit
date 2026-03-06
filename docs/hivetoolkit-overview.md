# hivetoolkit Overview

## 1. Overview

This document provides an overview of the visualization capabilities offered by **hivetoolkit**.

`hivetoolkit` focuses exclusively on _how Hive-format mass spectrometry data are visualized_.
It does not handle data access or analysis. Data objects passed to the visualization
functions are obtained via the Hive Data Access API for Python (`hive-data-access`).

The visualization functions in `hivetoolkit` return Plotly `Figure` objects and are
designed for interactive environments such as Jupyter Notebook and JupyterLab.

This guide describes **what kinds of visualizations are available** and **how they are
conceptually used**.
Executable examples demonstrating typical workflows are provided in the notebooks
included in this repository.

For detailed function definitions, arguments, and supported options, see
**hivetoolkit-api-reference.md**.

## 2. Chromatogram Visualization

Chromatograms represent signal intensity as a function of retention time.

Typical chromatograms derived from scan MS data include TIC (Total Ion Chromatogram),
BPC (Base Peak Chromatogram), and XIC (Extracted Ion Chromatogram).
Chromatogram point lists are usually obtained from `QualAnalysis` or `QuanAnalysis`
objects provided by `hive-data-access`.
Chromatograms from `DADAnalysis` or `AnalogAnalysis` objects are also supported.

In `hivetoolkit`, chromatogram visualization is intended for both exploratory inspection
and comparative analysis of chromatographic behavior.

### Available Functions

-   **`draw_chromatogram`**
    Draws a single chromatogram, such as TIC, BPC, or XIC.

-   **`draw_overlaid_chromatogram`**
    Draws multiple chromatograms overlaid in a single figure, which is useful for
    comparing chromatographic profiles across samples or conditions.

For detailed descriptions of function arguments and optional settings, refer to
**hivetoolkit-api-reference.md**.

## 3. Spectrum Visualization

Spectra represent signal intensity as a function of m/z (or wavelength) at a specific
acquisition point.

Spectrum data are typically obtained from a `QualAnalysis` object via the
`hive-data-access` API.
DAD spectra obtained from a `DADAnalysis` object are also supported.

Spectrum visualization in `hivetoolkit` is commonly used to inspect signal composition
at a specific retention time, confirm peak identity, or compare spectral patterns
between samples.

### Available Functions

-   **`draw_spectrum`**
    Draws a single mass spectrum or DAD spectrum.

-   **`draw_spectra_map`**
    Draws multiple spectra together as a two-dimensional map of retention time versus
    m/z (or wavelength), where signal intensity is represented using a color scale.

For detailed descriptions of function arguments and optional settings, refer to
**hivetoolkit-api-reference.md**.

## 4. Combined and Multi-panel Visualization

In exploratory data analysis, it is often useful to inspect multiple visualizations
simultaneously.

`hivetoolkit` provides functionality to combine multiple plots into a single
multi-panel layout, allowing related views of the data to be inspected side by side.

### Available Function

-   **`draw_multiplot`**
    Creates a multi-panel figure by arranging multiple chromatograms and/or spectra
    into a single layout.

For details on how to construct and render multi-panel figures, refer to
**hivetoolkit-api-reference.md** and the example notebooks.

## 5. Customization Overview

`hivetoolkit` allows basic customization of plot appearance and annotation behavior.

### 5.1 Visual Appearance Styles

Styles control the overall look of plots, such as color theme, layout spacing,
and font style.

For detailed usage of style settings, see **hivetoolkit-api-reference.md**.

### 5.2 Annotation Labels

Annotation labels can be used to highlight peaks or specific positions on plots.

For detailed usage of labeling settings, see **hivetoolkit-api-reference.md**.

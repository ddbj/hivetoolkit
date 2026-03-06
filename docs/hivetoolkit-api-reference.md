# hivetoolkit API Reference

## 1. Overview

This document provides the reference manual for the public API of **hivetoolkit**.
It is intended as a dictionary-style API reference.
Conceptual explanations and usage-oriented documentation are provided in
**hivetoolkit-visualization-guide.md**.
<br>

## 2. Public Functions

The following functions provide the primary visualization capabilities of hivetoolkit.

### `draw_chromatogram` function

Draws a single chromatogram.

#### Synopsis

> `draw_chromatogram(quan_chrom, title=None, x_label='Minutes', y_label='Absolute Intensity',
style=None, labels=None, color=None, multiplot=None, allow_negative_intensity=False,
width=None, height=None, _out_writer=None)`

#### Arguments

-   `quan_chrom` (mandatory): a **QuanAnalysis** or **AnalogAnalysis** object,
    or a list of **ChromatogramPoint** or **SpectrumBasedChromatogramPoint** objects.
-   `title` (optional): The text displayed as the graph title.
    When `quan_chrom` is a **QuanAnalysis** or **AnalogAnalysis** object,
    the title is automatically generated unless explicitly provided by the user.
-   `x_label`, `y_label` (optional): Texts to be displayed as the graph axis title.
    When `quan_chrom` is a **QuanAnalysis** or **AnalogAnalysis** object,
    they are automatically generated unless explicitly provided by the user.
-   `style` (optional): A _HivePlotlySettings_ object, or a dict specifying plot settings,
    such as color themes, fonts and layout spacing.
    See the [_HivePlotlySettings_](#hiveplotlysettings-class) section below for details.
-   `labels` (optional): A dict to specify graph annotation labels.
    Typical usage is to annotate the peak top, by showing intensity and location.
    See the [_HivePlotlyLabels_](#hiveplotlylabels-class) section below for details.
-   `color` (optional): A color value compatible with Python color specifications
    (e.g., HEX, RGB, or named colors).
    If not specified, a color will be assigned automatically.
-   `multiplot` (optional): To create multiple plots in a trellis arrangement,
    specify a list where the multi-plot information will be stored.
    The actual rendering is deferred until the `draw_multiplot` function is called.
    For details, see the [`draw_multiplot`](#draw_multiplot-function) section below.
-   `allow_negative_intensity` (optional): Defaults to False.
    Set this to True when plotting a chromatogram that contains negative intensity values
    (e.g., data derived from DAD).
-   `width`, `height` (optional): The size of the graph in pixels.
-   `_out_writer` (internal use): This is for internal system use only.
    Users should not modify this parameter.

### `draw_overlaid_chromatogram` function

Draws multiple chromatograms on a single graph.

#### Synopsis

> `draw_overlaid_chromatogram(quan_chrom_list, title = None,
x_label = 'Minutes', y_label = 'Absolute Intensity', style = None, colors=None,
multiplot=None, allow_negative_intensity=False, width=None, height=None, _out_writer=None)`

#### Arguments

-   `quan_chorm_list` (mandatory): a list of **QuanAnalysis** or **AnalogAnalysis** objects,
    or a list of lists of **ChromatogramPoint** or **SpectrumBasedChromatogramPoint** objects.
-   `title` (optional): The text displayed as the graph title.
    Unlike `draw_chromatogram`, title will not be automatically generated.
-   `x_label`, `y_label` (optional): Texts to be displayed as the graph axis title.
    Unlike `draw_chromatogram`, `x_label` and `y_label` will not be automatically generated.
    The default values assume MS cases. Thus you must explicitly assign these
    for non-MS data.
-   `style` (optional): A _HivePlotlySettings_ object, or a dict specifying plot settings,
    such as color themes, fonts and layout spacing.
    See the [_HivePlotlySettings_](#hiveplotlysettings-class) section below for details.
-   `colors` (optional): A list of color values compatible with Python color specifications
    (e.g., HEX, RGB, or named colors).
    If not specified, colors will be assigned automatically.
-   `multiplot` (optional): To create multiple plots in a trellis arrangement,
    specify a list where the multi-plot information will be stored.
    The actual rendering is deferred until the `draw_multiplot` function is called.
    For details, see the [`draw_multiplot`](#draw_multiplot-function) section below.
-   `allow_negative_intensity` (optional): Defaults to False.
    Set this to True when plotting a chromatogram that contains negative intensity values
    (e.g., data derived from DAD).
-   `width`, `height` (optional): The size of the graph in pixels.
-   `_out_writer` (internal use): This is for internal system use only.
    Users should not modify this parameter.

### `draw_spectrum` function

Draw a single spectrum.

#### Synopsis

> `draw_spectrum(points, title = None, x_label = 'm/z', y_label = 'Absolute Intensity',
style = '', labels=None, color=None, multiplot=None, relative_intensity_cutoff=1e-3,
allow_negative_intensity = False, width=None, height=None, _out_writer=None)`

#### Arguments

-   `points` (mandatory): a **Spectrum** or **DADSpectrum** object,
    or a list of **SpectrumPoint** objects.
-   `title` (optional): The text displayed as the graph title.
    When `points` is a **Spectrum** or **DADSpectrum** object,
    the title is automatically generated unless explicitly provided by the user.
-   `x_label`, `y_label` (optional): Texts to be displayed as the graph axis title.
    When `points` is a **Spectrum** or **DADSpectrum** object,
    they are automatically generated unless explicitly provided by the user.
-   `style` (optional): A _HivePlotlySettings_ object, or a dict specifying plot settings,
    such as color themes, fonts and layout spacing.
    See the [_HivePlotlySettings_](#hiveplotlysettings-class) section below for details.
-   `labels` (optional): A dict to specify graph annotation labels.
    Typical usage is to annotate the peak top, by showing intensity and location.
    See the [_HivePlotlyLabels_](#hiveplotlylabels-class) section below for details.
-   `color` (optional): A color value compatible with Python color specifications
    (e.g., HEX, RGB, or named colors).
    If not specified, a color will be assigned automatically.
-   `multiplot` (optional): To create multiple plots in a trellis arrangement,
    specify a list where the multi-plot information will be stored.
    The actual rendering is deferred until the `draw_multiplot` function is called.
    For details, see the [`draw_multiplot`](#draw_multiplot-function) section below.
-   `relative_intensity_cutoff` (optional): A ratio between 0 and 1,
    where the maximum intensity is 1. The default value is `0.001`.
    It is highly recommended to set this value. While low-intensity signals
    are often invisible on the graph, their large population can slow down processing.
    Using this cutoff significantly improves performance.
-   `allow_negative_intensity` (optional): Defaults to False.
    Set this to True when plotting a chromatogram that contains negative intensity values
    (e.g., data derived from DAD).
-   `width`, `height` (optional): The size of the graph in pixels.
-   `_out_writer` (internal use): This is for internal system use only.
    Users should not modify this parameter.

### `draw_spectra_map` function

Draw a series of spectra as a 2-dimensional map of retention time vs. m/z or wavelength plane.
Intensity is displayed on a color scale.

#### Synopsis

> `draw_spectra_map(qual_or_spectra, acquisiiton_condition = None, title = None,
x_label = 'RT', y_label = "m/z", style = '', x_resolution=0.01, y_resolution=1.0,
multiplot=None, width=None, height=None, _out_writer=None)`

#### Arguments

-   `qual_or_spectra` (mandatory): a **QualAnalysis** or **DADAnalysis** object,
    or a list of **Spectrum** or **DADSpectrum** objects.
-   `acquisition_condition` (mandatory for QualAnalysis):
    Required when the first argument is a **QualAnalysis** object.
    This specifies the **AcquisitionCondition** used to filter the scan spectra.
    Since **QualAnalysis** stores all scan spectra regardless of their
    acquisition conditions, this restriction is necessary to ensure the
    consistency of the displayed data.
-   `title` (optional): The text displayed as the graph title.
-   `x_label`, `y_label` (optional): Texts to be displayed as the graph axis title.
    When `qual_or_spectra` is a **QualAnalysis** or **DADAnalysis** object,
    they are automatically generated unless explicitly provided by the user.
-   `style` (optional): A _HivePlotlySettings_ object, or a dict specifying plot settings,
    such as color themes, fonts and layout spacing.
    See the [_HivePlotlySettings_](#hiveplotlysettings-class) section below for details.
-   `x_resolution`, `y_resolution` (optional):
    Default values are 0.01 for `x_resolution` and 1.0 for `y_resolution`.
    These parameters are used to bin the retention time value (x axis)
    and the m/z or wavelength values (y axis) to determine the intensity
    of each cell in the two-dimensional map.
    Plot color of the cell is determined by the highest intensity within the cell.
-   `multiplot` (optional): To create multiple plots in a trellis arrangement,
    specify a list where the multi-plot information will be stored.
    The actual rendering is deferred until the `draw_multiplot` function is called.
    For details, see the [`draw_multiplot`](#draw_multiplot-function) section below.
-   `width`, `height` (optional): The size of the graph in pixels.
-   `_out_writer` (internal use): This is for internal system use only.
    Users should not modify this parameter.

### `draw_multiplot` function

Draws multiple sub-graphs in a trellis arrangement.

#### Synopsis

> `draw_multiplot(multi_fig, num_col=3, row_height=150, keep_axis_title=False,
horizontal_space=0.05, _out_writer=None)`

#### Arguments

-   `multi_fig` (mandatory): A list storing drawing data of sub-graphs.
-   `num_col` (optional): The number of trellis columns. Default is 3.
-   `row_height` (optional): Height of each row in the trellis, in pixels.
    Default is 150.
-   `keep_axis_title` (optional): Default is False.
    Set to True if the title of each sub-graph should be preserved.
-   `horizontal_space` (optional): Width of a space between sub-graphs.
    Specify by a ratio between 0 and 1, where the whole graph width is 1.
    Default is 0.05.
-   `_out_writer` (internal use): This is for internal system use only.
    Users should not modify this parameter.

#### Usage

To draw multiple graphs in a trellis arrangement, follow the steps below:

1. Prepare an empty list.  
   e.g. `multi_fig = []`  
   This list is used to store all graph data.
2. Call `draw_chromatogram`, `draw_overlaid_chromatogram`, `draw_spectrum` or
   `draw_spectra_map` functions to define sub-graphs in the parent graph.

    - To call `draw...` functions, specify the defined `multi_fig` object
      as the argument of `multi_fig`.
    - Actual rendering does not occur on calling the `draw...` function.
    - Instead, drawing data is stored within the specified `multi_fig` object.
    - The sub-graphs are arranged horizontally at first, on called order.

3. Call `draw_multiplot` function with the `multi_fig` argument.  
   Then rendering of all sub-graphs is performed.

## 3. Supporting Classes

The following classes are used to configure visualization styles and labels.
They are typically passed as arguments to the functions described above.

## HivePlotlySettings class

This class controls the following graph styles:

-   `Theme` or `Template`:  
    The following options are available:
    -   `auto` or `adaptive`: (default) Automatic color theme selection
        according to the front-end, such as Jupyter Notebook.  
        N.B. This may not always work. Explicitly select an appropriate theme
        if it would not work.
    -   `none` or `transparent`: No color theme. Use transparent color if available.
    -   `plotly`: Plotly default plotting theme.
    -   `white` or `light`: White background theme.
    -   `dark` or `black`: Dark or black background theme.
    -   `presentation`: Presentation-oriented theme.
-   `Layout` or `Spacing`:  
    The following options are available:
    -   `normal`: (default) Normal spacing layout.
    -   `compact`: Compact or dense spacing layout.
    -   `spacious`: Spacious or well-spaced layout.
-   `Font` (Font Family):  
    The following options are available:
    -   `sansserif`: (default) Sans-Serif font series, like Arial, verdana.
    -   `serif`: Serif font series, like Times, Georgia.

This can be specified as `style` optional argument of each `draw_...` function
(except `draw_multiplot`), or `set_default_plot_style(...)` function to define
the default style.

The style argument can be specified as a dict.

For dict keys, and values, above the listed words can be used.

> [TIPS!]
> When using the dict to define the style,
> keywords and value words do not need to be fully spelled out 
> as long as they are unambiguous.

Examples:

```
style = dict(template='white', font='sansserif', spacing='compact')
# style = dict(temp='white', font='sans', spac='comp') # Abbreviated notation is also possible.
hivetoolkit.draw_chromatogram(quan_analysis, style=style)
```

## HivePlotlyLabels class

This class defines how annotation labels are rendered on the graph.
Labels are configured using a **dictionary**.

There are two patterns for defining label information:

### Labeling peak tops

This pattern labels the top N peaks based on the specified style.

Full syntax for peak labels:

```
label=dict(top=dict(n=<num_labels>, format=<label_format>), offset=<offset_value>)
```

-   `<num_labels>`: The number of top peaks to label.
    If this is 1 (to label only the highest peak), then `n=<num_peak>` part can be omitted.
-   `<format_label>`: A Python format string. You can use the variables `{x}` and `{y}`
    to represent the coordinates of the label location.
    If omitted, the default format `"({x:.2f}, {y:.1e})"` is used.
-   `<offset_value>`: Vertical offset of the location where the label is displayed.

Examples:

```
label=dict(top=dict(n=5, format="RT={x:.3f}, Intensity={y:.1e}"), offset=30)
label=dict(top=2) ## Labels top 2 peaks with the default format.
label=dict(top="RT={x:.2f}, Intensity={y:.1e}") ## Labels only the highest peak with a custom format.
```

### Labeling at a fixed location

This pattern places an annotation label at a specified x-coordinate.

Full syntax for fixed location label:

```
label={<location> : <label_format>}
```

-   `<location>`: The x-axis value where the label should be placed.
-   `<label_format>`: Same as the format string described above.

Examples:

```
label={3.2 : "Location at 3.2 min"}
```

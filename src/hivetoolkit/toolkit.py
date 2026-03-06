#region Imports
import hivetoolkit.adaptive_plotly as ap
import plotly.graph_objects as go
import plotly.colors as plcolors
import plotly.io as pio
import os
import re
import copy
import math
import statistics
import hive_data_access
import numpy as np
from pathlib import Path
from io import StringIO
from plotly.subplots import make_subplots
from datetime import datetime
from enum import Enum
#endregion Imports

#region hivetoolkit internal classes and functions

class HivePlotlySettings:
    """Settings of plot styles for Hive.
    Styles can be set by a dict or keywords.
    When specified by a dict, then following keys and values can be assigned:
    - `theme` or `template`:
      - `auto` or `adaptive` (default)
      - `none` or `transparent`
      - `white` or `light`
      - `dark` or `black`
      - `plotly`
      - `presentation`
    - `layout` or `spacing`:
      - `normal` (default)
      - `compact`
      - `spacious`
    - `font` or `fontfamily`:
      - `sansserif` (default)
      - `serif`

    Keywords are case-insensitive and can be separated by spaces, commas, semicolons, vertical bars, or slashes.
    Dots, hyphens, and underscores in keywords are ignored.
    Keywords can be abbreviated as long as they are unambiguous.
    Possible keywords:
    - (theme or template related)
      - auto-theme (default)
      - no-theme
      - white-theme
      - dark-theme
      - plotly-theme
      - presentation-theme
    - (font related)
      - sans-serif-font (default)
      - serif-font
    - (layout or spacing related)
      - normal-layout (default)
      - compact-layout
      - spacious-layout
    """

    SERIF_FONTS = 'Times New Roman, Georgia, serif'
    SANS_SERIF_FONTS = 'Open Sans, verdana, Arial, sans-serif'
    FONTS_LOOKUP = { "serif" : SERIF_FONTS, "sansserif" : SANS_SERIF_FONTS }

    def __init__(self, style_def = None, template = 'auto', font = 'sansserif', spacing = 'normal', title_fontsize = 16, label_fontsize = 14, responsive = True):
        if not template in ['plotly', 'plotly_white', 'plotly_dark', 'presentation', 'none', 'auto']:
            raise ValueError(f"template must be one of 'plotly', 'plotly_white', 'plotly_dark', 'presentation', or 'none'")
        if not font in HivePlotlySettings.FONTS_LOOKUP:
            raise ValueError(f"font must be one of 'serif' or 'sansserif'")
        if not spacing in ['compact', 'normal', 'spacious']:
            raise ValueError(f"spacing must be one of 'compact', 'normal', or 'spacious'")
        if not isinstance(title_fontsize, (int, float)) or title_fontsize <= 5:
            raise ValueError(f"title_fontsize must be a positive number larger than 5")
        if not isinstance(label_fontsize, (int, float)) or label_fontsize <= 5:
            raise ValueError(f"label_fontsize must be a positive number larger than 5")
        if not isinstance(responsive, bool):
            raise TypeError(f"responsive must be a bool value")
        if template == 'auto':
            self._auto_theme = True
            self._explicit_template = False
            self._template = 'none'
        else:
            self._auto_theme = False
            self._explicit_template = True
            self._template = template
        self._font_family = self.FONTS_LOOKUP[re.sub(r'\W+', '', font.lower())]
        self._axis_color = 'black'
        self._axis_standoff_base = 15
        self._margin_width_base = 40
        self._fontsize_title_base = title_fontsize
        self._fontsize_label_base = label_fontsize
        self._layout_spacing = spacing # 'compact' or 'normal' or 'spacious'
        self._responsive = responsive
        # print(f"Initialized HivePlotlySettings: {self}")
        if style_def:
            self.set_style(style_def)
    def __str__(self):
        ret = StringIO()
        match self._template:
            case 'plotly_white':
                ret.write("White-Theme")
            case 'plotly_dark':
                ret.write("Dark-Theme")
            case 'presentation':
                ret.write("Presentation-Theme")
            case 'plotly':
                ret.write("Plotly-Theme")
            case 'none':
                ret.write("No-Theme")
            case 'auto':
                ret.write("Auto-Theme")
            case _:
                ret.write('[' + str(self._template) + "]-Theme")
        ret.write(" " + self._layout_spacing.capitalize() + "-Layout ")
        match self._font_family:
            case self.SANS_SERIF_FONTS:
                ret.write("Sans-Serif-Font")
            case self.SERIF_FONTS:
                ret.write("Serif-Font")
            case _:
                ret.write('[' + str(self._font_family) + "]-Font")
        return ret.getvalue().strip()
    def _match_shorter(self, str1, str2):
        return str2.startswith(str1) if len(str1) < len(str2) else str1.startswith(str2)
    def set_style(self, style_def):
        # import inspect
        # print(f"Setting HivePlotlySettings style with: {style_def} called {inspect.stack()[1]}")
        if (isinstance(style_def, HivePlotlySettings)):
            self._template = style_def._template
            self._font_family = style_def._font_family
            self._axis_color = style_def._axis_color
            self._axis_standoff_base = style_def._axis_standoff_base
            self._layout_spacing = style_def._layout_spacing
            self._margin_width_base = style_def._margin_width_base
            self._fontsize_title_base = style_def._fontsize_title_base
            self._fontsize_label_base = style_def._fontsize_label_base
            self._responsive = style_def._responsive
        elif isinstance(style_def, dict) or (isinstance(style_def, list) and 0 < len(style_def) and all(isinstance(item, tuple) and len(item) == 2 for item in style_def)):
            for key, value in style_def.items() if isinstance(style_def, dict) else style_def:
                key = re.sub(r'[\.\-_]', '', key).lower()
                # print(f"Setting plotly style key: {key}, value: {value}")
                if any(s.startswith(key) for s in ['template', 'theme']):
                    self._explicit_template = True
                    self._auto_theme = False
                    value = re.sub(r'[\.\-_]', '', value).lower()
                    if ('presentation'.startswith(value)):
                        self._template = 'presentation'
                        self._axis_color = 'black'
                        self._axis_standoff_base = 20
                    elif any(s.startswith(value) for s in ['dark', 'black']):
                        self._template = 'plotly_dark'
                        self._axis_color = 'white'
                        self._axis_standoff_base = 15
                    elif any(s.startswith(value) for s in ['white', 'light']):
                        self._template = 'plotly_white'
                        self._axis_color = 'black'
                        self._axis_standoff_base = 15
                    elif any(s.startswith(value) for s in ['none', 'transparent']):
                        self._template = 'none'
                        self._axis_color = pio.templates['none'].layout.font.color
                        self._axis_standoff_base = 15
                    elif any(s.startswith(value) for s in ['auto', 'adaptive']):
                        self._template = 'none'
                        self._axis_color = pio.templates['none'].layout.font.color
                        self._axis_standoff_base = 15
                        self._auto_theme = True
                    elif ('plotly'.startswith(value)):
                        self._template = 'plotly'
                        self._axis_color = 'black'
                        self._axis_standoff_base = 15
                    else:
                        raise ValueError(f"Unknown template/theme value: {value}")
                    # print(f"Set template to {self._template}, explicit={self._explicit_template}")
                elif any(s.startswith(key) for s in ['layout', 'spacing']):
                    value = re.sub(r'[\.\-_]', '', value).lower()
                    if ('compact'.startswith(value)):
                        self._layout_spacing = 'compact'
                    elif ('spacious'.startswith(value)):
                        self._layout_spacing = 'spacious'
                    elif ('normal'.startswith(value)):
                        self._layout_spacing = 'normal'
                    else:
                        raise ValueError(f"Unknown layout/spacing value: {value}")
                elif 'fontfamily'.startswith(key):
                    value = re.sub(r'[\.\-_]', '', value).lower()
                    if ('sansserif'.startswith(value)):
                        self._font_family = self.SANS_SERIF_FONTS
                    elif ('serif'.startswith(value)):
                        self._font_family = self.SERIF_FONTS
                    else:
                        raise ValueError(f"Unknown font/fontfamily value: {value}")
                elif 'responsive'.startswith(key):
                    if isinstance(value, bool):
                        self._responsive = value
                    elif isinstance(value, str):
                        if value.lower() in ('y', 'yes', 't', 'true'):
                            self._responsive = True
                        elif value.lower() in ('n', 'no', 'f', 'false'):
                            self._responsive = False
                        else:
                            raise ValueError(f"Invalid value {value} for responsive. Must be bool.")
                    else:
                        self._responsive = bool(value)
                else:
                    raise ValueError(f"Unknown style key: {key}")
        elif isinstance(style_def, str):
            words = re.split(r'[\s,;\|\/]+', style_def)
            for w in words:
                handled = False
                w = re.sub(r'[\.\-_]', '', w).lower()
                #print(f"Setting plotly style keyword: {w}")
                if self._match_shorter(w, 'plotlytheme'):
                    self._template = 'plotly'
                    self._axis_color = 'black'
                    self._axis_standoff_base = 15
                    self._explicit_template = True
                    self._auto_theme = False
                    handled = True
                elif self._match_shorter(w, 'whitetheme'):
                    self._template = 'plotly_white'
                    self._axis_color = 'black'
                    self._axis_standoff_base = 15
                    self._explicit_template = True
                    self._auto_theme = False
                    handled = True
                elif self._match_shorter(w, 'darktheme'):
                    self._template = 'plotly_dark'
                    self._axis_color = 'white'
                    self._axis_standoff_base = 15
                    self._explicit_template = True
                    self._auto_theme = False
                    handled = True
                elif self._match_shorter(w, 'presentationtheme'):
                    self._template = 'presentation'
                    self._axis_color = 'black'
                    self._axis_standoff_base = 20
                    self._explicit_template = True
                    self._auto_theme = False
                    handled = True
                elif self._match_shorter(w, 'notheme') or self._match_shorter(w, 'transparenttheme'):
                    self._template = 'none'
                    self._axis_color = pio.templates['none'].layout.font.color
                    self._axis_standoff_base = 15
                    self._explicit_template = True
                    self._auto_theme = False
                    handled = True
                elif self._match_shorter(w, 'autotheme'):
                    self._template = 'none'
                    self._axis_color = pio.templates['none'].layout.font.color
                    self._axis_standoff_base = 15
                    self._explicit_template = True
                    self._auto_theme = True
                    handled = True
                if self._match_shorter(w, 'normallayout'):
                    self._layout_spacing = 'normal'
                    handled = True
                elif self._match_shorter(w, 'compactlayout'):
                    self._layout_spacing = 'compact'
                    handled = True
                elif self._match_shorter(w, 'spaciouslayout'):
                    self._layout_spacing = 'spacious'
                    handled = True
                if self._match_shorter(w, 'sansseriffont'):
                    self._font_family = self.SANS_SERIF_FONTS
                    handled = True
                elif self._match_shorter(w, 'seriffont'):
                    self._font_family = self.SERIF_FONTS
                    handled = True
                if not handled:
                    raise ValueError(f"Unknown style keyword: {w}")
        else:
            raise TypeError(f"style_base must be keywords or existing HivePlotlySettings instance")

    def _get_actual_size(self, base_size, convert_int = True):
        match self._layout_spacing:
            case 'compact':
                val = int(base_size * 0.75)
                return int(round(val)) if convert_int else val
            case 'spacious':
                val = int(base_size * 1.5)
                return int(round(val)) if convert_int else val
            case 'normal':
                return int(base_size)
            case _:
                raise KeyError(f"Unknown spacing keyword {self._layout_spacing}")
    def _get_axis_standoff(self):
        return self._get_actual_size(self._axis_standoff_base)
    def _get_label_fontsize(self):
        return self._get_actual_size(self._fontsize_label_base)
    def _get_title_fontsize(self):
        return self._get_actual_size(self._fontsize_title_base)
    def _get_margin(self):
        mw = self._get_actual_size(self._margin_width_base)
        sof = self._get_axis_standoff()
        xfs = self._get_label_fontsize()
        return dict(l=mw + sof + xfs * 2 + 10, r=mw, t=mw + self._get_title_fontsize(), b=mw + sof)
    def _make_config(self):
        return {'staticPlot' : False, 'toImageButtonOptions' : {'format' : 'svg' }, 'displaylogo' : False, 'responsive' : self._responsive }
    def _make_layout(self, title, x_label, y_label, x_range = [0, None], x_tickformat = '.1f', y_tickformat = 'd', y_range=None, width=None, height=None):
        layout = go.Layout(title = dict(text = title, font=dict(size=self._get_title_fontsize())),
                         font = dict(family = self._font_family),
                         width=width, height=height,
                         margin = self._get_margin(),
                         xaxis= dict(title = dict(text=x_label, font=dict(size=self._get_label_fontsize()), standoff=self._get_axis_standoff()),
                                    tickformat = x_tickformat, ticks = 'outside',
                                    tickcolor = self._axis_color, linecolor = self._axis_color,
                                    tickfont = dict(size=self._get_label_fontsize()),
                                    mirror = True, zeroline = False, showgrid = False, automargin = False,
                                    range = x_range),
                         yaxis=dict(title=dict(text=y_label, font=dict(size=self._get_label_fontsize()), standoff=self._get_axis_standoff()),
                                    tickformat = y_tickformat, ticks = 'outside',
                                    tickcolor = self._axis_color, linecolor = self._axis_color,
                                    tickfont = dict(size=self._get_label_fontsize()),
                                    zeroline = True, zerolinecolor = self._axis_color, zerolinewidth = 0.5,
                                    showline = True, mirror = True, side = 'left',
                                    range = [-1e-6, None] if y_range is None else y_range,
                                    automargin = y_range is not None,
                                    rangemode = 'tozero' if y_range is not None and 0 in y_range else 'normal',
                                    showgrid = False),
                         showlegend = False,
                         template = self._template,
                         hovermode = 'closest', dragmode = 'zoom',
                         modebar = dict(remove = ['pan', 'zoomin', 'zoomout', 'autoscale', 'select', 'lasso']))
        if self._template == 'none':
            layout.paper_bgcolor = "rgba(0,0,0,0)"
            layout.plot_bgcolor = "rgba(0,0,0,0)"
        ###print(f"Layout template={self._template}, {layout.template} pap_bg={layout.paper_bgcolor} plt_bgcolor={layout.plot_bgcolor}")
        return layout

global _current_plotly_settings
_current_plotly_settings = HivePlotlySettings()

def set_default_plot_style(style):
    """Change the default plot style to be applied to all the draw_... methods.

    The `style` argument can be a dictionary used to modify the theme, font family, 
    and layout spacing of the graph. See the `HivePlotlySettings` class for details.

    If the style argument is specified for each draw_... method, then the argument specified for each method takes precedence.
    """
    global _current_plotly_settings
    _current_plotly_settings.set_style(style)

def _find_nearest_index(value_list, target):
    if len(value_list) == 0 or not isinstance(target, (int, float)):
        return None
    return min(range(len(value_list)), key=lambda i: abs(value_list[i] - target))

def _search_highest_index(value_list, threshold, nth_tops=1, skip_intervals=10, allow_negative=False):
    indices = []
    for _ in range(nth_tops):
        idx = None
        max_value = -1
        for i in range(len(value_list)):
            if any(abs(i - checked_idx) < skip_intervals for checked_idx in indices):
                continue
            if (allow_negative and abs(threshold) <= abs(value_list[i]) and abs(value_list[i]) > max_value) or \
                (threshold <= value_list[i] and value_list[i] > max_value):
                max_value = abs(value_list[i])
                idx = i
        if idx is not None:
            indices.append(idx)
    return indices

class HivePlotlyLabels:
    """Definition of annotation labels to be drawn on the plot.

    Definition should be given as a dictionary, or a list of tuples, as a pair of location key and label string.

    Location key must be either a float value of x coordinate, or top-N specification.

    top-N specification := 'top'[n] [/ interval], where n and interval are integer values, and items in [] can be omitted.  
    e.g. top | top5 | top5/20  
    When it is specified, then top n-th peaks are searched and labeled.

    The interval value designates to skip searching from already found peaks.  
    Default interval value is 10 for Chromatogram, and 1 for Spectrogram.

    The label string can contain special notation of {x} and {y}, which will be replaced with actual x- and y-coordinate value.  
    {x} {y} notation can contain additional Python format string after ':'  
    e.g. RT={x:.2f}, Intensity={y:.1e}  
    If label string is ommitted, then '({x:.2f}, {y:.1e})' will be used.

    Annotation label definition dictionary or list of tuples can contain special optional specification:  
    { 'offset' : offset-value }  
    where offset-value is a numeric value specifying the height position offset of the label. Default offset value is 10.
    """
    _RX_TOP = r'^top(\d*)\s*(\/\s*(\d+))?'
    def _parse_as_top_param(self, label_item, auto_label_interval):
        if re.match(self._RX_TOP, label_item, re.IGNORECASE):
            mch = re.match(self._RX_TOP, label_item, re.IGNORECASE)
            self._auto_label = dict(top_n = int(mch.group(1)) if mch.group(1) != '' else 1,
                skip_interval = int(mch.group(3)) if mch.group(3) is not None and mch.group(3) != '' else auto_label_interval, 
                label_format = None)
            return True
        else:
            return False
    def __init__(self, label_def, label_offset = 10, auto_label_interval = 10):
        self._fixed_labels = []
        self._label_offset = label_offset
        self._auto_label = None
        if isinstance(label_def, str):
            self._parse_as_top_param(label_def, auto_label_interval)
        else:
            items = label_def.items() if isinstance(label_def, dict) else label_def
            for item in items:
                if isinstance(item, str):
                    self._parse_as_top_param(item, auto_label_interval)
                elif isinstance(item, tuple) and len(item) == 2:
                    lx, ltext = item
                    #print(f"as tuple: {lx}, {ltext}")
                    if isinstance(lx, (int, float)) and isinstance(ltext, str):
                        self._fixed_labels.append((lx, ltext))
                    elif isinstance(lx, str):
                        if lx.lower() == 'top':
                            #print(f"parse top: {lx}, {ltext}")
                            self._auto_label = dict(top_n = 1, skip_interval = auto_label_interval, label_format = None)
                            if (ltext is None) or (isinstance(ltext, str) and ltext == ''):
                                pass
                            elif isinstance(ltext, int) or (isinstance(ltext, str) and ltext.isdigit()):
                                self._auto_label.update({'top_n': int(ltext) if int(ltext) > 0 else 1})
                            elif isinstance(ltext, dict):
                                for ky, val in ltext.items():
                                    ky = ky.lower()
                                    #print(f"ltext dict key: {ky}, val: {val}")
                                    if 'interval'.startswith(ky):
                                        if (isinstance(val, int) and val > 0):
                                            self._auto_label.update({'skip_interval': val})
                                    elif 'format'.startswith(ky) or 'label'.startswith(ky):
                                        if isinstance(val, str):
                                            self._auto_label.update({'label_format': val})
                                    elif ky == 'n':
                                        if (isinstance(val, int) and val > 0):
                                            self._auto_label.update({'top_n': val})
                                    else:
                                        raise ValueError(f"Unknown top label specification key {ky} in {ltext}")
                            elif isinstance(ltext, str) and ltext != '':
                                self._auto_label.update({'label_format' : ltext})
                            else:
                                raise ValueError(f"invalid top label specification {ltext}, must be dict, integer for top n, or string for label format")
                        elif self._parse_as_top_param(lx, auto_label_interval):
                            if ltext is not None and ltext != '':
                                self._auto_label.update({'label_format' : ltext})
                        elif 'offset'.startswith(lx.lower()):
                            if isinstance(ltext, int) or ltext.isdigit():
                                self._label_offset = int(ltext) 
                            else:
                                raise ValueError(f"Offset value {ltext} must be an integer")
                        else:
                            raise ValueError(f"Unknown label specification, key {lx} should be top or offset")
                    else:
                        raise ValueError(f"Unknown label specification key {lx} must be numeric, 'top' or 'offset'")
                else:
                    raise ValueError(f"Unknown label specification {item}")
        #print(f"Auto label: {self._auto_label}, Fixed labels: {self._fixed_labels} Offset: {self._label_offset}")

    _RX_LABEL_ALLOWED = r'\{(x|y)(:.+?)?\}'
    def _make_label_str(self, format_str, x, y):
        if format_str is None or format_str == '':
            return f'({x:.2f}, {y:.1e})'
        if (0 < format_str.count('{') or 0 < format_str.count('}')):
            rm_fmt_str = re.sub(self._RX_LABEL_ALLOWED, '', format_str)
            if re.search(self._RX_LABEL_ALLOWED, format_str) and rm_fmt_str.count('{') == 0 and rm_fmt_str.count('}') == 0:
                return format_str.format(x=x, y=y)
            else:
                raise NameError(f'Invalid format {format_str}. Only variables x or y are allowed, optionally with Python format string followed by :')
        else:
            return format_str

    def draw_labels(self, figure, plot_styles, x_data, y_data):
        label_items = copy.copy(self._fixed_labels)
        if self._auto_label:
            indices = _search_highest_index(y_data, threshold=1, nth_tops=self._auto_label.get('top_n'), skip_intervals=self._auto_label.get('skip_interval'), allow_negative=True)
            if indices != [None]:
                label_items.extend((x_data[nx], self._auto_label.get('label_format')) for nx in indices if nx is not None)
        ann_list = []
        for lx, ltext in label_items:
            idx = _find_nearest_index(x_data, lx)
            if idx is None:
                continue
            x = x_data[idx]
            y = y_data[idx]
            label = self._make_label_str(ltext, x, y)
            ann = dict(x=x, y=y, text=str(label),
                    showarrow=True, arrowhead=1,
                    ax=0, ay=-self._label_offset,
                    font=dict(size=plot_styles._get_label_fontsize(), color=plot_styles._axis_color),
                    bgcolor='rgba(255,255,255,0.6)' if plot_styles._template != 'plotly_dark' else 'rgba(0,0,0,0.6)',
                    borderpad=3)
            figure.add_annotation(x=ann['x'], y=ann['y'], text=ann['text'], showarrow=ann['showarrow'], arrowhead=ann['arrowhead'],
                    ax=ann['ax'], ay=ann['ay'], font=ann['font'], bgcolor=ann['bgcolor'], borderpad=ann['borderpad'])
            ann_list.append(ann)
        return ann_list

def draw_multiplot(multi_fig, num_col=3, row_height=150, keep_axis_title=False, shared_axis=False, horizontal_space=0.05, _out_writer=None):
    """draw multiple plots in a single figure in trellis layout.

    To use this function, firstly define an empty list as multi_fig,  
    then call draw_...() methods with multiplot=multi_fig argument.  
    Finally, call this function with the multi_fig list.

    `num_column` designates the number of columns in trellis layout.  
    `row_height` designates the height of single row.  
    `keep_axis_title` (boolean) designates the x- and y-axis title of each sub-figure should be kept.  
    `horizonta_space` is a real value between [0, 1] where 1 means the full width of the whole graph, designating the width of the space between columns.  
    `_out_writer` is used internally and should not be specified by users.
    """

    num_figs = len(multi_fig)
    if num_figs == 0:
        return
    num_row = int(math.ceil(num_figs / num_col))
    vertical_space = 0.15 if num_row < 3 else (0.3 / (num_row - 1))
    # `vertical_space` is a real value between [0, 1] where 1 means the full height of the whole graph, designating the height of the space between rows.  
    parent_fig = make_subplots(rows=num_row, cols=num_col, \
        horizontal_spacing=horizontal_space, vertical_spacing=vertical_space, subplot_titles=[multi_fig[i]['title'] for i in range(num_figs)], \
        shared_xaxes=shared_axis, shared_yaxes=shared_axis)
    for ndx in range(num_figs):
        nc = ndx % num_col
        nr = int(math.floor(ndx / num_col))
        subfig = multi_fig[ndx]
        trace = subfig['trace']
        #print(f"trace type={type(trace)} {hasattr(trace, 'y')}")
        if isinstance(trace, list):
            for tr in trace:
                parent_fig.add_trace(tr, row=nr + 1, col=nc + 1)
        else:
            parent_fig.add_trace(trace, row=nr + 1, col=nc + 1) # here caused unexpected keyword Error on specifying showlegend=False;
        layout = subfig['layout']
        #print(f"Title: {layout.title.text} ndx={ndx} nr={nr} nc={nc}")
        if keep_axis_title:
            parent_fig.update_xaxes(layout.xaxis, row=nr+1, col=nc+1)
            parent_fig.update_yaxes(layout.yaxis, row=nr+1, col=nc+1)
        else:
            parent_fig.update_xaxes(layout.xaxis, title_text='', row=nr+1, col=nc+1)
            parent_fig.update_yaxes(layout.yaxis, title_text='', row=nr+1, col=nc+1)
        if hasattr(layout, 'annotations'):
            for ann in layout.annotations:
                new_ann = dict(ann)
                new_ann.update({ 'xref': f'x{nc+1}', 'yref': f'y{nr+1}' })
                parent_fig.add_annotation(new_ann)
        if ndx == 0:
            parent_fig.update_layout(font=layout.font, margin=layout.margin, template=layout.template, hovermode=layout.hovermode, dragmode=layout.dragmode, modebar=layout.modebar)
            config = multi_fig[ndx]['config']
    ## Ensure no trace creates legend entries (some trace types like heatmap can still cause legend-like entries depending on their settings).
    ## Force all traces to not appear in legend before showing the figure.
    parent_fig.update_traces(showlegend=False) ## even added this according to GitHub copilot, but still not eliminaated the legend of heatmap;
    parent_fig.update_layout(height=row_height * num_row, showlegend=False)
    global _current_plotly_settings
    if _out_writer is not None:
        if _out_writer._env == "jupyter" and layout is not None and layout.paper_bgcolor is not None and layout.plot_bgcolor is not None:
            ## when set_default_plot_style is not explicitly called with template, should set parent_fig's bgcolor to transparent,
            ## though subgraph layout's bgcolors would be set to transparent already.
            parent_fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        if not _out_writer.draw_fig(parent_fig,  height=row_height * num_row):
            if not _current_plotly_settings._auto_theme:
                parent_fig.show(config=config)
            else:
                ap.show_adaptive(parent_fig, config=config)
    else:
        if not _current_plotly_settings._auto_theme:
            parent_fig.show(config=config)
        else:
            ap.show_adaptive(parent_fig, config=config)

def draw_chromatogram(quan_chrom, title=None, x_label='Minutes', y_label='Absolute Intensity', style=None, labels=None, color=None, multiplot=None, allow_negative_intensity=False, width=None, height=None, _out_writer=None):
    """Draw a chromatogram from a QuanAnalysis, AnalogAnalysis, or a list of 
    ChromatogramPoint/SpectrumBasedChromatogramPoint objects.

    The first argument, `quan_chrom`, should be either a `QuanAnalysis` or `AnalogAnalysis` object, 
    or a list of `ChromatogramPoint` instances.

    If `title` is specified, it will be displayed as the graph title.
    If omitted and the first argument is a `QuanAnalysis` or `AnalogAnalysis`, 
    an appropriate title will be automatically assigned.

    `x_label` and `y_label` specify the axis titles as strings. 
    If omitted and the first argument is a `QuanAnalysis` or `AnalogAnalysis`, 
    appropriate labels will be automatically assigned.

    The `style` argument can be a dictionary used to modify the theme, font family, 
    and layout spacing of the graph. See the `HivePlotlySettings` class for details.

    The `labels` argument can also be a dictionary used to draw labels on the graph. 
    Typical examples include:  
        `dict(top=dict(n=5, format='{x:.2f}, {y:.1e}'))`   
    which marks the top 5 most intense peaks with the specified format.
    The `format` value must be a valid Python format string.
    See the `HivePlotlyLabels` class for more information.

    The graph color can be specified using the `color` argument as a string.
    It must be a valid Python color specification.

    If `multiplot` is provided, drawing will be deferred, and the graph data will be 
    stored in the specified list to be rendered later by `draw_multiplot()`.

    `allow_negative_intensity` is a boolean value indicating whether negative intensity 
    values should be plotted.

    `width` and `height` specify the dimensions of the graph in pixels.

    `_out_writer` is used internally and should not be specified by users.
    """

    global _current_plotly_settings
    plot_styles = copy.copy(_current_plotly_settings)
    if style:
        plot_styles.set_style(style)

    y_range = [None, None] if allow_negative_intensity else None
    y_tickformat = 'd'
    if isinstance(quan_chrom, (hive_data_access.quan.QuanAnalysis, hive_data_access.quan.AnalogAnalysis)):
        if title is None:
            if (isinstance(quan_chrom, hive_data_access.quan.QuanAnalysis)):
                if quan_chrom.extract_value:
                    title = f"{quan_chrom.compound_name} ({quan_chrom.extract_value:.2f})"
                elif quan_chrom.q1 and quan_chrom.q3:
                    title = f"{quan_chrom.compound_name} ({quan_chrom.q1:.2f}>{quan_chrom.q3:.2f})"
                else:
                    title = quan_chrom.compound_name
            elif (isinstance(quan_chrom, hive_data_access.quan.AnalogAnalysis)):
                title = quan_chrom.description
                y_range = [None, None]
                y_tickformat = '.2f'
        points = quan_chrom.chromatogram_points
    elif isinstance(quan_chrom, list) and 0 < len(quan_chrom) and isinstance(quan_chrom[0], (hive_data_access.common.ChromatogramPoint, hive_data_access.common.SpectrumBasedChromatogramPoint)):
        points = quan_chrom

    rt_list = [points[i].retention_time for i in range(len(points))]
    intensity_list = [points[i].intensity for i in range(len(points))]
    if color is not None:
        data = [go.Scatter(x = rt_list, y = intensity_list, line=dict(color=color))]
    else:
        data = [go.Scatter(x = rt_list, y = intensity_list)]
    layout = plot_styles._make_layout(title, x_label, y_label, x_range=[0, 10] if len(rt_list) == 0 else [rt_list[0], rt_list[-1]], \
        y_range=y_range, y_tickformat=y_tickformat, width=width, height=height)
    config = plot_styles._make_config()
    fig = go.Figure(data, layout)

    # labels: dict{x: text} or list of (x, text); see HivePlotlyLabels;
    label_annot = None
    if labels:
        label_def = HivePlotlyLabels(labels, label_offset=10, auto_label_interval=max(10, int(len(rt_list)/40)))
        label_annot = label_def.draw_labels(fig, plot_styles, rt_list, intensity_list)
    if multiplot is not None:
        if label_annot:
            # instead of assigning to multiplot dict as annotation, inserted labels within data traces
            for ann in label_annot:
                data.append(go.Scatter(x=[ann['x']], y=[ann['y']], mode='text', text=[ann['text']], textposition='bottom center',
                    showlegend=False, hoverinfo='skip')) # unable to set font and bgcolor here, but seems acceptable
        if len(multiplot) == 0:
            multiplot.append(dict(trace=data, title=title, layout=layout, config=config))
        else:
            multiplot.append(dict(trace=data, title=title, layout=layout))
    else:
        if _out_writer is not None:
            if not _out_writer.draw_fig(fig, width=width, height=height):
                if not plot_styles._auto_theme:
                    fig.show(config = config)
                else:
                    ap.show_adaptive(fig, config=config)
        else:
            if not plot_styles._auto_theme:
                fig.show(config = config)
            else:
                ap.show_adaptive(fig, config=config)

def draw_overlaid_chromatogram(quan_chrom_list, title = None, x_label = 'Minutes', y_label = 'Absolute Intensity', style = None, colors=None, multiplot=None, allow_negative_intensity=False, width=None, height=None, _out_writer=None):
    """Draw overlaid chromatograms from a list of QuanAnalysis, AnalogAnalysis, or a list of lists of
    ChromatogramPoint/SpectrumBasedChromatogramPoint objects.

    The first argument, `quan_chrom_list`, should be eithr a list of `QuanAnalysis` or `AnalogAnalysis` objects, or a list of lists of
    ChromatogramPoint/SpectrumBasedChromatogramPoint instances.

    `title`, `x_label` and `y_label` specify the graph title and axis titles as strings.
    No automatic assignment will be performed even the first argument contains QuanAnalys or AnalogAnalysis.

    The `style` argument can be a dictionary used to modify the theme, font family, 
    and layout spacing of the graph. See the `HivePlotlySettings` class for details.

    `labels` option is not supported in this function.

    The graph colors can be specified using the `colors` argument as a list of strings.
    They must be valid Python color specification.
    
    If `multiplot` is provided, drawing will be deferred, and the graph data will be 
    stored in the specified list to be rendered later by `draw_multiplot()`.

    `allow_negative_intensity` is a boolean value indicating whether negative intensity 
    values should be plotted.

    `width` and `height` specify the dimensions of the graph in pixels.

    `_out_writer` is used internally and should not be specified by users.
    """

    global _current_plotly_settings
    plot_styles = copy.copy(_current_plotly_settings)
    if style:
        plot_styles.set_style(style)

    data = []
    rt_min = None
    rt_max = None
    for i in range(len(quan_chrom_list)):
        if isinstance(quan_chrom_list[i], (hive_data_access.quan.QuanAnalysis, hive_data_access.quan.AnalogAnalysis)):
            rt_list = [quan_chrom_list[i].chromatogram_points[j].retention_time for j in range(len(quan_chrom_list[i].chromatogram_points))]
            intensity_list = [quan_chrom_list[i].chromatogram_points[j].intensity for j in range(len(quan_chrom_list[i].chromatogram_points))]
        elif isinstance(quan_chrom_list[i], list) and 0 < len(quan_chrom_list[i]) and isinstance(quan_chrom_list[i][0], (hive_data_access.common.ChromatogramPoint, hive_data_access.common.SpectrumBasedChromatogramPoint)):
            rt_list = [quan_chrom_list[i][j].retention_time for j in range(len(quan_chrom_list[i]))]
            intensity_list = [quan_chrom_list[i][j].intensity for j in range(len(quan_chrom_list[i]))]
        if isinstance(colors, list) and 0 < len(colors):
            d = go.Scatter(x = rt_list, y = intensity_list, line=dict(color=colors[i % len(colors)]))
        else:
            d = go.Scatter(x = rt_list, y = intensity_list)
        data.append(d)
        if rt_min is None or rt_list[0] < rt_min:
            rt_min = rt_list[0]
        if rt_max is None or rt_max < rt_list[-1]:
            rt_max = rt_list[-1]
    layout = plot_styles._make_layout(title, x_label, y_label, x_range=[rt_min, rt_max], y_range=[None, None] if allow_negative_intensity else None, width=width, height=height)
    config = plot_styles._make_config()
    fig = go.Figure(data, layout)
    if multiplot is not None:
        if len(multiplot) == 0:
            multiplot.append(dict(trace=data, title=title, layout=layout, config=config))
        else:
            multiplot.append(dict(trace=data, title=title, layout=layout))
    else:
        if _out_writer is not None:
            if not _out_writer.draw_fig(fig, width=width, height=height):
                if not plot_styles._auto_theme:
                    fig.show(config = config)
                else:
                    ap.show_adaptive(fig, config=config)
        else:
            if not plot_styles._auto_theme:
                fig.show(config = config)
            else:
                ap.show_adaptive(fig, config=config)

def draw_spectrum(points, title = None, x_label = 'm/z', y_label = 'Absolute Intensity', style = '', labels=None, color=None, multiplot=None, relative_intensity_cutoff=1e-3, allow_negative_intensity = False, width=None, height=None, _out_writer=None):
    """Draw spectrogram from a Spectrum or a DADSpectrum object.

    The first argument `points` should be a Spectrum or DADSpectrum object.

    If `title` is specified, it will be displayed as the graph title. 

    `x_label` and `y_label` specify the axis titles as strings. 
    If omitted, appropriate labels will be automatically assigned.

    The `style` argument can be a dictionary used to modify the theme, font family, 
    and layout spacing of the graph. See the `HivePlotlySettings` class for details.

    The `labels` argument can also be a dictionary used to draw labels on the graph. 
    Typical examples include:  
        `dict(top=dict(n=5, format='{x:.2f}, {y:.1e}'))`   
    which marks the top 5 most intense peaks with the specified format.
    The `format` value must be a valid Python format string.
    See the `HivePlotlyLabels` class for more information.

    The graph color can be specified using the `color` argument as a string.
    It must be a valid Python color specification.

    If `multiplot` is provided, drawing will be deferred, and the graph data will be 
    stored in the specified list to be rendered later by `draw_multiplot()`.

    If `relative_intensity_cutoff` is given, then points with abs(intensity) lower than (max intensity * relative_intensity_cutoff) will be ignored.

    `allow_negative_intensity` is a boolean value indicating whether negative intensity values should be plotted.

    `width` and `height` specify the dimensions of the graph in pixels.

    `_out_writer` is used internally and should not be specified by users.
    """

    global _current_plotly_settings
    plot_styles = copy.copy(_current_plotly_settings)
    if style:
        plot_styles.set_style(style)
    
    if isinstance(points, (hive_data_access.qual.Spectrum, hive_data_access.qual.DADSpectrum)):
        if isinstance(points, hive_data_access.qual.DADSpectrum):
            if x_label == 'm/z':
                x_label = 'Wavelength'
            if y_label == 'Absolute Intensity':
                y_label = 'Absorbance'
            allow_negative_intensity = True
        points = points.get_spectrum_points()

    if color is None:
        color = plcolors.DEFAULT_PLOTLY_COLORS[0]
    # (below) original implementation causing very slow rendering for large number of points
    # x_list = [points[i].x for i in range(len(points))]
    # intensity_list = [points[i].intensity for i in range(len(points))]
    min_x, max_x = (None, None)
    if 0 < len(points):
        min_x, max_x = points[0].x, points[-1].x
        x_width = max_x - min_x
        #print(f"min_x={min_x} max_x={max_x} x_width={x_width}")
        if 0 < x_width:
            min_x -= x_width * 0.01
            max_x += x_width * 0.01;
        #print(f"adjusted min_x={min_x} max_x={max_x}")
    x_list = []; intensity_list = []
    max_intns = max(abs(points[i].intensity) for i in range(len(points))) if 0 < len(points) else 0
    cutoff_abs_intns = max_intns * relative_intensity_cutoff
    #print(f"max_intns={max_intns} cutoff={cutoff_abs_intns}")

    min_y, max_y = (0, 0)
    for i in range(len(points)):
        if abs(points[i].intensity) < cutoff_abs_intns:
            continue
        x_list.append(points[i].x)
        intensity_list.append(points[i].intensity)
        if max_y < points[i].intensity:
            max_y = points[i].intensity
        if allow_negative_intensity and points[i].intensity < min_y:
            min_y = points[i].intensity
    #print(f"y min, max = {min_y}, {max_y}")
    if min_y < 0:
        y_width = max_y - min_y
        if 0 < max_y:
            max_y += y_width * 0.08
        min_y -= y_width * 0.01
    else:
        max_y *= 1.08
    #print(f"adjusted y min, max = {min_y}, {max_y}")
    #data = go.Scatter(x = x_list, y = intensity_list, mode = 'markers', marker_opacity = 0) # original implementation
    data = [go.Scatter(x = [x_list[i], x_list[i]], y = [0, intensity_list[i]], mode='lines', line=dict(color=color), hoverinfo='none') for i in range(len(x_list))]
    data.append(go.Scatter(x = x_list, y = intensity_list, mode = 'markers', marker_opacity = 0)) # to enable hoverinfo on peaks
    layout = plot_styles._make_layout(title, x_label, y_label, x_range=[min_x, max_x], y_range=[min_y, max_y], x_tickformat='d', width=width, height=height)
    config = plot_styles._make_config()
    fig = go.Figure(data, layout)
    # (below) original implementation is no longer used for already drawn lines above
    # for i in range(len(x_list)):
    #     #fig.add_shape(type = 'line', x0 = x_list[i], y0 = 0, x1 = x_list[i], y1 = intensity_list[i], line=dict(color=color))
    #     fig.add_trace(go.Scatter(x = [x_list[i], x_list[i]], y = [0, intensity_list[i]], mode='lines', line=dict(color=color)))

    # labels: dict{x: text} or list of (x, text); See HivePlotlyLabels
    label_annot = None
    if labels:
        label_def = HivePlotlyLabels(labels, label_offset=10, auto_label_interval=1)
        label_annot = label_def.draw_labels(fig, plot_styles, x_list, intensity_list)
    if multiplot is not None:
        if label_annot:
            # instead of assigning to multiplot dict as annotation, inserted labels within data traces
            for ann in label_annot:
                data.append(go.Scatter(x=[ann['x']], y=[ann['y']], mode='text', text=[ann['text']], textposition='top center',
                    showlegend=False, hoverinfo='skip')) # unable to set font and bgcolor here, but seems acceptable
        if len(multiplot) == 0:
            multiplot.append(dict(trace=data, title=title, layout=layout, config=config))
        else:
            multiplot.append(dict(trace=data, title=title, layout=layout))
    else:
        if _out_writer is not None:
            if not _out_writer.draw_fig(fig, width=width, height=height):
                if not plot_styles._auto_theme:
                    fig.show(config = config)
                else:
                    ap.show_adaptive(fig, config=config)
        else:
            if not plot_styles._auto_theme:
                fig.show(config = config)
            else:
                ap.show_adaptive(fig, config=config)

def draw_spectra_map(qual_or_Spectra, acquisiiton_condition = None, title = None, x_label = 'RT', y_label = "m/z", style = '', x_resolution=0.01, y_resolution=1.0, multiplot=None, width=None, height=None, _out_writer=None):
    """Draw heatmap of whole spectra from QualAnalysis, DADAnalysis, or list of Spectrum/DADSpectrum objects.

    The first argument, `qual_or_spectra`, should be either a `QualAnalysis` or `DADAnalysis` object, or a list of `Spectrum` or `DADSpectrum` instances.

    `title`, `x_label` and `y_label` specify the graph title and axis titles as strings.

    The `style` argument can be a dictionary used to modify the theme, font family, 
    and layout spacing of the graph. See the `HivePlotlySettings` class for details.

    Heatmap's unit lattice size can be specified with `x_resolution` and `y_resolution` parameters.
    
    If `multiplot` is provided, drawing will be deferred, and the graph data will be 
    stored in the specified list to be rendered later by `draw_multiplot()`.

    `width` and `height` specify the dimensions of the graph in pixels.

    `_out_writer` is used internally and should not be specified by users.
    """
    global _current_plotly_settings
    plot_styles = copy.copy(_current_plotly_settings)
    if style:
        plot_styles.set_style(style)

    if isinstance(qual_or_Spectra, (hive_data_access.qual.QualAnalysis, hive_data_access.qual.DADAnalysis)):
        if isinstance(qual_or_Spectra, hive_data_access.qual.DADAnalysis):
            if y_label == "m/z":
                y_label = "Wavelength"
            qual_or_Spectra = [qual_or_Spectra.get_spectrum(sn) for sn in range(qual_or_Spectra.get_spectra_count())]
        else: # for QualAnalysis, acquisition_condition specification is mandatory;
            if (acquisiiton_condition is None or not (isinstance(acquisiiton_condition, hive_data_access.qual.AcquisitionCondition))):
                raise TypeError("Missing acquisition_condition argument for QualAnalysis")
            spctlist = []
            for sn in range(qual_or_Spectra.get_spectra_count()):
                spct = qual_or_Spectra.get_spectrum(sn)
                if (spct.acquisition_condition == acquisiiton_condition):
                    spctlist.append(spct)
            qual_or_Spectra = spctlist

    if isinstance(qual_or_Spectra, list) and 0 < len(qual_or_Spectra) and isinstance(qual_or_Spectra[0], (hive_data_access.qual.Spectrum, hive_data_access.qual.DADSpectrum)):
        pass
    else:
        return

    #region prep. map data
    min_x = 99999; max_x = -99999
    min_z = math.inf; max_z = -math.inf
    x_dict = {}
    tmp_spect_buf = {}
    for spct in qual_or_Spectra:
        spectrum = spct.get_spectrum_points()
        nrm_t = round(spct.retention_time / x_resolution) * x_resolution
        dic = tmp_spect_buf[nrm_t] if 0 < len(tmp_spect_buf) and nrm_t in tmp_spect_buf else {}
        for spct in spectrum:
            spx = spct.x
            spint = spct.intensity
            nrm_x = round(spx / y_resolution) * y_resolution
            if nrm_x in dic:
                if abs(dic[nrm_x]) < abs(spint):
                    dic[nrm_x] = spint
            else:
                dic[nrm_x] = spint
            if nrm_x < min_x:
                min_x = nrm_x
            if max_x < nrm_x:
                max_x = nrm_x
            if nrm_x not in x_dict:
                x_dict[nrm_x] = 1
        tmp_spect_buf[nrm_t] = dic
    list_t = [x for x in tmp_spect_buf.keys()]
    list_x = list(x_dict.keys())
    list_x.sort()
    #print(f"min_x={min_x} max_x={max_x}")
    map_intns = np.zeros((len(list_x) + 1, len(list_t) + 1))
    for ndx_x, rt in enumerate(list_t):
        spct = tmp_spect_buf[rt]
        for spx, spint in spct.items():
            ndx_y = list_x.index(spx)
            if abs(map_intns[ndx_y, ndx_x]) < abs(spint):
                map_intns[ndx_y, ndx_x] = spint
            if max_z < spint:
                max_z = spint
            if spint < min_z:
                min_z = spint
    #print(f"min_z={min_z} max_z={max_z}")

    # adjust color scale range
    if min_z < 0:
        if -min_z < max_z:
            min_z = -max_z
        else:
            max_z = -min_z
    else:
        min_z = 0
    #endregion prep. map data

    #region prepare color scale
    # print(f"style template: {plot_styles._template} explicit: {plot_styles._explicit_template}")
    if 'dark' in plot_styles._template:
        colorscale = [
            [0.0, "cyan"], # negative max
            [0.4, "blue"],
            [0.5, "black"], # center, 0 value
            [0.6, "red"],
            [1.0, "magenta"], # positive max
        ] if min_z < 0 else [
            [0.0, "black"], # min, 0 value
            [0.05, "blue"],
            [0.2, "limegreen"],
            [0.5, "yellow"],
            [1.0, "red"], # max
        ]
    else:
        colorscale = [
            [0.0, "blue"], # negative max
            [0.4, "cyan"],
            [0.5, "white"], # center, 0 value
            [0.6, "limegreen"],
            [1.0, "red"], # positive max
        ] if min_z < 0 else [
            [0.0, "white"], # min, 0 value
            [0.05, "cyan"],
            [0.2, "limegreen"],
            [0.5, "yellow"],
            [1.0, "red"], # max
        ]
    #endregion prepare color scale

    data = go.Heatmap(x = list_t, y = list_x, z = map_intns,
        colorscale = colorscale,
        zmin=min_z, zmax=max_z,
        colorbar=None if multiplot is None else dict(title='Intensity'),
        showlegend = not (multiplot is None))
    layout = plot_styles._make_layout(title, x_label, y_label, x_range=[None, None], y_range=[None, None], x_tickformat='.1f', y_tickformat='.1f', width=width, height=height)
    config = plot_styles._make_config()
    fig = go.Figure(data, layout)
    if multiplot is not None:
        if len(multiplot) == 0:
            multiplot.append(dict(trace=data, title=title, layout=layout, config=config))
        else:
            multiplot.append(dict(trace=data, title=title, layout=layout))
    else:
        if _out_writer is not None:
            if not _out_writer.draw_fig(fig, width=width, height=height):
                if not plot_styles._auto_theme:
                    fig.show(config = config)
                else:
                    ap.show_adaptive(fig, config=config)
        else:
            if not plot_styles._auto_theme:
                fig.show(config = config)
            else:
                ap.show_adaptive(fig, config=config)

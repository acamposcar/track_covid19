from math import pi

from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, BasicTickFormatter, HoverTool, DatetimeTickFormatter
from bokeh.plotting import figure

curdoc().theme = 'dark_minimal'
daysRange = 50


def country_graph(df, countryCode, x, y, color_bar, color_line):

    # Daily Bar Graph
    hover = HoverTool(tooltips=[("Date", "@" + x + "{%d-%b}"), (y.capitalize(), "@" + y)],
                      formatters={"@" + x: 'datetime'})
    p_daily = figure(title=f'{y.capitalize()} - Daily change', plot_height=350, sizing_mode='scale_width',
                    x_axis_type='datetime', toolbar_location=None, tools=[hover])
    p_daily.xaxis.formatter = DatetimeTickFormatter(days='%d-%b', months='%d-%b',
                                                   hours='%d-%b', minutes='%d-%b')
    p_daily.vbar(x=x, top=y, source=ColumnDataSource(df[-daysRange:]), line_width=6, color=color_bar, alpha=0.7)
    p_daily.line(x=x, y=f'{y}MovingAverage', source=ColumnDataSource(df[-daysRange:]), line_width=3, color=color_line,
                legend_label="7-day average", alpha=0.9)
    p_daily.legend.location = "top_left"
    p_daily.legend.background_fill_alpha = 0
    p_daily.xaxis.major_label_orientation = pi / 4
    p_daily.xgrid.grid_line_color = None
    p_daily.outline_line_color = None
    p_daily.background_fill_alpha = 0
    p_daily.border_fill_alpha = 0
    p_daily.title.text_font = 'helvetica'
    p_daily.title.text_font_style = 'normal'
    p_daily.title.align = "center"
    # Accumulated Line Graph

    hover = HoverTool(tooltips=[("Date", "@" + x + "{%d-%b}"), (y.capitalize(), "@" + y)],
                      formatters={"@" + x: 'datetime'})
    p_accum = figure(title=f'{y.capitalize()} - Total (log scale)', plot_height=350, sizing_mode='scale_width',
                    y_axis_type="log", x_axis_type='datetime', toolbar_location=None, tools=[hover])
    p_accum.yaxis.formatter = BasicTickFormatter(use_scientific=False)
    p_accum.xaxis.formatter = DatetimeTickFormatter(days='%d-%b', months='%d-%b',
                                                   hours='%d-%b', minutes='%d-%b')
    p_accum.line(x=x, y=f'{y}Accum', source=ColumnDataSource(df[-daysRange:]), line_width=4, color=color_bar, alpha=0.8)
    p_accum.xaxis.major_label_orientation = pi / 4
    p_accum.background_fill_alpha = 0
    p_accum.border_fill_alpha = 0
    p_accum.xgrid.grid_line_color = None
    p_accum.outline_line_color = None
    p_accum.title.text_font = 'helvetica'
    p_accum.title.text_font_style = 'normal'
    p_accum.title.align = "center"
    return p_daily, p_accum


def world_graph(df, x, y, color_bar, color_line):
    # Filter Country Data
    df = df.groupby(by='dateRep').sum()
    df[f'{y}MovingAverage'] = df[y].rolling(window=7).mean()
    # Daily Bar Graph
    hover = HoverTool(tooltips=[("Date", "@" + x + "{%d-%b}"), (y.capitalize(), "@" + y)],
                      formatters={"@" + x: 'datetime'})
    fig_bar = figure(title=f'Global {y.capitalize()} - Daily Change', plot_height=350, sizing_mode='scale_width',
                     x_axis_type='datetime', toolbar_location=None, tools=[hover])
    fig_bar.xaxis.formatter = DatetimeTickFormatter(days='%d-%b', months='%d-%b',
                                                    hours='%d-%b', minutes='%d-%b')
    fig_bar.vbar(x=x, top=y, source=ColumnDataSource(df[-daysRange:]), line_width=6, color=color_bar, alpha=0.7)
    fig_bar.line(x=x, y=f'{y}MovingAverage', source=ColumnDataSource(df[-daysRange:]), line_width=4, color=color_line,
                 legend_label="7-day average", alpha=0.8)
    fig_bar.title.text_font = 'helvetica'
    fig_bar.title.text_font_style = 'normal'
    fig_bar.title.align = "center"
    fig_bar.legend.location = "top_left"
    fig_bar.legend.background_fill_alpha = 0
    fig_bar.xaxis.major_label_orientation = pi / 4
    fig_bar.background_fill_alpha = 0
    fig_bar.border_fill_alpha = 0
    fig_bar.xgrid.grid_line_color = None
    fig_bar.outline_line_color = None

    return fig_bar

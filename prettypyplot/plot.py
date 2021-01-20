"""Wrapper for matplotlib plotting functions.

BSD 3-Clause License
Copyright (c) 2020, Daniel Nagel
All rights reserved.

"""
# ~~~ IMPORT ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import warnings
from os import path

import matplotlib as mpl  # mpl = dm.tryImport('matplotlib')
from matplotlib import legend as mlegend
from matplotlib import pyplot as plt
from mpl_toolkits import axes_grid1 as mpl_axes_grid1

from prettypyplot import tools
from prettypyplot.style import __MODE, __STYLE


# ~~~ FUNCTIONS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def imshow(*args, ax=None, **kwargs):
    """Display an image, i.e. data on a 2D regular raster.

    This is a wrapper of pyplot.imshow(). In contrast to the original function
    the default value of `zorder` is increased to `1`.

    Parameters
    ----------
    ax : matplotlib axes, optional
        Matplotlib axes to plot in.

    args, kwargs
        See [pyplot.imshow()](MPL_DOC.pyplot.imshow.html)

    """
    args, ax = tools.parse_axes(*args, ax=ax)

    if 'zorder' not in kwargs:
        kwargs['zorder'] = 1

    # plot
    return ax.imshow(*args, **kwargs)


def plot(*args, ax=None, **kwargs):
    """Plot simple lineplot.

    Wrapping pyplot.plot() to adjust to style. For more information on the
    arguments see in matplotlib documentation.
    If STYLE='minimal', spines will be limited to plotting range.

    Parameters
    ----------
    ax : matplotlib axes
        Matplotlib axes to plot in.

    args, kwargs
        See [pyplot.plot()](MPL_DOC.pyplot.plot.html)

    """
    # parse axes
    args, ax = tools.parse_axes(*args, ax=ax)

    # plot
    axes = ax.plot(*args, **kwargs)

    if __STYLE == 'minimal':
        # TODO: change this to function
        xminmax = _xminmax(ax)
        xticks = ax.get_xticks()
        if xticks.size:
            ax.spines['bottom'].set_bounds(xminmax[0], xminmax[1])
            ax.spines['top'].set_bounds(xminmax[0], xminmax[1])
            # firsttick = np.compress(xticks >= min(ax.get_xlim()), xticks)[0]
            # lasttick = np.compress(xticks <= max(ax.get_xlim()), xticks)[-1]
            # ax.spines['bottom'].set_bounds(firsttick, lasttick)
            # ax.spines['top'].set_bounds(firsttick, lasttick)
            # newticks = xticks.compress(xticks <= lasttick)
            # newticks = newticks.compress(newticks >= firsttick)
            # ax.set_xticks(newticks)

        yminmax = _yminmax(ax)
        yticks = ax.get_yticks()
        if yticks.size:
            ax.spines['left'].set_bounds(yminmax[0], yminmax[1])
            ax.spines['right'].set_bounds(yminmax[0], yminmax[1])
            # firsttick = np.compress(yticks >= min(ax.get_ylim()), yticks)[0]
            # lasttick = np.compress(yticks <= max(ax.get_ylim()), yticks)[-1]
            # ax_i.spines['left'].set_bounds(firsttick, lasttick)
            # ax_i.spines['right'].set_bounds(firsttick, lasttick)
            # newticks = yticks.compress(yticks <= lasttick)
            # newticks = newticks.compress(newticks >= firsttick)
            # ax.set_yticks(newticks)

    return axes


def savefig(fname, use_canvas_size=True, **kwargs):
    """Save figure as png and pdf.

    This methods corrects figsize for poster/beamer mode.

    Parameters
    ----------
    fname : str
        Output filename. If no file ending, pdf will be used.

    use_canvas_size : bool, optional
        If True the specified figsize will be used as canvas size.

    kwargs
        See [pyplot.savefig()](MPL_DOC.pyplot.savefig.html)

    """
    fig = plt.gcf()
    ax = fig.get_axes()[0]
    figsize = fig.get_size_inches()

    set_figsize = figsize

    if __STYLE == 'minimal':
        # reduce number of ticks by factor 1.5 if more than 4
        tick_reduc = 1.5
        for axes in plt.gcf().get_axes():
            if len(axes.get_xticks()) > 4:
                axes.locator_params(
                    tight=False,
                    axis='x',
                    nbins=len(axes.get_xticks()) / tick_reduc,
                )
            if len(axes.get_yticks()) > 4:
                axes.locator_params(
                    tight=False,
                    axis='y',
                    nbins=len(axes.get_yticks()) / tick_reduc,
                )

    if __MODE == 'poster':
        fig.set_size_inches(
            (3 * figsize[0], 3 * figsize[1]),
        )
    elif __MODE == 'beamer':
        fig.set_size_inches(
            (3 * figsize[0], 3 * figsize[1]),
        )

    with warnings.catch_warnings():
        warnings.filterwarnings('ignore')
        fig.tight_layout()

    # convert figsize to canvas size
    if use_canvas_size:
        x0, y0, width, height = ax.get_position().bounds
        figsize = (figsize[0] / width, figsize[1] / height)
        fig.set_size_inches(figsize)

    # save as pdf if not specified
    if 'format' not in kwargs:
        if path.splitext(fname)[1][1:] == '':
            fname = '{0}.pdf'.format(fname)

    # save fig
    plt.savefig(fname, **kwargs)

    # reset figsize, if user calls this function multiple times on same figure
    fig.set_size_inches(set_figsize)


def legend(*args, outside=False, ax=None, axs=None, **kwargs):
    """Generate a nice legend.

    This is a wrapper of pyplot.legend(). Take a look there for the default
    arguments and options. The ticks and labels are moved to the opposite side.
    For `top` and `bottom` the default value of columns is set to the number of
    labels, for all other options to 1. In case of many labels this parameter
    needs to be adjusted.

    .. todo::
        Use handles and labels from *args if provided

    Parameters
    ----------
    outside : str or bool
        False, 'top', 'right', 'bottom' or 'left'.

    axs : list of mpl.axes.Axes
        List of axes which are used for extracting all labels.

    ax : mpl.axes.Axes
        Axes which is used for placing legend.

    args, kwargs
        See [pyplot.legend()](MPL_DOC.pyplot.legend.html)

    Returns
    -------
    leg
        Matplotlib legend handle.

    Examples
    --------
    .. include:: ../gallery/legend/README.md

    """
    if outside not in {False, 'top', 'right', 'left', 'bottom'}:
        raise ValueError(
            'Use for outside one of [False, "top", "right", "left", "bottom"]',
        )

    # parse axes
    args, ax = tools.parse_axes(*args, ax=ax)

    # parse axs
    if axs is None:
        axs = [ax]
    elif not all((isinstance(arg, mpl.axes.Axes) for arg in axs)):
        raise TypeError('axs needs to be of type matplotlib.axes.Axes.')

    # shift axis to opposite side.
    if outside:
        activate_axis(_opposite_side(outside))

    # set anchor, mode and location
    if outside == 'top':
        kwargs.setdefault('bbox_to_anchor', (0.0, 1.0, 1.0, 0.01))
        kwargs.setdefault('mode', 'expand')
        kwargs.setdefault('loc', 'lower left')
    elif outside == 'bottom':
        kwargs.setdefault('bbox_to_anchor', (0.0, 0.0, 1.0, 0.01))
        kwargs.setdefault('mode', 'expand')
        kwargs.setdefault('loc', 'upper left')
    elif outside == 'right':
        kwargs.setdefault('bbox_to_anchor', (1.03, 0.5))
        kwargs.setdefault('loc', 'center left')
    elif outside == 'left':
        kwargs.setdefault('bbox_to_anchor', (-0.03, 0.5))
        kwargs.setdefault('loc', 'center right')

    # get handles and labels of selected axes
    handles, labels = mlegend._get_legend_handles_labels(axs)

    # set number of ncol to the number of items
    if outside in {'top', 'bottom'}:
        kwargs.setdefault('ncol', len(labels))

    # generate legend
    leg = ax.legend(handles, labels, *args, **kwargs)
    if __STYLE == 'minimal':
        leg.get_frame().set_linewidth(0.0)
    elif __STYLE == 'default':
        leg.get_frame().set_linewidth(plt.rcParams['axes.linewidth'])

    # shift title to the left if on top or bottom
    # taken from: https://stackoverflow.com/a/53329898
    if outside in {'top', 'bottom'}:
        child = leg.get_children()[0]
        title = child.get_children()[0]
        hpack = child.get_children()[1]
        child._children = [hpack]
        hpack._children = [title] + hpack.get_children()

    return leg


def _opposite_side(pos):
    """Return opposite of 'top', 'bottom', 'left', 'right'."""
    if pos == 'top':
        return 'bottom'
    elif pos == 'bottom':
        return 'top'
    elif pos == 'right':
        return 'left'
    elif pos == 'left':
        return 'right'
    raise ValueError('Only "top", "bottom", "left", "right" are accepted.')


def activate_axis(position, ax=None):
    """Shift the specified axis to the opposite side.

    Parameters
    ----------
    position : str or list of str
        Specify axis to flip, one of ['left', 'right', 'top', 'bottom'].

    ax : matplotlib axes
        Matplotlib axes to flip axis.

    """
    # get axes
    ax = tools.gca(ax)

    # convert string to list of strings
    if isinstance(position, str):
        position = [position]

    # allowed values
    positions = {'bottom', 'top', 'left', 'right'}

    # move axes ticks and labels to opposite side of position
    for pos in position:
        if pos not in positions:
            raise ValueError(
                '{0:!r} is not a valid value for {1}; supported values are {2}'
                .format(pos, 'position', ', '.join(positions))
            )

        if pos in {'bottom', 'top'}:
            axis = ax.xaxis
        elif pos in {'left', 'right'}:
            axis = ax.yaxis
        axis.set_ticks_position(pos)
        axis.set_label_position(pos)


def colorbar(im, width='7%', pad='0%', position='right', label=None, **kwargs):
    """Generate colorbar of same height as image.

    Wrapper around pyplot.colorbar which corrects the height.

    Parameters
    ----------
    im : matplotlib.axes.AxesImage
        Specify the object the colorbar belongs to, e.g. the return value of
        pyplot.imshow().

    width : str or float, optional
        The width between figure and colorbar stated relative as string ending
        with '%' or absolute value in inches.

    pad : str or float, optional
        The width between figure and colorbar stated relative as string ending
        with '%' or absolute value in inches.

    position : str, optional
        Specify the position relative to the image where the colorbar is
        plotted, choose one of ['left', 'top', 'right', 'bottom']

    label : str, optional
        Specify the colorbar label.

    kwargs
        Colorbar properties of
        [pyplot.colorbar()](MPL_DOC.pyplot.colorbar.html)

    """
    orientation = 'vertical'
    if position in {'top', 'bottom'}:
        orientation = 'horizontal'

    # get axes
    if hasattr(im, 'axes'):
        ax = im.axes
    elif hasattr(im, 'ax'):
        ax = im.ax
    else:
        ax = plt.gca()

    # generate divider
    divider = mpl_axes_grid1.make_axes_locatable(ax)
    cax = divider.append_axes(position, width, pad=pad)

    cbar = plt.colorbar(im, cax=cax, orientation=orientation)
    if label:
        cbar.set_label(label)

    # set ticks and label of ticks to the outside
    activate_axis(position, ax=cax)
    # set the axis opposite to the colorbar to active
    activate_axis(_opposite_side(position), ax=ax)

    # invert width and pad
    pad_inv, width_inv = tools.invert_sign(pad), tools.invert_sign(width)
    cax_reset = divider.append_axes(position, width_inv, pad=pad_inv)
    cax_reset.set_visible(False)

    return cbar


def grid(*args, ax=None, **kwargs):
    """Generate grid.

    This function will add a major and minor grid in case of STYLE='default',
    a major grid in case of 'none' and otherwise nothing.

    Parameters
    ----------
    ax : matplotlib axes
        Axes to plot grid.

    args, kwargs
        See [pyplot.grid()](MPL_DOC.pyplot.grid.html)

    """
    # parse axes
    args, ax = tools.parse_axes(*args, ax=ax)

    if __STYLE == 'default':
        gr_maj = ax.grid(which='major', linestyle='--', **kwargs)
        gr_min = ax.grid(which='minor', linestyle='dotted', **kwargs)
        ax.set_axisbelow(True)
        return (gr_maj, gr_min)


def _xminmax(ax):
    """Get xrange of plotted data."""
    return _minmax(lim=ax.get_xlim(), rcparam='axes.xmargin')


def _yminmax(ax):
    """Get yrange of plotted data."""
    return _minmax(lim=ax.get_ylim(), rcparam='axes.ymargin')


def _minmax(lim, rcparam):
    """Get range of plotted data."""
    width = lim[1] - lim[0]
    margin = plt.rcParams[rcparam]
    return [  # min max
        lim[0] + (margin + idx) / (1 + 2 * margin) * width
        for idx in (0, 1)
    ]

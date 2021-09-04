import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import argparse
import glob
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.widgets import RangeSlider, CheckButtons

def LockInX_ds(ds):
    s1_len = ds.loc[ds['SWL'] == 3].index[1]
    x = ds['s1'].values[:s1_len]
    y = ds['s2'].values[::s1_len]

    """ Check if back and forth """
    if len(np.unique(x)) == s1_len:
        z = np.reshape(ds['HP334xx [V]'].values, (len(y), len(x)))

    else :
        x_len = len(x)//2
        x = x[:x_len]
        
        z = np.array([ds['HP334xx [V]'].values[x_len*n:x_len*(n+1)] for n in range(len(ds)//x_len) if n % 2 == 0])
        z_back = np.array([ds['HP334xx [V]'].values[x_len*n:x_len*(n+1)] for n in range(len(ds)//x_len) if n % 2 != 0])

    return x,y,z

def plot_2d(z, x, y):
    fig, main_ax = plt.subplots(figsize=(5, 5))

    """ Create axes """
    divider = make_axes_locatable(main_ax)
    top_ax = divider.append_axes("top", 1.05, pad=0.1, sharex=main_ax)
    bottom_ax = divider.append_axes("top", 0.1, pad=0.1)
    right_ax = divider.append_axes("right", 1.05, pad=0.1, sharey=main_ax)
    top_ax.xaxis.set_tick_params(labelbottom=False)
    right_ax.yaxis.set_tick_params(labelleft=False)
    main_ax.autoscale(enable=True)
    right_ax.autoscale(enable=True)
    top_ax.autoscale(enable=True)
    main_ax.set(xlabel='s1', ylabel='s2')

    """ Plot values """
    cax = main_ax.imshow(z, origin='lower', cmap='RdBu', aspect='auto')
    v_line = main_ax.axvline(np.nan, color='C0')
    h_line = main_ax.axhline(np.nan, color='C1')
    v_prof, = right_ax.plot(z[:,0],np.arange(len(y)), 'C0')
    h_prof, = top_ax.plot(np.arange(len(x)), z[0,:], 'C1')

    """ Update on mouse move """
    def on_move(event):
        if event.inaxes is main_ax:
            cur_x = event.xdata
            cur_y = event.ydata

            v_line.set_xdata([cur_x,cur_x])
            h_line.set_ydata([cur_y,cur_y])
            v_prof.set_xdata(z[:,int(cur_x)])
            h_prof.set_ydata(z[int(cur_y),:])
            right_ax.relim()
            right_ax.autoscale_view()
            top_ax.relim()
            top_ax.autoscale_view()

            fig.canvas.draw_idle()
    fig.canvas.mpl_connect('motion_notify_event', on_move)

    """ Update cmap range """
    def update_vlim(val):
        cax.set_clim(val[0], val[1])

    vmin, vmax = np.min(z), np.max(z), 
    slider = RangeSlider(bottom_ax, "Z-value", vmin, vmax, valinit=(vmin, vmax))
    slider.on_changed(update_vlim)

    """ Return slider otherwise not working with multiple figures """
    return slider #

def main_file(file):
    ds = pd.read_csv(file, sep='\t')
    x,y,z = LockInX_ds(ds)
    plot = plot_2d(z,x,y)
    plt.show()

def main_directory(directory):
    plots = []
    for file in  glob.glob(directory+'*.dat'):
        ds = pd.read_csv(file, sep='\t')
        x,y,z = LockInX_ds(ds)
        plot.append(plot_2d(z,x,y)) #need to be appened to list in order to have each slider working
    plt.show()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="2D plotter on-the-fly")
    parser.add_argument('-f','--file', help="File")
    parser.add_argument('-d','--directory', help="Directory")
    args = parser.parse_args()

    if args.file is not None:
        main_file(args.file)

    if args.directory is not None:
        main_directory(args.directory)

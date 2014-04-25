from numpy import mean, meshgrid, arange, sqrt, zeros, vstack
from os.path import join, splitext
from subprocess import call
from tempfile import mkdtemp
from visvis import gca, record

from phypno.attr import Channels
from phypno.attr.chan import find_chan_in_region, assign_region_to_channels
from phypno.viz.plot_3d import plot_surf, plot_chan

from .snap_grid_to_pial import is_grid


N_ANGLES = 72
HEMI_TOL = 5  # tolerance for electrodes in one or the other hemisphere


def _plot_grid_and_depth_elec(hemi_chan):

    grid_strip_chan = hemi_chan(is_grid)
    neuroport = hemi_chan(lambda x: x.label.lower() == 'neuroport')
    depth_chan = hemi_chan(lambda x: not is_grid(x))

    fig = plot_chan(neuroport, color=(0, 1, 0, 1))
    plot_chan(grid_strip_chan, fig, color=(1, 0, 0, 1))
    plot_chan(depth_chan, fig, color=(0, 0, 1, 1))

    return fig


def plot_rotating_brains(chan, anat, gif_file):
    """Plot the two hemispheres including the electrodes.

    Parameters
    ----------
    chan : instance of phypno.attr.chan.Channels
        channels to plot
    anat : instance of phypno.attr.anat.Freesurfer
        anatomy to plot
    gif_file : str
        name of the gif image.

    """
    hemi_chan = {}
    hemi_chan['lh'] = chan(lambda x: x.xyz[0] < HEMI_TOL)
    hemi_chan['rh'] = chan(lambda x: x.xyz[0] > -HEMI_TOL)

    for hemi, one_hemi_chan in hemi_chan.items():
        fig = _plot_grid_and_depth_elec(one_hemi_chan)
        surf = anat.read_surf(hemi)
        plot_surf(surf, fig)

        ax = gca()
        ax.camera.elevation = 10
        ax.camera.zoom = 0.007
        ax.camera.loc = tuple(mean(surf.vert, axis=0))

        rec = record(ax)
        for i in range(N_ANGLES):
            ax.camera.azimuth = 360 * i / N_ANGLES
            if ax.camera.azimuth > 180:
                ax.camera.azimuth -= 360
            ax.Draw()
            fig.DrawNow()
        rec.Stop()
        fig.Destroy()

        img_dir = mkdtemp()

        rec.Export(join(img_dir, 'image.png'))

        hemi_gif = splitext(gif_file)[0] + '_' + hemi + splitext(gif_file)[1]
        call('convert ' + join(img_dir, 'image*.png') + ' ' + hemi_gif,
             shell=True)


def make_table_of_regions(chan, anat, wiki_table):
    """Write location of the channels as wiki page.

    Parameters
    ----------
    chan : instance of phypno.attr.chan.Channels
        channels to plot
    anat : instance of phypno.attr.anat.Freesurfer
        anatomy to plot
    wiki_table : str
        path to write wiki table.

    """
    assign_region_to_channels(chan, anat)
    neuroport = chan(lambda x: x.label.lower() == 'neuroport')
    depth_chan = chan(lambda x: not is_grid(x))

    with open(wiki_table, 'w') as f:

        if len(neuroport.chan) == 1:
            f.write('Neuroport in ' + neuroport.chan[0].attr['region']
                    + '\n')

        f.write('\n^ Regions ^ Electrodes ^\n')
        for region in sorted(set(depth_chan.return_attr('region'))):
            chan_in_region = find_chan_in_region(depth_chan, anat, region)
            f.write('| {} | {} |\n'.format(region, ', '.join(chan_in_region)))

        f.write('\n^ Electrode ^ Distance ^ Regions ^ \n')
        for one_chan in depth_chan.chan:
            f.write('| {0} | {1} | {2} |\n'.format(one_chan.label,
                                                   one_chan.attr['approx'],
                                                   one_chan.attr['region']))

def create_chan_MG37():
    """Create channels for MG37. MG37 does not have electrode position. We
    should get the correct electrode locations. Until then, we can use this
    placeholder function.

    """
    n_chan = 16
    a_labels = ['AGR' + str(i+1) for i in range(n_chan)]
    a_xyz = _make_grid_MG37(n_chan, 4)

    n_chan = 64
    p_labels = ['PGR' + str(i+1) for i in range(n_chan)]
    p_xyz = _make_grid_MG37(n_chan, 0)

    labels = a_labels + p_labels
    xyz = vstack((a_xyz, p_xyz))

    return Channels(labels, xyz)


def _make_grid_MG37(n_chan, start_point):
    """start_point = 4 for AGR or 0 for PGR """
    y_grid, z_grid = meshgrid(arange(sqrt(n_chan)),
                              start_point - arange(sqrt(n_chan)))
    xyz = zeros((n_chan, 3))
    x = -1
    for i, z, y in zip(arange(n_chan), y_grid.flatten(), z_grid.flatten(),):
        xyz[i, :] = [x, y, z]

    return xyz

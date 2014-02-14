from os.path import join, splitext
from subprocess import call
from tempfile import mkdtemp
from visvis import gca, record

from phypno.viz.plot_3d import plot_surf, plot_chan

from .snap_grid_to_pial import is_grid


N_ANGLES = 72
HEMI_TOL = 5  # tolerance for electrodes in one or the other hemisphere


def _plot_grid_and_depth_elec(hemi_chan):

    grid_strip_chan = hemi_chan(is_grid)
    depth_chan = hemi_chan(lambda x: not is_grid(x))

    fig = plot_chan(grid_strip_chan, color=(1, 0, 0, 1))
    plot_chan(depth_chan, fig, color=(0, 0, 1, 1))

    return fig


def plot_rotating_brains(chan, anat, gif_file):
    """Plot the two hemispheres including the electrodes.

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
        plot_surf(anat.read_surf(hemi), fig)

        ax = gca()
        ax.camera.elevation = 10
        ax.camera.zoom = 0.007
        if hemi == 'lh':
            ax.camera.loc = (-30, -20, 0)
        if hemi == 'rh':
            ax.camera.loc = (30, -20, 0)
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

        hemi_gif = splitext(gif_file)[0] + '-' + hemi + splitext(gif_file)[1]
        call('convert ' + join(img_dir, 'image*.png') + ' ' + hemi_gif,
             shell=True)

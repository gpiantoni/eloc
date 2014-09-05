from phypno.attr.chan import find_chan_in_region, assign_region_to_channels
from phypno.viz.plot_3d import Viz3

from .snap_grid_to_pial import is_grid


N_ANGLES = 72
HEMI_TOL = 5  # tolerance for electrodes in one or the other hemisphere


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

        surf = anat.read_surf(hemi)

        fig = Viz3()
        fig.add_chan(one_hemi_chan(is_grid),
                     color=(1, 0, 0, 1))
        fig.add_chan(one_hemi_chan(lambda x: x.label.lower() == 'neuroport'),
                     color=(0, 1, 0, 1))
        fig.add_chan(one_hemi_chan(lambda x: not is_grid(x)),
                     color=(0, 0, 1, 1))
        # for some weird reasons, surf has to go after channels
        fig.add_surf(surf)

        fig._ax.camera.elevation = 0
        fig.rotate(gif_file.replace('XX', hemi))
        fig._fig.Destroy()


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

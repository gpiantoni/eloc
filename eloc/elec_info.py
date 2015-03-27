from os.path import join, exists
from subprocess import check_call
from tempfile import mkdtemp

from phypno.attr.chan import find_chan_in_region, assign_region_to_channels
from phypno.viz.plot_3d import Viz3

from .snap_grid_to_pial import is_on_pial


ROTATE_STEP = 5
HEMI_TOL = 5  # tolerance for electrodes in one or the other hemisphere


def create_morph_maps(proc_dir):
    if exists(join(proc_dir, 'freesurfer')):
        cmd = []
        cmd.append('export SUBJECTS_DIR=' + proc_dir)
        cmd.append('mne_make_morph_maps --from freesurfer --to fsaverage --redo')
        check_call('; '.join(cmd), shell=True)


def plot_rotating_brains(chan, anat, gif_file, subj):
    """Plot the two hemispheres including the electrodes.

    Parameters
    ----------
    chan : instance of phypno.attr.chan.Channels
        channels to plot
    anat : instance of phypno.attr.anat.Freesurfer
        anatomy to plot
    gif_file : str
        name of the gif image.
    subj : str
        subject code, used to define which channels are on the pial surface

    Notes
    -----
    The code of Viz3 has changed quite a bit, the last running version is:
    phypno dccc0842a421795c4f8c2b404cd4ae33bc189ef3
    """
    hemi_chan = {}
    hemi_chan['lh'] = chan(lambda x: x.xyz[0] < HEMI_TOL)
    hemi_chan['rh'] = chan(lambda x: x.xyz[0] > -HEMI_TOL)

    for hemi, one_hemi_chan in hemi_chan.items():

        surf = getattr(anat.read_brain(), hemi)

        fig = Viz3(color='kw')

        def is_on_pial_for_subj(x): return is_on_pial(subj, x)
        fig.add_chan(one_hemi_chan(is_on_pial_for_subj),
                     color=(255, 0, 0, 255))
        fig.add_chan(one_hemi_chan(lambda x: x.label.lower() == 'neuroport'),
                     color=(0, 255, 0, 255))

        def is_not_on_pial_for_subj(x): return not is_on_pial(subj, x)
        fig.add_chan(one_hemi_chan(is_not_on_pial_for_subj),
                     color=(0, 0, 255, 255))
        # for some weird reasons, surf has to go after channels
        SKIN_COLOR = (239, 208, 207, 150)
        fig.add_surf(surf, color=SKIN_COLOR)

        fig._widget.opts['elevation'] = 0
        _rotate_brain(fig, gif_file.replace('XX', hemi))
        fig._widget.hide()


def _rotate_brain(fig, gif_file):
    img_dir = mkdtemp()

    if 'rh' in gif_file:
        angles = range(180, -180, -ROTATE_STEP)
    if 'lh' in gif_file:
        angles = range(-180, 180, ROTATE_STEP)
    IMAGE = 'image%09d.jpg'

    for i, ang in enumerate(angles):
        fig._widget.opts['azimuth'] = ang

        fig.save(join(img_dir, IMAGE % i))

    _make_gif(img_dir, gif_file)


def _make_gif(img_dir, gif_file):
    """Save the image as rotating gif.
    Parameters
    ----------
    img_dir : path to dir
    directory with all the imags
    gif_file : path to file
    file where you want to save the gif
    Notes
    -----
    It requires ''convert'' from Imagemagick
    """
    check_call('convert ' + join(img_dir, 'image*.jpg') + ' ' + gif_file,
               shell=True)


def make_table_of_regions(chan, anat, wiki_table, subj):
    """Write location of the channels as wiki page.

    Parameters
    ----------
    chan : instance of phypno.attr.chan.Channels
        channels to plot
    anat : instance of phypno.attr.anat.Freesurfer
        anatomy to plot
    wiki_table : str
        path to write wiki table.
    subj : str
        subject code, used to define which channels are on the pial surface
    """
    assign_region_to_channels(chan, anat, max_approx=3,
                              exclude_regions=('White', 'WM', 'Unknown'))
    neuroport = chan(lambda x: x.label.lower() == 'neuroport')

    def is_not_on_pial_for_subj(x): return not is_on_pial(subj, x)
    depth_chan = chan(is_not_on_pial_for_subj)

    with open(wiki_table, 'w') as f:

        if len(neuroport.chan) == 1:
            f.write('Neuroport in ' + neuroport.chan[0].attr['region'] + '\n')

        f.write('\n^ Regions ^ Electrodes ^\n')
        for region in sorted(set(depth_chan.return_attr('region'))):
            chan_in_region = find_chan_in_region(depth_chan, anat, region)
            f.write('| {} | {} |\n'.format(region, ', '.join(chan_in_region)))

        f.write('\n^ Electrode ^ Distance ^ Regions ^ \n')
        for one_chan in depth_chan.chan:
            f.write('| {0} | {1} | {2} |\n'.format(one_chan.label,
                                                   one_chan.attr['approx'],
                                                   one_chan.attr['region']))

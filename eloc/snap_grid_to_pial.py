from logging import getLogger
from re import match
from pathlib import Path
from subprocess import check_call
from tempfile import mkdtemp

from phypno.attr import Channels

lg = getLogger(__name__)


MCRROOT = '/opt/MATLAB/MATLAB_Compiler_Runtime/v83'
MATLAB_BIN = '/home/gio/projects/eloc/scripts/matlab/bin'


def is_on_pial(subj, chan):
    """Check if the electrodes are on the pial surface.

    Parameters
    ----------
    subj : str
        subject code, used to define which channels are on the pial surface
    chan : instance of phypno.attr.chan.Chan
        one single channel

    Returns
    -------
    bool
        if the channel should be on the pial surface
    """
    label = chan.label
    G1 = match('.*G[0-9]{1,2}$', label)
    CING1 = match('.*CING[0-9]$', label)
    GR1 = match('.*GR[0-9]{1,2}$', label.upper())
    RG1 = match('.*RG[0-9]{1,2}$', label.upper())  # typo for gr
    S1 = match('.*S[0-9]$', label.upper()) and not match('.*INS[0-9]$', label.upper())
    ref = match('REF[0-9]$', label.upper())
    neuroport = label in ('neuroport', 'Neuroport')
    microgrid = match('.*micro$', label.upper())

    extra = False
    if subj == 'MG33':
        extra = extra or match('.*TT[0-9]{1}$', label)
        extra = extra or match('.*SbT[0-9]{1}$', label)
        extra = extra or match('.*PO[0-9]{1}$', label)
    if subj == 'MG63':
        extra = extra or match('.*AST[0-9]{1}$', label)
        extra = extra or match('.*PST[0-9]{1}$', label)

    is_on_pial = ((G1 and not CING1) or GR1 or RG1 or S1 or ref or
                  neuroport or microgrid or extra)

    is_not_on_pial = True
    if subj == 'MG91':
        is_not_on_pial = not match('.*L[AP]TS[0-9]{1}$', label)

    return is_on_pial and is_not_on_pial


def adjust_grid_strip_chan(chan, freesurfer, subj):
    """Adjust only grid and strip channels.

    Parameters
    ----------
    chan : instance of phypno.attr.chan.Channels
        channels to snap, with or without grid
    freesurfer : instance of phypno.attr.anat.Freesurfer
        freesurfer information
    subj : str
        subject code, used to define which channels are on the pial surface

    Returns
    -------
    instance of phypno.attr.chan.Channels
        channels where grid and strip have been snapped to surface.

    Notes
    -----
    This works in a tricky way. It only passes the instance of Channels that
    contains instance of Chan which are of interest. However the instances of
    Chan are the same instances (same objects) of the main instance of
    Channels, the full one. That's why we don't need to specify an assignment
    explicitly.

    EM08 has 4 channels called G. They are not grid.

    """
    def is_on_pial_for_subj(x): return is_on_pial(subj, x)
    grid_strip_chan = chan(is_on_pial_for_subj)

    def is_not_on_pial_for_subj(x): return not is_on_pial(subj, x)
    depth_chan = chan(is_not_on_pial_for_subj)

    lg.info('grid/strip chan: ' + ','.join(grid_strip_chan.return_label()))
    lg.info('depth chan: ' + ','.join(depth_chan.return_label()))

    if grid_strip_chan.n_chan > 4:

        grid_xyz = grid_strip_chan.return_xyz()
        grid_in_rh = sum(grid_xyz[:, 0] > 0) > 10
        grid_in_lh = sum(grid_xyz[:, 0] < 0) > 10
        if grid_in_rh and grid_in_lh:
            raise ValueError('Grid is on both sides, check this subject.')
        elif grid_in_rh:
            hemi = 'rh'
        elif grid_in_lh:
            hemi = 'lh'
        else:
            raise ValueError('Not enough electrodes on either side.')

        pial_surf = getattr(freesurfer.read_brain('pial'), hemi)
        return _snap_to_surf(grid_strip_chan, pial_surf)

    else:
        return chan


def _snap_to_surf(chan, surf):

    data_path = Path(mkdtemp())
    lg.debug('temporary path: ' + str(data_path))

    pial = surf.surf_file
    filled = data_path.joinpath('pial.filled.mgz')
    outer = data_path.joinpath('pial_outer')
    smooth = data_path.joinpath('pial_outer_smooth')

    chan_path = data_path.joinpath('chan.csv')
    chan_snapped_path = data_path.joinpath('chan_snapped.csv')
    chan.export(str(chan_path))

    # create smooth surface
    check_call(['mris_fill', '-c', '-r', '1', str(pial), str(filled)])
    check_call(['./run_make_outer_surface.sh', str(MCRROOT), str(filled), '15',
                str(outer)], cwd=MATLAB_BIN)
    check_call(['mris_smooth', '-nw', '-n', '60',  str(outer), str(smooth)])

    # snap electrodes
    check_call(['./run_snap_elec.sh', str(MCRROOT), str(smooth),
                str(chan_path)], cwd=MATLAB_BIN)
    chan = Channels(str(chan_snapped_path))

    return chan

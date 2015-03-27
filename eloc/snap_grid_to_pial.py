from datetime import datetime
from getpass import getuser
from logging import getLogger
from numpy import savetxt, loadtxt
from os import remove
from os.path import join, basename, splitext
from re import match
from socket import gethostname
from subprocess import call, PIPE
from tempfile import mktemp

lg = getLogger(__name__)

MATLAB_PC = 'gp902@rgs03.research.partners.org'
TMP_DATA = 'projects/elecloc/data'
FREESURFER_MATLAB_PATH = '/apps/source/freesurfer_5.2/freesurfer/matlab'
SNAP_MATLAB_PATH = 'projects/elecloc'

USER = getuser()
HOST = gethostname()

REMOVE_FILES = True  # keep all the temporary files


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

    extra = False
    if subj == 'MG33':
        extra = extra or match('.*TT[0-9]{1}$', label)
        extra = extra or match('.*SbT[0-9]{1}$', label)
        extra = extra or match('.*PO[0-9]{1}$', label)
    if subj == 'MG63':
        extra = extra or match('.*AST[0-9]{1}$', label)
        extra = extra or match('.*PST[0-9]{1}$', label)

    return (G1 and not CING1) or GR1 or RG1 or S1 or ref or neuroport or extra


def _exec_remote_script(local_script):
    """Execute script on remote matlab PC.

    Parameters
    ----------
    local_script : path to file
        location of the file on local computer.

    Notes
    -----
    local_script will be deleted

    """
    remote_script = join(TMP_DATA, basename(local_script))

    if REMOVE_FILES:
        with open(local_script, 'a') as f:
            f.write('rm ' + remote_script +
                    '\n')  # this message will self-destruct

    lg.debug('exec_remote: scp')
    call('scp ' + local_script + ' ' + MATLAB_PC + ':' + TMP_DATA, shell=True)
    call('ssh ' + MATLAB_PC + ' "chmod u+x ' + remote_script + '"',
         shell=True)
    lg.debug('exec_remote: run script')
    call('ssh ' + MATLAB_PC + ' "./' + remote_script + '"',
         shell=True, stdout=PIPE)
    remove(local_script)


def create_outer_surf(surf_file):
    """Create outer surface using http://surfer.nmr.mgh.harvard.edu/fswiki/LGI.

    Parameters
    ----------
    surf_file : path to file
        file with the surface, most likely pial.

    Returns
    -------
    path to file
        file with the outer surface

    """
    lg.debug('copy surf file to remote')
    call('scp ' + surf_file + ' ' + MATLAB_PC + ':' + TMP_DATA, shell=True)

    surf_name = basename(surf_file)
    remote_surf = join(TMP_DATA, surf_name)
    remote_filled = join(TMP_DATA, surf_name + '.filled.mgz')  # mris_fill
    outer_surf = join(TMP_DATA, surf_name + '-outer')  # make_outer_surface
    smooth_outer_surf = outer_surf + '-smoothed'  # mris_smooth

    script_file = mktemp('.sh')
    with open(script_file, 'w') as f:
        f.write('mris_fill -c -r 1 ' + remote_surf + ' ' +
                remote_filled + '\n')

        f.write('matlab -nodesktop -nojvm -nosplash -r ' +
                '\"addpath(\'' + FREESURFER_MATLAB_PATH + '\'); ' +
                'make_outer_surface(\'' + remote_filled +
                '\', 15, \'' + outer_surf +
                '\'); exit"\n')

        f.write('mris_smooth -nw -n 60 ' + outer_surf +
                ' ' + smooth_outer_surf + '\n')

    lg.info('make outer surface: start')
    _exec_remote_script(script_file)
    lg.info('make outer surface: done')
    return smooth_outer_surf


def snap_to_surf(chan, surf_file):
    """Use remote script in Matlab to snap electrodes to grid.

    Parameters
    ----------
    chan : instance of phypno.attr.chan.Chan
        instance of channels to snap to outer pial
    surf_file : path to file
        this surface should usually be the smoothed outer pial surface.

    Returns
    -------
    instance of phypno.attr.chan.Chan
        where the subset of channels have been snapped to the surface.

    """
    xyz = chan.return_xyz()

    chan_file = mktemp('.csv')
    savetxt(chan_file, xyz, delimiter=",")

    remote_chan_file = join(TMP_DATA, basename(chan_file))
    snapped_remote_chan_file = splitext(remote_chan_file)[0] + '-snapped.csv'
    str_now = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    remote_matlab_log = join(TMP_DATA, 'matlab_log' + str_now + '.txt')
    local_matlab_log = join('/home/gio', 'matlab_log' + str_now + '.txt')

    lg.debug('copy chan file ({}) to remote'.format(chan_file))
    call('scp ' + chan_file + ' ' + MATLAB_PC + ':' + TMP_DATA, shell=True)
    remove(chan_file)

    script_file = mktemp('.sh')
    with open(script_file, 'w') as f:
        f.write('matlab -nodesktop -nojvm -nosplash -r ' +
                '"addpath(\'' + SNAP_MATLAB_PATH + '\'); ' +
                'snap_to_outerpial(\'' + surf_file + '\', \'' +
                remote_chan_file + '\'); exit" > ' +
                remote_matlab_log + '\n')

        f.write('scp ' + snapped_remote_chan_file + ' ' +
                USER + '@' + HOST + ':' + chan_file + '\n')
        f.write('scp ' + remote_matlab_log + ' ' +
                USER + '@' + HOST + ':' + local_matlab_log + '\n')

        if REMOVE_FILES:
            f.write('rm ' + join(TMP_DATA, '*') + '\n')

    lg.info('snap to surface: start')
    _exec_remote_script(script_file)
    lg.info('snap to surface: done')

    adjusted_xyz = loadtxt(chan_file, delimiter=',')

    for idx_xyz, one_chan in enumerate(chan.chan):
        one_chan.xyz = adjusted_xyz[idx_xyz, :]

    return chan


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

        pial_surf = freesurfer.read_surf(hemi, 'pial')
        outer_pial_file = create_outer_surf(pial_surf.surf_file)
        snap_to_surf(grid_strip_chan, outer_pial_file)

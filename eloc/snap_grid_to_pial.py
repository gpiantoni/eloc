from getpass import getuser
from numpy import savetxt, loadtxt
from os import remove
from os.path import join, basename, splitext
from socket import gethostname
from subprocess import call, PIPE
from tempfile import mktemp

from phypno.attr import Chan


MATLAB_PC = 'gp902@rgs03.research.partners.org'
TMP_DATA = 'projects/elecloc/data'
FREESURFER_MATLAB_PATH = '/apps/source/freesurfer_5.2/freesurfer/matlab'
SNAP_MATLAB_PATH = 'projects/elecloc'

USER = getuser()
HOST = gethostname()

REMOVE_FILES = True  # keep all the temporary files


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

    call('scp ' + local_script + ' ' + MATLAB_PC + ':' + TMP_DATA, shell=True)
    call('ssh ' + MATLAB_PC + ' "chmod u+x ' + remote_script + '"',
         shell=True)
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
    call('scp ' + surf_file + ' ' + MATLAB_PC + ':' + TMP_DATA, shell=True)

    surf_name = basename(surf_file)
    remote_surf = join(TMP_DATA, surf_name)
    remote_filled = join(TMP_DATA, surf_name + '.filled.mgz')  # mris_fill
    outer_surf = join(TMP_DATA, surf_name + '-outer')  # make_outer_surface
    smooth_outer_surf = outer_surf + '-smoothed'  # mris_smooth

    script_file = '/home/gio/script.sh'
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

    _exec_remote_script(script_file)
    return smooth_outer_surf


def snap_to_surf(chan, chan_name, surf_file):
    """Use remote script in Matlab to snap electrodes to grid.

    Parameters
    ----------
    chan : instance of phypno.attr.chan.Chan
        instance of channels to snap to outer pial
    chan_name : list of str
        list of channels to snap to the grid
    surf_file : path to file
        this surface should usually be the smoothed outer pial surface.

    Returns
    -------
    instance of phypno.attr.chan.Chan
        where the subset of channels have been snapped to the surface.

    """
    xyz = chan.return_chan_xyz(chan_name)

    chan_file = mktemp('.csv')
    savetxt(chan_file, xyz, delimiter=",")

    remote_chan_file = join(TMP_DATA, basename(chan_file))
    snapped_remote_chan_file = splitext(remote_chan_file)[0] + '-snapped.csv'
    call('scp ' + chan_file + ' ' + MATLAB_PC + ':' + TMP_DATA, shell=True)
    remove(chan_file)

    script_file = mktemp('.sh')
    with open(script_file, 'w') as f:
        f.write('matlab -nodesktop -nojvm -nosplash -r ' +
                '"addpath(\'' + SNAP_MATLAB_PATH + '\'); ' +
                'snap_to_outerpial(\'' + surf_file + '\', \'' +
                remote_chan_file + '\'); exit"\n')

        f.write('scp ' + snapped_remote_chan_file + ' ' +
                USER + '@' + HOST + ':' + chan_file + '\n')

        if REMOVE_FILES:
            f.write('rm ' + join(TMP_DATA, '*') + '\n')

    _exec_remote_script(script_file)

    adjusted_xyz = loadtxt(chan_file, delimiter=',')
    all_chan = chan.chan_name
    xyz = chan.xyz
    for idx_xyz, one_chan in enumerate(all_chan):
        try:
            idx = chan_name.index(one_chan)
            xyz[idx_xyz, :] = adjusted_xyz[idx, :]
        except ValueError:
            pass

    adjusted_chan = Chan(all_chan, xyz)
    return adjusted_chan

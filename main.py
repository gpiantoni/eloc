from os.path import join, listdir
from sys import path
path.append('/home/gio/projects/rcmg/scripts')
path.append('/home/gio/projects/eloc/scripts')

from phypno.attr import Chan, Surf, Freesurfer
from phypno.viz.plot_3d import plot_surf, plot_chan

from rcmg.interfaces import make_struct
from eloc.snap_grid_to_pial import create_outer_surf, snap_to_surf


recdir = '/home/gio/recordings'

# for subj in listdir(recdir):

subj = 'MG69'
dir_names = make_struct(subj, redo=False)
elec_file = join(dir_names['doc_elec'], 'elec_pos.csv')
chan = Chan(elec_file)

anat = Freesurfer(join(dir_names['mri_proc'], 'freesurfer'))







plot_surf(surf)
plot_chan(chan)


"""
    fixed_elec_file = fix_chan_name(subj, elec_file)
    for eeg_file in eeg_files:
        check_chan_name(eeg_file, fixed_elec_file, dir_names['doc'])
"""

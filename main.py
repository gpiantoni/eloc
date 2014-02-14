from logging import getLogger, DEBUG, INFO
from os import listdir
from os.path import join
from sys import path
path.append('/home/gio/projects/rcmg/scripts')
path.append('/home/gio/projects/eloc/scripts')

from phypno.attr import Channels, Freesurfer


from rcmg.interfaces import make_struct
from eloc.snap_grid_to_pial import adjust_grid_strip_chan

lg = getLogger('eloc')
lg.setLevel(INFO)

recdir = '/home/gio/recordings'

for subj in sorted(listdir(recdir)):
    lg.info('\n' + subj)

    dir_names = make_struct(subj, redo=False)
    elec_file = join(dir_names['doc_elec'], 'elec_pos.csv')
    adj_elec_file = join(dir_names['doc_elec'], 'elec_pos_adjusted.csv')

    chan = Channels(elec_file)
    anat = Freesurfer(join(dir_names['mri_proc'], 'freesurfer'))

    adjust_grid_strip_chan(chan, anat)
    chan.export(adj_elec_file)


"""
    fixed_elec_file = fix_chan_name(subj, elec_file)
    for eeg_file in eeg_files:
        check_chan_name(eeg_file, fixed_elec_file, dir_names['doc'])
"""

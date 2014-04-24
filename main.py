from logging import getLogger, DEBUG, INFO
from os import listdir
from os.path import join
from sys import path
path.append('/home/gio/projects/rcmg/scripts')
path.append('/home/gio/projects/eloc/scripts')

from phypno.attr import Channels, Freesurfer

from rcmg.interfaces import make_struct
from eloc.snap_grid_to_pial import adjust_grid_strip_chan
from eloc.elec_info import plot_rotating_brains, make_table_of_regions
from eloc.fix_chan_name import fix_chan_name

lg = getLogger('eloc')
lg.setLevel(DEBUG)

recdir = '/home/gio/recordings'

subj_with_correct_names = ['EM09']


for subj in listdir(recdir):

    lg.info('\n' + subj)

    dir_names = make_struct(subj, redo=False)
    elec_file = join(dir_names['doc_elec'], 'elec_pos.csv')
    adj_elec_file = join(dir_names['doc_elec'], 'elec_pos_adjusted.csv')

    try:
        chan = Channels(elec_file)
        anat = Freesurfer(join(dir_names['mri_proc'], 'freesurfer'))
    except:
        continue

    adjust_grid_strip_chan(chan, anat)
    chan.export(adj_elec_file)

    gif_file = join(dir_names['doc_wiki'], 'elec_pos.gif')
    try:
        plot_rotating_brains(chan, anat, gif_file)
    except FileNotFoundError:
        continue

    wiki_file = join(dir_names['doc_wiki'], 'elec_pos_table.txt')
    make_table_of_regions(chan, anat, wiki_file)

    if subj in subj_with_correct_names:
        fixed_elec_file = fix_chan_name(subj, elec_file)

"""

    for eeg_file in eeg_files:
        check_chan_name(eeg_file, fixed_elec_file, dir_names['doc'])
"""

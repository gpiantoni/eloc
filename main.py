from logging import getLogger, DEBUG, INFO
from os import listdir
from os.path import join
from sys import path
path.append('/home/gio/projects/rcmg/scripts')
path.append('/home/gio/projects/eloc/scripts')

from phypno.attr import Channels, Freesurfer

from rcmg.interfaces import make_struct
from eloc.snap_grid_to_pial import adjust_grid_strip_chan
from eloc.elec_info import (plot_rotating_brains, make_table_of_regions)
from eloc.fix_chan_name import fix_chan_name, check_chan_name

lg = getLogger('eloc')
lg.setLevel(DEBUG)

recdir = '/home/gio/recordings'


for subj in sorted(listdir(recdir), reverse=False):

    lg.info('\n' + subj)
    dir_names = make_struct(subj, redo=False)

    if subj in ('MG43', 'MG64', 'MG70'):
        all_sess = ('A', 'B')
    else:
        all_sess = ('A', )

    for sess in all_sess:

        elec_file = join(dir_names['doc_elec'], subj + '_elec_pos-orig_sess' +
                         sess + '.csv')
        adj_elec_file = join(dir_names['doc_elec'], subj +
                             '_elec_pos-adjusted_sess' + sess + '.csv')
        names_elec_file = join(dir_names['doc_elec'], subj +
                               '_elec_pos-names_sess' + sess + '.csv')

        try:
            chan = Channels(elec_file)
            anat = Freesurfer(join(dir_names['mri_proc'], 'freesurfer'))
        except (FileNotFoundError, OSError) as err:
            lg.warn(err)
            continue

        try:
            adjust_grid_strip_chan(chan, anat)
        except ValueError as err:
            lg.warn(err)
        chan.export(adj_elec_file)

        gif_file = join(dir_names['doc_wiki'], subj + '_elec_pos-XX_sess' +
                        sess + '.gif')
        try:
            plot_rotating_brains(chan, anat, gif_file)
        except FileNotFoundError:
            continue

        wiki_file = join(dir_names['doc_wiki'], subj + '_elec_pos-wiki_sess' +
                         sess + '.txt')
        make_table_of_regions(chan, anat, wiki_file)

        fix_chan_name(subj, adj_elec_file, names_elec_file)
        chan = Channels(names_elec_file)

        xltek_chan_file = join(dir_names['doc_elec'], 'xltek_elec_names.csv')
        try:
            check_chan_name(chan, xltek_chan_file, sess)
        except FileNotFoundError:
            continue

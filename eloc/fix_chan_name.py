from os.path import join, basename, splitext
from phypno import Dataset
from phypno.attr import Chan


def fix_chan_name(subj_code, elec_file):
    """Match channel names between elec loc and datasets

    It happens that some names are typed differently between the EEG recordings
    and the localization of the electrodes. For our analysis, they have to be
    identical. This function creates a new eeg file with the correct names.

    It's very subject-specific, I don't want to over-generalize.

    """
    fixed_elec_file = splitext(elec_file)[0] + '_fixed.csv'
    chan = Chan(elec_file)

    oldname = []
    newname = []

    if subj_code == 'MG59':
        oldname.extend(['RPT{}'.format(x) for x in range(1, 65)])
        newname.extend(['RTP{}'.format(x) for x in range(1, 65)])
        # some are missing, one chan is written twice

    if subj_code == 'MG61':
        oldname.extend(['AGR{}'.format(x) for x in range(1, 65)])
        newname.extend(['GR{}'.format(x) for x in range(1, 65)])

    if subj_code == 'MG62':
        oldname.extend(['LFO5'])
        newname.extend(['LOF5'])

    if subj_code == 'MG63':
        oldname.extend(['GR{}'.format(x) for x in range(1, 65)])
        newname.extend(['AGR{}'.format(x) for x in range(1, 65)])
        oldname.extend(['gr{}'.format(x) for x in range(1, 65)])
        newname.extend(['PGR{}'.format(x) for x in range(1, 65)])
        oldname.extend(['RAT{}'.format(x) for x in range(1, 9)])
        newname.extend(['ATD{}'.format(x) for x in range(1, 9)])
        oldname.extend(['RMT{}'.format(x) for x in range(1, 9)])
        newname.extend(['MTD{}'.format(x) for x in range(1, 9)])
        oldname.extend(['RPF{}'.format(x) for x in range(1, 9)])
        newname.extend(['PFD{}'.format(x) for x in range(1, 9)])
        oldname.extend(['ROF{}'.format(x) for x in range(1, 9)])
        newname.extend(['OFD{}'.format(x) for x in range(1, 9)])
        oldname.extend(['AST{}'.format(x) for x in range(1, 9)])
        newname.extend(['ATS{}'.format(x) for x in range(1, 9)])
        oldname.extend(['PST{}'.format(x) for x in range(1, 9)])
        newname.extend(['PTS{}'.format(x) for x in range(1, 9)])
        # no location for PTD

    if subj_code == 'MG64':
        oldname.extend(['GR{}'.format(x) for x in range(1, 65)])
        newname.extend(['SGR{}'.format(x) for x in range(1, 65)])
        oldname.extend(['tgr{}'.format(x) for x in range(1, 65)])
        newname.extend(['IGR{}'.format(x) for x in range(1, 65)])
        oldname.extend(['RAT{}'.format(x) for x in range(1, 9)])
        newname.extend(['ATD{}'.format(x) for x in range(1, 9)])
        oldname.extend(['RPT{}'.format(x) for x in range(1, 9)])
        newname.extend(['PTD{}'.format(x) for x in range(1, 9)])
        oldname.extend(['RDF{}'.format(x) for x in range(1, 9)])
        newname.extend(['DFD{}'.format(x) for x in range(1, 9)])
        oldname.extend(['ROF{}'.format(x) for x in range(1, 9)])
        newname.extend(['OFD{}'.format(x) for x in range(1, 9)])
        oldname.extend(['RSF{}'.format(x) for x in range(1, 9)])
        newname.extend(['SFD{}'.format(x) for x in range(1, 9)])
        oldname.extend(['AIS{}'.format(x) for x in range(1, 9)])
        newname.extend(['AIH{}'.format(x) for x in range(1, 9)])
        oldname.extend(['PIS{}'.format(x) for x in range(1, 9)])
        newname.extend(['PIH{}'.format(x) for x in range(1, 9)])

    if subj_code == 'MG65':
        newname.extend(['ASTS{}'.format(x) for x in range(1, 9)])
        oldname.extend(['ATS{}'.format(x) for x in range(1, 9)])
        oldname.extend(['PTS1'])
        oldname.extend(['PSTS1'])
        oldname.extend(['PST{}'.format(x) for x in range(2, 9)])
        newname.extend(['PSTS{}'.format(x) for x in range(2, 9)])
        oldname.extend(['LOF{}'.format(x) for x in range(1, 9)])
        newname.extend(['OFD{}'.format(x) for x in range(1, 9)])
        oldname.extend(['LAF{}'.format(x) for x in range(1, 9)])
        newname.extend(['AFD{}'.format(x) for x in range(1, 9)])
        oldname.extend(['LMF{}'.format(x) for x in range(1, 9)])
        newname.extend(['MFD{}'.format(x) for x in range(1, 9)])
        # some elec are missing locations

    if subj_code == 'MG66':
        oldname.extend(['sgr{}'.format(x) for x in range(1, 17)])
        newname.extend(['FGR{}'.format(x) for x in range(1, 17)])
        oldname.extend(['trg2'])
        oldname.extend(['TGR2'])
        oldname.extend(['tgr{}'.format(x) for x in range(1, 17)])
        newname.extend(['TGR{}'.format(x) for x in range(1, 17)])
        oldname.extend(['ATS{}'.format(x) for x in range(1, 9)])
        newname.extend(['ASTS{}'.format(x) for x in range(1, 9)])
        oldname.extend(['PTS1'])
        oldname.extend(['PSTS1'])
        oldname.extend(['PST{}'.format(x) for x in range(2, 9)])
        newname.extend(['PSTS{}'.format(x) for x in range(2, 9)])
        oldname.extend(['LPF{}'.format(x) for x in range(1, 9)])
        newname.extend(['PFD{}'.format(x) for x in range(1, 9)])
        oldname.extend(['LOF{}'.format(x) for x in range(1, 9)])
        newname.extend(['OFD{}'.format(x) for x in range(1, 9)])
        oldname.extend(['LAT{}'.format(x) for x in range(1, 9)])
        newname.extend(['ATD{}'.format(x) for x in range(1, 9)])
        oldname.extend(['LPT{}'.format(x) for x in range(1, 9)])
        newname.extend(['PTD{}'.format(x) for x in range(1, 9)])

    if subj_code == 'MG67':
        oldname = ['fgr{}'.format(x) for x in range(1, 17)]
        newname = ['SFG{}'.format(x) for x in range(1, 17)]
        oldname.extend(['RAT{}'.format(x) for x in range(1, 7)])
        newname.extend(['ATD{}'.format(x) for x in range(1, 7)])
        oldname.extend(['RPT{}'.format(x) for x in range(1, 7)])
        newname.extend(['PTD{}'.format(x) for x in range(1, 7)])
        oldname.extend(['AST{}'.format(x) for x in range(1, 7)])
        newname.extend(['ASTS{}'.format(x) for x in range(1, 7)])
        oldname.extend(['PST{}'.format(x) for x in range(1, 7)])
        newname.extend(['PSTS{}'.format(x) for x in range(1, 7)])
        oldname.extend(['ROF{}'.format(x) for x in range(1, 7)])
        newname.extend(['OFD{}'.format(x) for x in range(1, 7)])
        oldname.extend(['RPF{}'.format(x) for x in range(1, 7)])
        newname.extend(['PFD{}'.format(x) for x in range(1, 7)])
        oldname.extend(['RDF{}'.format(x) for x in range(1, 7)])
        newname.extend(['DFD{}'.format(x) for x in range(1, 7)])
        oldname.extend(['SS{}'.format(x) for x in range(1, 9)])
        newname.extend(['SYDS{}'.format(x) for x in range(1, 9)])

    elif subj_code == 'MG68':
        oldname = ['LM{}'.format(x) for x in range(1, 9)]
        newname = ['LMF{}'.format(x) for x in range(1, 9)]
        oldname.extend(['RM{}'.format(x) for x in range(1, 9)])
        newname.extend(['RMF{}'.format(x) for x in range(1, 9)])
        oldname.append('LPT4 ')  # space
        newname.append('LPT4')

    for old1, new1 in zip(oldname, newname):
        chan.chan_name = [new1 if ch == old1 else ch for ch in chan.chan_name]

    chan.export(fixed_elec_file)
    return fixed_elec_file


def check_chan_name(eeg_file, elec_file, dest_dir):
    d = Dataset(eeg_file)
    ch = Chan(elec_file)
    report_file = join(dest_dir, basename(eeg_file) + '_chan_report.txt')

    # everything stays upper-case
    nogood = ['C{}'.format(x) for x in range(257)]  # empty channels
    nogood.extend(['OSAT', 'PR'])  # I don't care about these channels

    scalp = ['FP1', 'FP2', 'F3', 'F4', 'F7', 'F8', 'T3', 'T4', 'T5',  'EVT',
             'T6', 'O1', 'O2', 'F3', 'F4', 'C3', 'C4', 'P3', 'P4', 'FZ', 'CZ',
             'PZ', 'C2', 'EKG', 'A1', 'A2', 'T1', 'T2', 'LOC', 'ROC', 'EMG1',
             'EMG2',
             'CII',  # idk
             'FO1', 'FO2', 'FO3', 'FO4']  # MG69: idk

    trigger = ['TRIG', 'TRIG1', 'TRIG2', 'TGR2', 'TRIG/EMG', 'TRIG 1',
               'TRIG 2']

    ref = ['REF', 'REF1', 'REF2', 'REF3', 'REF4']

    pos_chan_name = ch.chan_name

    n_scalp = 0
    n_trigger = 0
    n_ref = 0
    n_ieeg = 0
    unknown = []
    for c in d.header['chan_name']:
        if not c.upper() in nogood:  # we just don't care
            if c in pos_chan_name:
                n_ieeg += 1
                pos_chan_name.remove(c)
            elif c.upper() in scalp:
                n_scalp += 1
            elif c.upper() in trigger:
                n_trigger += 1
            elif c.upper() in ref:
                n_ref += 1
            else:
                unknown.append(c)

    with open(report_file, 'w') as f:
        f.write('Scalp Channels   {0: 3}\n'
                'Trigger Channels {1: 3}\n'
                'Reference Channels {2: 3}\n'
                'IEEG Channels    {3: 3}\n'
                'rec but no pos {4}\n\n'
                'pos but no rec {5}'.format(n_scalp, n_trigger, n_ref, n_ieeg,
                                     ', '.join(unknown),
                                     ', '.join(pos_chan_name)))

    return report_file

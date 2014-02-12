
from phypno.attr import Chan, Surf
from phypno.viz.plot_3d import plot_surf, plot_chan

from eloc.snap_grid_to_pial import create_outer_surf, snap_to_surf


subj_code = 'MG51'
pial_surf = '/home/gio/recordings/' + subj_code + '/mri/proc/freesurfer/surf/lh.pial'
elec_file = '/home/gio/recordings/' + subj_code + '/doc/elec_pos.csv'

outer_pial_file = create_outer_surf(pial_surf)
chan = Chan(elec_file)

ad_chan = snap_to_surf(chan, chan.chan_name[:96], outer_pial_file)

surf = Surf(pial_surf)

plot_surf(surf)
plot_chan(chan)

from obspy.clients.filesystem.sds import Client
from obspy import UTCDateTime, read_inventory
from obspy.signal.array_analysis import array_processing
import os
from retreat.data.fix_times import fix_times
import matplotlib.pyplot as plt

cwd=os.getcwd()
sds_root=cwd+"/retreat/example_data"
sds_type=''
myFMTSTR="{network}.{station}.{location}.{channel}.{year}.{doy:03d}.00.00.mseed"

tstart=UTCDateTime('2014-09-03-06:00')
length=300

client = Client(sds_root, sds_type)
client.FMTSTR = myFMTSTR
inv = read_inventory(cwd+"/retreat/example_data/dataless.seed.UR")

st = client.get_waveforms("VI","UR*","", "HHZ", tstart, tstart+length, merge=1)
 
# remove mean
st.detrend("demean")

# remove trend
st.detrend("linear")

# taper
st.taper(max_percentage=0.05)

# bandpass filter
st.filter("bandpass", freqmin=0.1, freqmax=10)

for tr in st:
    factor = int(round(tr.stats.sampling_rate/25.0))
    tr.decimate(factor)

# add coordinates
for tr in st:
    # get lat and lon from inventory:
    seedid = tr.get_id()
    if type(inv).__name__ == "Inventory":
        tr.stats.coordinates = inv.get_coordinates(seedid)
    else:
        tr.stats.coordinates = dict(
        latitude=inv[inv["id"] == seedid]["latitude"][0],
        longitude=inv[inv["id"] == seedid]["longitude"][0],
        elevation=inv[inv["id"] == seedid]["elevation"][0],
        local_depth=0.0,
    )
        
##### array processing parameters
kwargs = dict(
    # slowness grid: X min, X max, Y min, Y max, Slow Step
    sll_x=-0.6, slm_x=0.6,\
    sll_y=-0.6, slm_y=0.6,\
    sl_s=0.025,
    # sliding window properties
    win_len=10.0, 
    win_frac=1.0-0.3, #NB obspy array_processing uses.. 
    # ..fraction for STEP not overlap
    # frequency properties
    frqlow=0.5, frqhigh=5.0,\
    prewhiten=False,
    # restrict output
    semb_thres=-1E9, vel_thres=-1E9,
    stime=None,
    etime=None,
    store=None,
    verbose=True,
    method=0, # 0 = beamforming, 1 = capon
)
#########
kwargs = fix_times(st, kwargs)


data = array_processing(st, **kwargs)

    # split data matrix
time = data[:, 0]
relpow = data[:, 1]
abspow = data[:, 2]
baz = data[:, 3]
slow = data[:, 4]

fig, ax = plt.subplots(2, 1)

aindex=0

pstart = st[0].stats.starttime.matplotlib_date
pend = st[0].stats.endtime.matplotlib_date


ax[aindex].cla()
ax[aindex].scatter(time, baz, c=slow, alpha=0.6, edgecolors='none')

aindex = aindex + 1

ax[aindex].cla()
ax[aindex].scatter(time, slow)



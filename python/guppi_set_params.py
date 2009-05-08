import os, sys
from guppi_utils import *
from astro_utils import current_MJD
from optparse import OptionParser

# Parse command line

# Dict containing list of key/val pairs to update in
# the status shared mem
update_list = {}
def add_param(option, opt_str, val, parser, *args):
    update_list[args[0]] = val

# Func to add a key/val setting option to the command line.
# longopt, short are the command line flags
# name is the shared mem key (ie, SCANNUM, RA_STR, etc)
# type is the value type (string, float, etc)
# help is the help string for -h
par = OptionParser()
def add_param_option(longopt, name, help, type="string", short=None):
    if short!=None:
        par.add_option(short, longopt, help=help, 
                action="callback", callback=add_param, 
                type=type, callback_args=(name,))
    else:
        par.add_option(longopt, help=help, 
                action="callback", callback=add_param, 
                type=type, callback_args=(name,))

# Non-parameter options
par.add_option("-U", "--update", dest="update",
        help="Run in update mode",
        action="store_true", default=False)
par.add_option("-c", "--cal", dest="cal", 
               help="Setup for cal scan (folding mode)",
               action="store_true", default=False)
par.add_option("-i", "--increment_scan", dest="inc",
               help="Increment scan num",
               action="store_true", default=False)
par.add_option("-I", "--onlyI", dest="onlyI",
               help="Only record total intensity",
               action="store_true", default=False)

# Parameter-setting options
add_param_option("--scannum", short="-n", 
        name="SCANNUM", type="int",
        help="Set scan number")
add_param_option("--tscan", short="-T",
        name="SCANLEN", type="float",
        help="Scan length (sec)")
add_param_option("--parfile", short="-P",
        name="PARFILE", type="string", 
        help="Use this parfile for folding")
add_param_option("--tfold", short="-t",
        name="TFOLD", type="float",
        help="Fold dump time (sec)")
add_param_option("--bins", short="-b",
        name="NBIN", type="int",
        help="Number of profile bins for folding")
add_param_option("--cal_freq",
        name="CAL_FREQ", type="float",
        help="Frequency of pulsed noise cal (Hz, default 25.0)")
add_param_option("--dstime", 
        name="DS_TIME", type="int",
        help="Downsample in time (int, power of 2)")
add_param_option("--dsfreq", 
        name="DS_FREQ", type="int",
        help="Downsample in freq (int, power of 2)")
add_param_option("--obs", 
        name="OBSERVER", type="string",
        help="Set observers name")
add_param_option("--src", 
        name="SRC_NAME", type="string",
        help="Set observed source name")
add_param_option("--ra", 
        name="RA_STR", type="string",
        help="Set source R.A. (hh:mm:ss.s)")
add_param_option("--dec", 
        name="DEC_STR", type="string",
        help="Set source Dec (+/-dd:mm:ss.s)")
add_param_option("--freq", 
        name="OBS_FREQ", type="float",
        help="Set center freq (MHz)")
add_param_option("--bw", 
        name="OBSBW", type="float",
        help="Hardware total bandwidth (MHz)")
add_param_option("--nchan", 
        name="OBSNCHAN", type="int",
        help="Number of hardware channels")
add_param_option("--npol", 
        name="NPOL", type="int",
        help="Number of hardware polarizations")
add_param_option("--feed_pol", 
        name="FD_POLN", type="string",
        help="Feed polarization type (LIN/CIRC)")
add_param_option("--acc_len", 
        name="ACC_LEN", type="int",
        help="Hardware accumulation length")
add_param_option("--packets", 
        name="PKTFMT", type="string",
        help="UDP packet format")


# non-parameter options
par.add_option("--gb43m", dest="gb43m", 
               help="Set params for 43m observing",
               action="store_true", default=False)
par.add_option("--nogbt", dest="gbt", 
               help="Don't pull values from gbtstatus",
               action="store_false", default=True)
par.add_option("--fake", dest="fake",
               help="Set params for fake psr",
               action="store_true", default=False)

(opt,arg) = par.parse_args()

# 43m implies nogbt
if (opt.gb43m):
    opt.gbt = False

# Fake psr implies nogbt
if (opt.fake):
    opt.gbt = False

# Attach to status shared mem
g = guppi_status()

# read what's currently in there
g.read()

# If we're not in update mode
if (opt.update == False):

    # These will later get overwritten with gbtstatus and/or
    # command line values
    g.update("SRC_NAME", "unknown")
    g.update("OBSERVER", "unknown")
    g.update("RA_STR", "00:00:00.0")
    g.update("DEC_STR", "+00:00:00.0")
    g.update("TELESCOP", "GBT")
    g.update("FRONTEND", "none")
    g.update("PROJID", "test")
    g.update("FD_POLN", "LIN")
    g.update("TRK_MODE", "TRACK")
    g.update("OBSFREQ", 1200.0)
    g.update("OBSBW", 800.0)

    g.update("OBS_MODE", "SEARCH")
    g.update("CAL_MODE", "OFF")

    g.update("SCANLEN", 8 * 3600.)
    g.update("BACKEND", "GUPPI")
    g.update("PKTFMT", "GUPPI")
    g.update("DATAHOST", "bee2_10")
    g.update("DATAPORT", 50000)
    g.update("POL_TYPE", "IQUV")

    g.update("CAL_FREQ", 25.0)
    g.update("CAL_DCYC", 0.5)
    g.update("CAL_PHS", 0.0)

    g.update("OBSNCHAN", 2048)
    g.update("NPOL", 4)
    g.update("NBITS", 8)
    g.update("PFB_OVER", 4)
    g.update("NBITSADC", 8)
    g.update("ACC_LEN", 16)
    g.update("NRCVR", 2)

    g.update("ONLY_I", 0)
    g.update("DS_TIME", 1)
    g.update("DS_FREQ", 1)

    g.update("TFOLD", 30.0)
    g.update("NBIN", 256)
    g.update("PARFILE", "")

    g.update("OFFSET0", 0.0)
    g.update("SCALE0", 1.0)
    g.update("OFFSET1", 0.0)
    g.update("SCALE1", 1.0)
    g.update("OFFSET2", 0.5)
    g.update("SCALE2", 1.0)
    g.update("OFFSET3", 0.5)
    g.update("SCALE3", 1.0)

    # Pull from gbtstatus if needed
    if (opt.gbt):
        g.update_with_gbtstatus()

    # Current time
    MJD = current_MJD()
    MJDd = int(MJD)
    MJDf = MJD - MJDd
    MJDs = int(MJDf * 86400 + 1e-6)
    offs = (MJD - MJDd - MJDs/86400.0) * 86400.0
    g.update("STT_IMJD", MJDd)
    g.update("STT_SMJD", MJDs)
    if offs < 2e-6: offs = 0.0
    g.update("STT_OFFS", offs)


# Any 43m-specific settings
if (opt.gb43m):
    g.update("TELESCOP", "GB43m")
    g.update("FRONTEND", "43m_rcvr")
    g.update("FD_POLN", "LIN")

# Any fake psr-specific settings
if (opt.fake):
    g.update("SRC_NAME", "Fake_PSR")
    g.update("FRONTEND", "none")
    g.update("OBSFREQ", 1000.0)
    g.update("FD_POLN", "LIN")

# Cal mode
if (opt.cal):
    g.update("OBS_MODE", "CAL")
    g.update("CAL_MODE", "ON")
    g.update("TFOLD", 10.0)
    g.update("SCANLEN", 60.0)

# Scan number
try:
    scan = g["SCANNUM"]
    if (opt.inc):
        g.update("SCANNUM", scan+1)
except KeyError:
    g.update("SCANNUM", 1)

# Observer name
try:
    obsname = g["OBSERVER"]
except KeyError:
    obsname = "unknown"

if (obsname=="unknown"):
    try:
        username = os.environ["LOGNAME"]
    except KeyError:
        username = os.getlogin()
    g.update("OBSERVER", username)

# Apply explicit command line values
# These will always take precedence over defaults now
for (k,v) in update_list.items():
    g.update(k,v)

# Apply to shared mem
g.write()

# Update any derived parameters:

# Base file name
if (opt.cal):
    base = "guppi_%5d_%s_%04d_cal" % (g['STT_IMJD'], 
            g['SRC_NAME'], g['SCANNUM'])
else:
    base = "guppi_%5d_%s_%04d" % (g['STT_IMJD'], 
            g['SRC_NAME'], g['SCANNUM'])
g.update("BASENAME", base)

# Time res, channel bw
g.update("TBIN", abs(g['ACC_LEN']*g['OBSNCHAN']/g['OBSBW']*1e-6))
g.update("CHAN_BW", g['OBSBW']/g['OBSNCHAN'])

# Az/el
g.update_azza()

# Apply back to shared mem
g.write()

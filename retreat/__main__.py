"""Launches the software"""
import argparse
from retreat.start import start

### set up arguments
parser = argparse.ArgumentParser()

# web mode
parser.add_argument("-w", "--web", help="Run using web interface in browser rather than GUI window",
                    action="store_true")
# command line mode
parser.add_argument("-c", "--cmd", help="Run using command interface - NO GUI, \
                    parameters read from defaults file", action="store_true")

# specify figure output destination
parser.add_argument("-f", "--figs", help="Specify either: 'gui' or 'web' for figure output.\
                    Only valid in command line mode (-c)")

# specify defaults file
parser.add_argument("-d", "--defaults", help="Full path to defaults file")

# multiple array mode
parser.add_argument("-n", "--narrays", help="Use multiple arrays, give number of arrays")

args = parser.parse_args()

### process arguments

# print path to defaults file for log
if args.defaults:
    print("defaults file:", args.defaults)

# check if command line mode when specifying figure output
if args.figs:
    if not args.cmd:
        raise SystemExit('Error. Can only specify figure destination in command line mode (-c)')
    if args.figs not in  ('gui', 'web'):
        raise SystemExit('Error. Figure destination MUST be either: "gui" or "web"')

# check for multiple arrays
if args.narrays:
    if int(args.narrays) > 2:
        if not args.cmd:
            raise SystemExit('Error. More than 2 arrays is incompatible with the GUI.\n\
For more than 2 arrays, RETREAT must be run in command line mode\n\
with the defaults file supplied, i.e. with both -c and -d options')

### start RETREAT

if __name__ == '__main__':
    start(args)

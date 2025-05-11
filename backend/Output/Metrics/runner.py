import os
import argparse
from optparse import OptionParser
from robotmetrics import generate_report
from robotmetrics import IGNORE_TYPES
from robotmetrics import IGNORE_LIBRARIES
from version import __version__

def parse_options():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    general = parser.add_argument_group("General")
    parser.add_argument(
        '-v', '--version',
        action='store_true',
        dest='version',
        help='Display application version information'
    )
    general.add_argument(
        '--logo',
        dest='logo',
        default='./Images/BRT_LOGO.png',
        help="User logo (default: dummy BRT image )"
    )

    general.add_argument(
        '--ignorelib',
        dest='ignore',
        default=IGNORE_LIBRARIES,
        nargs="+",
        help="Ignore keywords of specified library in report"
    )

    general.add_argument(
        '--ignoretype',
        dest='ignoretype',
        default=IGNORE_TYPES,
        nargs="+",
        help="Ignore keywords with specified type in report"
    )

    general.add_argument(
        '-I', '--inputpath',
        dest='path',
        default=os.path.curdir,
        help="Path of result files"
    )

    general.add_argument(
        '-R', '--report',
        dest='report_name',
        default='report.html',
        help="Name of report.html"
    )

    general.add_argument(
        '-L', '--log',
        dest='log_name',
        default='log.html',
        help="Name of log.html"
    )

    general.add_argument(
        '-O', '--output',
        dest='output',
        default="output.xml",
        help="Name of output.xml"
    )

    email_parser = parser.add_argument_group("Sending email",)
    email_parser.add_argument(
        '-E', '--email',
        dest='email',
        action="store_true",
        help="Sends email with metrics report"
    )
    email_parser.add_argument(
        '--to',
        dest='to',
        default=None,
        help="To address"
    )

    email_parser.add_argument(
        '--from',
        dest='sender',
        default=None,
        help="From address"
    )

    email_parser.add_argument(
        '--cc',
        dest='cc',
        default=None,
        help="CC address"
    )

    email_parser.add_argument(
        '--pwd',
        dest='pwd',
        default=None,
        help="Password of email"
    )

    args = parser.parse_args()
    return args


def main():
    args = parse_options()
    print(args)
    if args.version:
        print(__version__)
        exit(0)

    generate_report(args)

if __name__ == "__main__":
     main()

import sys


class ConfigurationError(Exception):
    pass


def run():
    print "TODO"
    sys.argv
    sys.exit(0)


def usage(out):
    out.write(_(u"TODO: usage\n"))


def main():
    try:
        run()
    except ConfigurationError, e:
        sys.stderr.write(_(u"Error: ") + e.message + u"\n")
        usage(sys.stderr)
        sys.exit(1)

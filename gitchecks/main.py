import codecs
import gettext
import locale
import sys
import os


def setup():
    app_dir = os.path.dirname(os.path.realpath(__file__))

    # Setup gettext
    locale.setlocale(locale.LC_ALL, '')
    gettext.install('gitchecks', os.path.join(app_dir, 'locales'), True)

    # Python tends to f*ck up, make sure it doesn't decide to use 'ascii'
    sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)
    sys.stderr = codecs.getwriter(locale.getpreferredencoding())(sys.stderr)

    # Setup the Python path
    try:
        import knock.main
    except ImportError:
        sys.path.insert(0, os.path.realpath(os.path.join(app_dir, '..')))
        try:
            import gitchecks.main
        except ImportError:
            sys.stderr.write(_(u"Couldn't setup the Python path\n"))
            sys.exit(2)


def main():
    setup()

    import gitchecks.app
    gitchecks.app.main()


if __name__ == '__main__':
    main()

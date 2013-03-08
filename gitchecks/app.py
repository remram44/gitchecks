import re
import string
import subprocess
import sys


whitespace = set(iter(string.whitespace))

def iswhitespace(s):
    return all(c in whitespace for c in s)


def warning(msg):
    sys.stderr.write("W: %s\n" % msg)


def error(msg):
    sys.stderr.write("E: %s\n" % msg)


chunkstart = re.compile(r'^@@ -[0-9]+(?:,[0-9+])? \+([0-9]+)(?:,[0-9+])?')

def check_commit(check_whitespace=True, whitespace_near=0):
    """Checks that no trailing whitespace is added by the commit.
    """
    diff = subprocess.Popen(['git', 'diff', '--cached',
                             '-U%d' % whitespace_near],
                            stdout=subprocess.PIPE)
    stdout, stderr = diff.communicate()
    errors = 0
    filename = None
    for line in stdout.split('\n'):
        if line.startswith('+++ b/'):
            filename = line[6:]
        elif line.startswith('@@ '):
            lineno = int(chunkstart.match(line).group(1))
        elif line.startswith(' '):
            if len(line) > 1 and line[-1] in whitespace:
                warning(
                        _(u"in {file}, line {line}: trailing whitespace "
                          "within {context_lines} lines of change").format(
                        file=filename, line=lineno,
                        context_lines=whitespace_near))
            lineno += 1
        elif line.startswith('+'):
            if len(line) > 1 and line[-1] in whitespace:
                error(
                        _(u"in {file}, line {line}: change adds trailing "
                          "whitespace").format(file=filename, line=lineno))
                errors += 1
            lineno += 1

    return errors


def parse_cmdline(args):
    if len(args) <= 1:
        sys.stderr.write(_(u"gitchecks called without arguments"))
        sys.exit(1)
    action = args[1]
    params = dict()
    for arg in args[2:]:
        pos = arg.find('=')
        if pos != -1:
            params[arg[:pos]] = arg[pos+1:]
        else:
            params[arg[:pos]] = True
    return action, params


def main():
    if len(sys.argv) == 1:
        sys.stderr.write(_(u"gitchecks called without arguments"))
        sys.exit(1)

    action, params = parse_cmdline(sys.argv)
    if action == 'pre-commit':
        errors = check_commit(**params)
        if errors > 0:
            sys.stderr.write(_(u"%d errors, aborting commit\n") % errors)
            sys.exit(1)
    sys.exit(0)

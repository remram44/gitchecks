import os
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


chunkstart = re.compile(r'^@@ -[0-9]+(?:,[0-9]+)? \+([0-9]+)(?:,[0-9]+)?')

def check_commit(check_whitespace=True, whitespace_near=0, line_style=None,
        check_mergeconflict=True, python_check_debug=True):
    """Checks what is about to be committed.
    """
    if line_style is not None:
        line_style = line_style.lower()
    if isinstance(check_whitespace, basestring):
        check_whitespace = check_whitespace != '0'
    whitespace_near = int(whitespace_near)
    if isinstance(check_mergeconflict, basestring):
        check_mergeconflict = check_mergeconflict != '0'
    if isinstance(python_check_debug, basestring):
        python_check_debug = python_check_debug != '0'

    diff = subprocess.Popen(['git', 'diff', '--cached',
                             '-U%d' % whitespace_near],
                            stdout=subprocess.PIPE)
    stdout, stderr = diff.communicate()
    errors = 0
    filename = None
    for line in stdout.split('\n'):
        if line.startswith('+++ b/'):
            filename = line[6:]
        elif line.startswith('+++ '):
            filename = None
        elif not filename:
            pass    # Here we might be handling a deleted file, or reading the
                    # header
        elif line.startswith('@@ '):
            lineno = int(chunkstart.match(line).group(1))
        elif line.startswith(' '):
            if check_whitespace and len(line) > 1 and line[-1] in whitespace:
                warning(
                        _(u"in {file}, line {line}: trailing whitespace "
                          "within {context_lines} lines of change").format(
                        file=filename, line=lineno,
                        context_lines=whitespace_near))
            lineno += 1
        elif line.startswith('+'):
            if len(line) > 1:
                if line[-1] == '\r':
                    if line_style == 'lf':
                        error(
                                _(u"in {file}, line {line}: added line uses "
                                  "CRLF line ending").format(
                                file=filename, line=lineno))
                    line = line[:-1]
                elif line_style == 'crlf':
                    error(
                            _(u"in {file}, line {line}: added line uses LF "
                              "line ending").format(
                            file=filename, line=lineno))
                if check_whitespace and line[-1] in whitespace:
                    error(
                            _(u"in {file}, line {line}: change adds trailing "
                              "whitespace").format(file=filename, line=lineno))
                    errors += 1
                if check_mergeconflict and (
                        line.startswith('+>>>>>>>') or
                        line.startswith('+<<<<<<<') or
                        line.startswith('+=======')):
                    error(
                            _(u"in {file}, line {line}: committing a merge "
                              "conflict marker").format(
                            file=filename, line=lineno))
                if python_check_debug and filename[-3:].lower() == '.py':
                    if 'print' in line:
                        warning(
                                _(u"in {file}, line {line}: print statement "
                                  "added").format(file=filename, line=lineno))
                    if 'pdb.set_trace(' in line:
                        warning(
                                _(u"in {file}, line {line}: adding "
                                  "pdb.set_trace()").format(
                                file=filename, line=lineno))
                    if 'code.interact' in line:
                        warning(
                                _(u"in {file}, line {line}: adding "
                                  "code.interact()").format(
                                file=filename, line=lineno))
            lineno += 1

    return errors


def parse_cmdline(args):
    if len(args) <= 1:
        sys.stderr.write(_(u"gitchecks called without arguments\n"))
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


def find_git_dir():
    here = os.path.realpath('.')
    while not os.path.exists('.git'):
        parent = os.path.realpath('..')
        if parent == here:
            sys.stderr.write(_(u"Unable to find .git folder in parent "
                               "directories! Aborting..."))
            sys.exit(1)
        os.chdir(parent)


def main():
    action, params = parse_cmdline(sys.argv)
    find_git_dir()

    if action == 'pre-commit':
        # Are we merging?
        if os.path.isfile('.git/MERGE_HEAD'):
            sys.exit(0)

        errors = check_commit(**params)
        if errors > 0:
            sys.stderr.write(_(u"%d errors, aborting commit\n") % errors)
            sys.exit(1)
    sys.exit(0)

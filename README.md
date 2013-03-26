# gitchecks

This is a pack of source checks intended to be used as commit hook.

## Setup

Create `.git/hooks/pre-commit` and add the following content:

    #!/bin/sh
    python /path/to/githooks/main.py pre-commit [options]

where `[options]` is a bunch of options with the format `opt1=val1 opt2=val2`

## Available checks

### Whitespace errors

Fails if the commit adds trailing whitespace. Warns if a change occurs near an
erroneous line.

Options:
* `check_whitespace` enables/disables check (default: `1`, enabled)
* `whitespace_near` sets the number of lines around a change to check (default:
`0` lines, doesn't check)

### Line ending style

Fails if the commit adds line with an incorrect line ending sequence.

Options:
* `line_style` either `crlf` or `lf`, the expected line ending sequence
(default: unset, disabled)

### Merge conflict markers

Fails if the commit adds mergeconflict markers.

Options:
* `check_mergeconflict` enables/disables check (default: `1`, enabled)

### Python debugging output

Warns if the commit adds common debugging lines, such as print statements and
calls to pdb.set_trace or code.interact. Only used on files ending with `.py`.

Options:
* `python_check_debug` enables/disables check (default: `1`, enabled)

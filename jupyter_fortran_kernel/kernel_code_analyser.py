import re

ANY          = lambda p: r'(?:(?:{})*)'.format(p)
ONE_OR_MORE  = lambda p: r'(?:(?:{})+)'.format(p)
EITHER       = lambda a, b: r'(?:(?:{})|(?:{}))'.format(a, b)
OPTIONAL     = lambda p: r'(?:(?:{})?)'.format(p)
WHITESPACE   = r'(?:[ \t])'
END_OF_CODE  = r'(?:$|!)'


def codeline_ends_a_program(line):
    m = re.match('^' + ANY(WHITESPACE) + 'end'
                     + ANY(WHITESPACE) + EITHER(END_OF_CODE,'program'),
                 line,
                 re.IGNORECASE)
    return (m is not None)


def codeline_starts_a_module(line):
    m = re.match('^' + ANY(WHITESPACE) + OPTIONAL('sub') + 'module',
                 line,
                 re.IGNORECASE)
    return (m is not None)


def analyse(code):

    result = {'cflags' : [],
              'ldflags': [],
              'args'   : [],
              'program': False,
              'module' : False}

    for line in code.splitlines():
        if codeline_ends_a_program(line):
            result['program'] = True
        elif codeline_starts_a_module(line):
            result['module'] = True
        elif line.startswith('!%'):
            key, value = line[2:].split(":", 2)
            key = key.strip().lower()

            if key in ['ldflags', 'cflags']:
                for flag in value.split():
                    result[key] += [flag]
            elif key == "args":
                # Split arguments respecting quotes
                for argument in re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', value):
                    result['args'] += [argument.strip('"')]

    return result

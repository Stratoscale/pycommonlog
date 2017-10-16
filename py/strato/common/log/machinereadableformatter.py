import re
import simplejson

color_regex = re.compile(r"([^-_a-zA-Z0-9!@#%&=,/'\";:~`\$\^\*\(\)\+\[\]\.\{\}\|\?\<\>\\]+|[^\s]+)")
suffix_regex = re.compile(r'\[\d+m')
repr_regex = re.compile(r"\<(RED|GREEN|YELLOW|BLUE|BLACK|MAGENTA|CYAN|WHITE)-string: \'(?P<txt>.*)\'\>", re.DOTALL)


class MachineReadableFormatter:
    _IGNORED_ATTRIBUTES = set(['relativeCreated', 'msecs', 'exc_info', 'startColor', 'endColor'])

    def format(self, record):
        data = dict(record.__dict__)
        for attribute in self._IGNORED_ATTRIBUTES:
            if attribute in data:
                del data[attribute]

        for attribute in data:
            if data[attribute] is not None:
                if isinstance(data[attribute], str):
                    data[attribute] = clean_colors(data.get(attribute, ""))
                elif isinstance(data[attribute], tuple):
                    data[attribute] = tuple((clean_colors(item) for item in data[attribute]))
        return simplejson.dumps(data, default=self._defaultSerializer, encoding='raw-unicode-escape')

    def _defaultSerializer(self, obj):
        return str(obj)


def clean_colors(text):
    result = color_regex.sub('', str(text))
    result = suffix_regex.sub('', result)
    match = repr_regex.match(result)
    if match:
        import ipdb
        ipdb.set_trace()
        result = repr_regex.sub(match.groupdict().get('txt', ''), result)

    return result

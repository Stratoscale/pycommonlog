import json


class MachineReadableFormatter:
    _IGNORED_ATTRIBUTES = set(['relativeCreated', 'msecs', 'message', 'exc_info', 'startColor', 'endColor'])

    def format(self, record):
        data = dict(record.__dict__)
        for attribute in self._IGNORED_ATTRIBUTES:
            if attribute in data:
                del data[attribute]
        return json.dumps(data, default=self._defaultSerializer, ensure_ascii=False)

    def _defaultSerializer(self, obj):
        return str(obj)

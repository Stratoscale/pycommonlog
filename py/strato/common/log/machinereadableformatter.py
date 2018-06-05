import simplejson
import uuid


class MachineReadableFormatter:
    _IGNORED_ATTRIBUTES = set(['relativeCreated', 'msecs', 'message', 'exc_info', 'startColor', 'endColor'])
    session_id = uuid.uuid4()

    def format(self, record):
        record.session_id = str(self.session_id)
        data = dict(record.__dict__)
        for attribute in self._IGNORED_ATTRIBUTES:
            if attribute in data:
                del data[attribute]
        return simplejson.dumps(data, default=self._defaultSerializer, encoding='raw-unicode-escape')

    def _defaultSerializer(self, obj):
        return str(obj)

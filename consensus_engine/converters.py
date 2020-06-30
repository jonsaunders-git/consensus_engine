# Contents consensus_engine/converters.py
import datetime
from django.utils.timezone import make_aware


class DateConverter:
    regex = '([0-3]|)\\d-[0-1]\\d-[1-2](0|9)\\d\\d'

    def to_python(self, value):
        return make_aware(datetime.datetime.strptime(value, "%d-%m-%Y"))

    def to_url(self, value):
        return '{}'.format(value.strftime('%d-%m-%Y'))

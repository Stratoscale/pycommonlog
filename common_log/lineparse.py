import datetime
import re
import calendar
import time


DEFAULT_TIMESTAMP_REGEX = '(\d{4}[-/]\d{2}[-/]\d{2} \d{2}[:]\d{2}[:]\d{2})'
# YYYY<-or/>MM<-or/>DD HH:MM:SS
DEFAULT_TIMESTAMP_FORMAT = "%Y/%m/%d %H:%M:%S"
# Year/Month/Day Hour:Minute:Second


def seperateTimestamp(message, timestampFormat=DEFAULT_TIMESTAMP_REGEX):
    # default regex matches date pattern in timestampFormat "yyyy/dd/mm hh:mm:ss"
    dateRegex = re.compile(timestampFormat)
    date = dateRegex.findall(message.strip())[0]
    # remove everything at the beginning of the line that isn't letters and "[" (for consul logs) to format multiple
    # line messages
    msg = '\n'.join([re.sub("^[^a-zA-Z\[]*", "                ", line) for line in message.split('\n')])
    return msg, date


def translateToEpoch(timeStamp, timestampFormat=DEFAULT_TIMESTAMP_FORMAT):
    ms = 0
    if timestampFormat.endswith('%f'):  # handle milliseconds
       separator = timestampFormat[-3]
       if separator in timeStamp:
          ms = timeStamp.rsplit(separator, 1)[1]
    timeObject = datetime.datetime.strptime(timeStamp, timestampFormat)
    return calendar.timegm(timeObject.timetuple()) + float(ms)/1000


def getTimezoneOffset():
    return time.timezone if (time.localtime().tm_isdst == 0) else time.altzone

import os
from time import sleep
from datetime import datetime
from threading import Thread

HERE = os.path.dirname(__file__)
DIR_UPLOADS = os.path.abspath(os.path.join(HERE, '..', '..', 'public', 'uploads'))

DEFAULT_CHUNK_SIZE = 64 * 2 ** 10



def _chunkinize(fileobj, chunk_size=None):
    if not chunk_size:
        chunk_size = DEFAULT_CHUNK_SIZE

    try:
        fileobj.seek(0)
    except AttributeError:
        pass

    while True:
        data = fileobj.read(chunk_size)
        if not data:
            break
        yield data


def get_upload_filepath(filename):
    dir_today = datetime.today().strftime('%Y%m%d')
    return os.path.join(DIR_UPLOADS, dir_today, filename)


def handle_file_upload(fileobj):
    # create target upload dir if necessary
    dir_today = datetime.today().strftime('%Y%m%d')
    dir_target = os.path.join(DIR_UPLOADS, dir_today)
    if not os.path.exists(dir_target):
        os.makedirs(dir_target)

    # make unique name for target file
    fnow = datetime.today().strftime('%H%M%S')
    filename = '%s-%s' % (fnow, fileobj.filename)
    filepath = os.path.join(dir_target, filename)
    try:
        with open(filepath, 'wb+') as dest:
            chunks = _chunkinize(fileobj.file)
            for chunk in chunks:
                dest.write(chunk)
            dest.flush()
        return filepath
    except:
        return None


def ticks(dt=None):
    if dt is None:
        dt = datetime.now()
    tick = lambda d: (d.hour*60*60) + (d.minute*60) + (d.second+d.microsecond)
    return (dt.toordinal() + tick(dt))


class TaskThread(Thread):
    count, level = (0, 0)

    def __init__(self, task, args):
        super(TaskThread, self).__init__()
        self.task = task
        self.args = args

    def percent_done(self):
        return self._get_percent_done(self.level, self.count)

    def run(self):
        self.sleep(0.05)
        self.task(self.args)

    def sleep(self, seconds=0.1):
        sleep(seconds)

    def set_progress(self, args, ref=0, target=100):
        progress, level, target = [int(x) for x in args.split(':')]
        if target == 0:
            self.level, self.count = (progress, 100)
        else:
            self.level, self.count = (level, target)
            done = self._get_percent_done(level, target, target-ref) + ref
            if done < progress:
                done = progress
            self.level, self.count = (done, 100)

    def _get_percent_done(self, chunk, total, percentage=100.0):
        return int((float(chunk)/float(total)) * percentage)

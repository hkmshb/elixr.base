import os
import sys
import enum
import transaction

from pyramid.paster import get_appsettings, setup_logging
from pyramid.scripts.common import parse_vars

from elixr.sax.export.importer import XRefResolver
from elixr.sax.orgz import Organisation
from elixr.sax.address import State
from elixr.base import AttrDict

from ..data.models import get_engine, get_session_factory, get_tm_session
from ..data.models.network import Voltage, ElectricLine, ElectricStation
from ..export.importer import MegaImporter



def _process(db, options):
    # check that the file exists
    if not os.path.exists(options['file']):
        print('File not found: %s' % options['file'])
        sys.exit(0)
    
    from openpyxl import load_workbook
    wb = load_workbook(options['file'], read_only=True)
    importer = MegaImporter(AttrDict(db=db, cache=XRefResolver(db)))
    importer.import_data(wb)
    if importer.has_errors:
        _log_errors(importer.summarise_errors())
        print('View error log for details...')


def _log_errors(message, log_dir=None):
    def get_freename(dir_path, filename):
        i, name, ext = 1, *os.path.splitext(filename)
        fullpath = os.path.join(dir_path, filename)
        while os.path.exists(fullpath):
            fullpath = os.path.join(dir_path, name + ('-%s' % i) + ext)
            i += 1
        return fullpath
    
    log_dir = log_dir or os.getcwd()
    fullpath = get_freename(log_dir, 'import-error.log')
    with open(fullpath, 'w') as f:
        f.write(message)
        f.flush()


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)

def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
        
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    
    settings = get_appsettings(config_uri, options=options)
    session_factory = get_session_factory(get_engine(settings))

    with transaction.manager:
        db = get_tm_session(session_factory, transaction.manager)
        assert 'file' in options
        _process(db, options)

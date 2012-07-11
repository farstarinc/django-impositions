import sys
import traceback
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_syncdb
from django.core.signals import got_request_exception
from impositions.models import DataLoader
from impositions.utils import get_data_loader

@receiver(post_syncdb)
def sync_data_loaders(sender, **kwargs):
    # FIXME: Check to see if impositions has been migrated to at least 0005
    loaders = getattr(settings, 'IMPOSITIONS_DATA_LOADERS', ())
    for pfx, path in loaders:
        try:
            loader = DataLoader.objects.get(prefix=pfx)
        except DataLoader.DoesNotExist:
            loader = DataLoader(prefix=pfx, path=path)
            print 'Adding impositions data loader: {}'.format(pfx)
        else:
            if loader.path != path:
                print 'Updating impositions data loader: {}'.format(pfx)
                loader.path = path

        loader.save()

    # remove data obsolete data loaders
    for loader in DataLoader.objects.all():
        try:
            get_data_loader(loader.path)
        except (ImportError, AttributeError):
            print 'Removing obsolete data loader: {}'.format(loader.prefix)
            loader.delete()

@receiver(got_request_exception)
def exception_printer(sender, **kwargs):
    print >> sys.stderr, ''.join(traceback.format_exception(*sys.exc_info()))

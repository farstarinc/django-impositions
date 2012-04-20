from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_syncdb
from impositions.models import DataLoader

@receiver(post_syncdb)
def sync_data_loaders(sender, **kwargs):
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

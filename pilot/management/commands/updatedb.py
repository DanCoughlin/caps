from django.core.management.base import BaseCommand, CommandError
from django.core.management.color import no_style
import caps.updates

class Command(BaseCommand):
    help = "Executes a python-based database update script"
    args = "script"

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError("Usage: updatedb <script>")
    
        modname = args[0]
        self.style = no_style()

        # Dynamic import: im doin it rite?
        try:
            __import__("caps.updates." + modname)
            module = getattr(caps.updates, modname)
        except:
            raise CommandError("importing module caps.updates.%s failed" % modname)
        
        for method in [getattr(module, ref) for ref in dir(module) if ref.startswith('update_')]:
            try:
                print "Executing %s" % method.__name__
                method()
            except TypeError:
                # element is not callable(), continue
                continue


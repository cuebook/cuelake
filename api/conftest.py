import pytest 
import pathlib
from django.core.management import call_command

@pytest.fixture()
def populate_seed_data(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        cmd_args = list(pathlib.Path().glob('seeddata/*.json'))
        call_command('loaddata', *cmd_args)


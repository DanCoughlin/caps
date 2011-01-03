import arkpy
from celery.decorators import task


@task
def mint(authority, template):
    return arkpy.mint(authority=authority, template=template)

@task
def validate(ark):
    return arkpy.validate(ark)

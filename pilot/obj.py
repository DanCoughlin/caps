class DigitalObject(object):

    def __init__(self, name, arkid, filetype, version, version_date, img=''):
        self.name = name
        self.arkid = arkid
        self.filetype = filetype
        self.version = version
        self.version_date = version_date
        self.img = img

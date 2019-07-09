from . import reflect

def name(tablename):
    arc = reflect()
    return arc['tables'][tablename]

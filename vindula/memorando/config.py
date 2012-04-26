# -*- coding: utf-8 -*-
try: # New CMF
    from Products.CMFCore.permissions import setDefaultRoles 
except ImportError: # Old CMF
    from Products.CMFCore.CMFCorePermissions import setDefaultRoles


PROJECTNAME = 'vindula.memorando'

try:
    from Products.CMFPlone.migrations import v2_1
except ImportError:
    HAS_PLONE21 = False
else:
    HAS_PLONE21 = True


# Permissions
DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"
setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ('Manager', 'Owner'))

product_globals = globals()


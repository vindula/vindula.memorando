from zope.i18nmessageid import MessageFactory

# Set up the i18n message factory for our package
MessageFactory = MessageFactory('vindula.memorando')

import logging
logger = logging.getLogger('vindula.memorando')
logger.debug('Installing Product')

import os, os.path
from App.Common import package_home
from Products.CMFCore import utils as cmfutils

try: # New CMF
    from Products.CMFCore import permissions as CMFCorePermissions 
except: # Old CMF
    from Products.CMFCore import CMFCorePermissions

from Products.CMFCore import DirectoryView
from Products.CMFPlone.utils import ToolInit
from Products.Archetypes.atapi import *
from Products.Archetypes import listTypes
from Products.Archetypes.utils import capitalize
from config import *

# first fix the validator
from Products.validation import validation

def initialize(context):
    import content

    # Initialize portal content
    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    cmfutils.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = content_types,
        permission         = DEFAULT_ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)  
        
        
               

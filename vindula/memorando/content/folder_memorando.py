# -*- coding: utf-8 -*-
from five import grok
from vindula.memorando import MessageFactory as _
from vindula.memorando.interfaces.interfaces import IFolderMemorando
from Products.ATContentTypes.content.folder import ATFolder

from AccessControl import ClassSecurityInfo

from zope.interface import implements
from Products.Archetypes.atapi import *
from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from vindula.memorando.config import *


FolderMemorando_schema =  ATFolder.schema.copy() + Schema((


))

finalizeATCTSchema(FolderMemorando_schema, folderish=True)

class FolderMemorando(ATFolder):
    """ Memorando Folder """
    security = ClassSecurityInfo()
    
    implements(IFolderMemorando)    
    portal_type = 'FolderMemorando'
    _at_rename_after_creation = True
    schema = FolderMemorando_schema


registerType(FolderMemorando, PROJECTNAME) 



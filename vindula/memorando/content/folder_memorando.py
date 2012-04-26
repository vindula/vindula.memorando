# -*- coding: utf-8 -*-
from five import grok
from Products.CMFCore.utils import getToolByName
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

class FolderMemorandoView(grok.View):
    grok.context(IFolderMemorando)
    grok.require('zope2.View')
    grok.name('folder_memorando_view')
    
    def getMemorandos(self):
        pc = getToolByName(self.context,'portal_catalog')
        memorandos = pc(     portal_type='Memorando',
                             review_state="published",
                             sort_on='getObjPositionInParent',)
        L = []
        if memorandos:
            for memorando in memorandos:
                D = {}
                D['titulo'] = memorando.Title
                D['url'] = memorando.getObject().absolute_url()
                L.append(D)
        return L
                
    

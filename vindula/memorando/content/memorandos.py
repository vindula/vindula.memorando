# -*- coding: utf-8 -*-
from five import grok
from Products.CMFCore.utils import getToolByName
from vindula.memorando import MessageFactory as _
from vindula.memorando.interfaces.interfaces import IMemorandos
from Products.ATContentTypes.content.folder import ATFolder

from AccessControl import ClassSecurityInfo

from zope.interface import implements
from Products.Archetypes.atapi import *
from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from vindula.memorando.config import *


Memorandos_schema =  ATFolder.schema.copy() + Schema((
    
    ImageField(
            name='image_memo',
            widget=ImageWidget(
                label=_(u"Imagem"),
                description=_(u"Imagem do Memorando.",),
            ),
        required=False,
    ),
    
    TextField(
            name='head_one',
            widget=StringWidget(
                label=_(u"Cabeçalho"),
                description=_("Insira o texto a ser adicionado no cabeçalho do Memorando.",),
                size = 50,
            ),
        required=False,
    ),
    
    TextField(
            name='head_two',
            widget=StringWidget(
                label=_(u"Sub Cabeçalho"),
                description=_(u"Insira o texto a ser adicionado no abaixo do cabeçalho do Memorando.",),
            ),
        required=False,
    ),                                                                                                  

))

finalizeATCTSchema(Memorandos_schema, folderish=True)

class Memorandos(ATFolder):
    """ Memorandos Folder """
    security = ClassSecurityInfo()
    
    implements(IMemorandos)    
    portal_type = 'Memorandos'
    _at_rename_after_creation = True
    schema = Memorandos_schema


registerType(Memorandos, PROJECTNAME) 

class MemorandosView(grok.View):
    grok.context(IMemorandos)
    grok.require('zope2.View')
    grok.name('memorandos_view')
    
    def getMemorandos(self):
        pc = getToolByName(self.context,'portal_catalog')
        memorandos = pc(portal_type='Memorando',
                        sort_on='getObjPositionInParent',
                        path = {'query': '/'.join(self.context.getPhysicalPath())}
                        )
        L = []
        if memorandos:
            for memorando in memorandos:
                D = {}
                D['titulo'] = memorando.Title
                D['url'] = memorando.getObject().absolute_url()
                L.append(D)
        return L
                
    

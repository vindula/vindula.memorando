# -*- coding: utf-8 -*-
from five import grok
from vindula.memorando import MessageFactory as _
from vindula.memorando.interfaces.interfaces import IMemorando
from Products.ATContentTypes.content.folder import ATFolder

from DateTime.DateTime import DateTime
from AccessControl import ClassSecurityInfo

from zope.interface import implements
from Products.Archetypes.atapi import *
from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from vindula.memorando.config import *


Memorando_schema =  ATFolder.schema.copy() + Schema((

    TextField(
            name='number',
            widget=StringWidget(
                label=_(u"Número"),
                description=_(u"Número do Memorando.",),
            ),
        required=False,
    ),
                                                
    DateTimeField('date',
        searchable = 1,
        required = 0,
        default_method = 'getDefaultTime',
        widget = CalendarWidget(
            label = 'Data'
        ),
    ),

    StringField(
            name='para',
            widget=SelectionWidget(
                label=_(u"Para:"),
                description=_("Selecione o usuário que deseja enviar o memorando."),
                
            ),
            required=0,
            vocabulary='voc_users',
    ),
    
    TextField(
            name='de',
            widget=StringWidget(
                label=_(u"De"),
                description=_(u"Destinatario.",),
            ),
        required=False,
    ),

    TextField(
            name='assunto',
            widget=StringWidget(
                label=_(u"Assunto"),
                description=_(u"Assunto.",),
            ),
        required=False,
    ),
    
    FileField(
            name='anexo',
            widget=FileWidget(
                label=_(u"Anexo"),
                description=_(u"anexe o memorando.",),
            ),
        required=False,
    ),

))

finalizeATCTSchema(Memorando_schema, folderish=False)

class Memorando(ATFolder):
    """ Memorando Folder """
    security = ClassSecurityInfo()
    
    implements(IMemorando)    
    portal_type = 'Memorando'
    _at_rename_after_creation = True
    schema = Memorando_schema

    def getDefaultTime(self):
        return DateTime()
    
    def voc_users(self):
        users = self.portal_membership.listMembers()
        L = []
        if users:
            for user in users:
                L.append(user.id)

        return L


registerType(Memorando, PROJECTNAME) 

class MemorandoView(grok.View):
    grok.context(IMemorando)
    grok.require('zope2.View')
    grok.name('view')
    


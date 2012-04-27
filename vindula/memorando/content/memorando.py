# -*- coding: utf-8 -*-
from five import grok
from vindula.memorando import MessageFactory as _
from vindula.memorando.interfaces.interfaces import IMemorando

from Products.ATContentTypes.content.folder import ATFolder
from Products.statusmessages.interfaces import IStatusMessage
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.Archetypes.atapi import *

from zope.app.component.hooks import getSite

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email.MIMEImage import MIMEImage
from email import Encoders

from DateTime.DateTime import DateTime
from datetime import datetime
from AccessControl import ClassSecurityInfo

from zope.interface import implements

from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget

from vindula.memorando.config import *


Memorando_schema =  ATFolder.schema.copy() + Schema((

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
                                                     
    TextField(
            name='number',
            widget=IntegerWidget(
                label=_(u"Número"),
                description=_(u"Número do Memorando.",),
                size = 10,
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
            name='to',
            widget=SelectionWidget(
                label=_(u"Para:"),
                description=_("Selecione o usuário que deseja enviar o memorando."),
                
            ),
            required=0,
            vocabulary='voc_users',
    ),
    
    StringField(
            name='email_to',
            widget=StringWidget(
                label=_(u"E-mail:"),
                description=_(u"Informe o e-mail do destinatário.",),
            ),
        required=False,
        validators = ('isEmail')
    ),
    
    TextField(
            name='from',
            widget=StringWidget(
                label=_(u"De:"),
                description=_(u"Informe o seu nome",),
            ),
        required=False,
    ),
    
    TextField(
            name='email_from',
            widget=StringWidget(
                label=_(u"E-mail:"),
                description=_(u"Informe o seu e-mail",),
            ),
        required=False,
        validators = ('isEmail')
    ),
    
    TextField(
            name='subject_memo',
            widget=StringWidget(
                label=_(u"Assunto"),
                description=_(u"Assunto do Memorando.",),
            ),
        required=False,
    ),
                                                     
    TextField(
            name='info_memo',
            default_content_type = 'text/restructured',
            default_output_type = 'text/x-html-safe',
            widget=RichWidget(
                label=_(u"Informações"),
                description=_(u"Insira as informações do Memorando."),
                rows="10",
            ),
            required=False,
    ),
                                                 

    FileField(
            name='attach',
            widget=FileWidget(
                label=_(u"Anexo"),
                description=_(u"anexe o memorando.",),
            ),
        required=False,
    ),

))

finalizeATCTSchema(Memorando_schema, folderish=False)
invisivel = {'view':'invisible','edit':'invisible',}
Memorando_schema['description'].widget.visible = invisivel 


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
    grok.name('memorando_view')
    
    def getAno(self):
        ano = datetime.now().strftime('%Y')
        return ano
    
    def getMemorando(self):
        obj = self.context
        D = {}
        D['titulo'] = obj.Title()
        if obj.getImage_memo() == '':
            D['imagem'] = ''
        else:
            D['imagem'] = obj.getImage_memo().absolute_url() + '/image_memo'
        D['cabecalho_um'] = obj.getHead_one()
        D['cabecalho_dois'] = obj.getHead_two()
        D['assunto'] = obj.getSubject_memo()
        D['descricao'] = obj.Description()
        D['numero'] = obj.getNumber()
        D['data'] = obj.getDate().strftime('%d/%m/%Y')
        D['hora'] = obj.getDate().strftime('%h:%m')
        D['para'] = obj.getTo()
        D['de'] = obj.getFrom()
        if obj.getAttach() == '':
            D['nome_arquivo'] = ''
        else:
            D['nome_arquivo'] = obj.getAttach().filename 
        D['anexo'] = obj.getAttach().absolute_url()
        D['info'] = obj.getInfo_memo()
        return D
    
    def envia_email(self):
        obj = self.context
        # Cria a mensagem raiz, configurando os campos necessarios para envio da mensagem.
        mensagem = MIMEMultipart('related')
        mensagem['Subject'] = obj.subject_memo()
        mensagem['From'] = obj.getEmail_from()
        mensagem['To'] = obj.getEmail_to()
        mensagem.preamble = 'This is a multi-part message in MIME format.'
        mensagem.attach(MIMEText(obj.getInfo_memo(), 'html', 'utf-8'))
        
        # Atacha os arquivos
        if obj.getAttach().data != '':
            parte = MIMEBase('application', 'octet-stream')
            parte.set_payload(obj.getAttach().data.data)
            Encoders.encode_base64(parte)
            parte.add_header('Content-Disposition', 'attachment; filename="%s"' % obj.getAttach().filename)
            
            mensagem.attach(parte)
        
        mail_de = mensagem['From']
        mail_para = mensagem['To']
        #Pegando SmtpHost Padrão do Plone
        smtp_host   = self.context.MailHost.smtp_host
        smtp_port   = self.context.MailHost.smtp_port
        smtp_userid = self.context.MailHost.smtp_uid
        smtp_pass   = self.context.MailHost.smtp_pwd
        server_all  = '%s:%s'%(smtp_host,smtp_port)

        smtp = smtplib.SMTP()
        try:
            smtp.connect(server_all)
            #Caso o Usuario e Senha estejam preenchdos faz o login
            if smtp_userid and smtp_pass:
                try:
                    smtp.ehlo()
                    smtp.starttls()
                    smtp.login(smtp_userid, smtp_pass)
                except:
                    smtp.login(smtp_userid, smtp_pass)
                    
            smtp.sendmail(mail_de, mail_para, mensagem.as_string())
            smtp.quit()
        except:
            return False

    def update(self):
        form = self.request.form
        submitted = form.get('form.submitted', False)
        if submitted:
            self.envia_email()
            IStatusMessage(self.request).addStatusMessage(_(u'E-Mail enviado com sucesso.'),"warning") 
        else:
            return None
        
        

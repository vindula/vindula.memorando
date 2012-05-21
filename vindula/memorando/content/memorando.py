# -*- coding: utf-8 -*-
from five import grok
from vindula.memorando import MessageFactory as _
from vindula.memorando.interfaces.interfaces import IMemorando
from vindula.myvindula.user import ModelsFuncDetails

from Products.CMFCore.utils import getToolByName
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
        validators = ('isEmail'),
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
Memorando_schema['email_from'].default_method = 'getEmailUser'
Memorando_schema['from'].default_method = 'getUser' 


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
        users = ModelsFuncDetails().get_allFuncDetails()
        L = [('usuario_fora_intranet','Usuário fora da Intranet')]
        result = ''
        
        if users is not None:
            for user in users:
                member_id = user.email
                member_name = user.name or member_id
                if member_id:
                    L.append((member_id, unicode(member_name)))
            
        return DisplayList((L))
    
    def getEmailUser(self):
        email = self.portal_membership.getAuthenticatedMember().email
        return email
    def getUser(self):
        user = self.portal_membership.getAuthenticatedMember().fullname
        return user

registerType(Memorando, PROJECTNAME)


class MemorandoView(grok.View):
    grok.context(IMemorando)
    grok.require('zope2.View')
    grok.name('memorando_view')
    
    def getAno(self):
        ano = datetime.now().strftime('%Y')
        return ano
    
    def getMemorando(self):
        pc = getToolByName(self.context,'portal_catalog')
        memorandos = pc(  portal_type='Memorandos',
                          review_state="published",
                          path = {'query': '/'.join(self.context.aq_parent.getPhysicalPath())
                                  } 
                          )
        D = {}
        if memorandos:
            for memorando in memorandos:
                memorando_obj = memorando.getObject()
                obj = self.context
                
                D['titulo'] = obj.Title()
                if memorando_obj.getImage_memo() == '':
                    D['imagem'] = ''
                else:
                    D['imagem'] = memorando_obj.getImage_memo().absolute_url() + '/image_memo'
                    try:
                        D['binario_imagem'] = memorando_obj.getImage_memo().data.data
                    except:
                        D['binario_imagem'] = memorando_obj.getImage_memo().data
                    D['nome_imagem'] = memorando_obj.getImage_memo().filename
                D['cabecalho_um'] = memorando_obj.getHead_one()
                D['cabecalho_dois'] = memorando_obj.getHead_two()
                D['descricao'] = obj.Description()
                D['numero'] = obj.getNumber()
                D['data'] = obj.getDate().strftime('%d/%m/%Y')
                D['hora'] = obj.getDate().strftime('%h:%m')
                if obj.getTo() == 'usuario_fora_intranet':
                    D['para'] = obj.getEmail_to()
                else:
                    D['para'] = obj.getTo()
                D['de'] = obj.getFrom()
                if obj.getAttach() == '':
                    D['nome_arquivo'] = ''
                else:
                    D['nome_arquivo'] = obj.getAttach().filename 
                D['anexo'] = obj.getAttach().absolute_url()
                D['info'] = obj.getInfo_memo()
        return D
    
    def geraHtmlMail(self):
        dict = self.getMemorando()
        ano = self.getAno()
        html = '<div id="content-fundo" style="background-color: #FFF !important;">\
                    <div id="image" style="float:left;margin:0px 10px 10px 10px;">\
                        <img src="cid:image1" width="120" height="150" />\
                    </div>\
                    <div>\
                        <h2 style="color:#6D6D6D; padding:10px 0px 0px 0px !important;">%s</h2>\
                        <h3 style="color:#6D6D6D;">%s</h3>\
                    </div>\
                    <br /><br /><br /><br /><br />\
                    <table border="1" width="100%%">\
                        <tr>\
                            <td>Número</td><td>%s/%s</td>\
                        </tr>\
                        <tr>\
                            <td>Data:</td>\
                            <td>%s</td>\
                        </tr>\
                        <tr>\
                            <td>Para:</td><td>%s</td>\
                        </tr>\
                        <tr>\
                            <td>De:</td><td>%s</td>\
                        </tr>\
                        <tr>\
                            <td>Assunto:</td><td>%s</td>\
                        </tr>\
                    </table>\
                    <br /><br />\
                    <div>%s</div>\
                </div>' % (dict['cabecalho_um'],dict['cabecalho_dois'],dict['numero'],ano,\
                             dict['data'],dict['para'],dict['de'],dict['titulo'],dict['info'])
        return html    
    
    def envia_email(self):
        memorando_obj = self.getMemorando()
        obj = self.context
        # Cria a mensagem raiz, configurando os campos necessarios para envio da mensagem.
        mensagem = MIMEMultipart('related')
        mensagem['Subject'] = obj.Title()
        mensagem['From'] = obj.getEmail_from()
        to = obj.getTo()
         
        if to == 'usuario_fora_intranet':
            mensagem['To'] = obj.getEmail_to()
        else:
            mensagem['To'] = to
        
        mensagem.preamble = 'This is a multi-part message in MIME format.'
        mensagem.attach(MIMEText(self.geraHtmlMail(), 'html', 'utf-8'))
        # Atacha os arquivos
        if memorando_obj['imagem'] != '':
            msgImage = MIMEImage(memorando_obj['binario_imagem'])
            # Define the image's ID as referenced above
            msgImage.add_header('Content-ID', '<image1>')
            mensagem.attach(msgImage)
            
        if obj.getAttach().data != '':
            parte = MIMEBase('application', 'octet-stream')
            try:
                parte.set_payload(obj.getAttach().data.data)
            except:
                parte.set_payload(obj.getAttach().data)
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
            print '------- Email enviado com sucesso -------'
        except:
            return False

    def update(self):
        form = self.request.form
        submitted = form.get('form.submitted', False)
        if submitted:
            self.envia_email()
            IStatusMessage(self.request).addStatusMessage(_(u'E-mail enviado com sucesso.'),"warning") 
        else:
            return None
        
        

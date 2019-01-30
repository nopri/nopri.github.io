#
# oerpapi
# Very simple OpenERP Client (XML-RPC API)
# (c) Noprianto <nop@noprianto.com>
# 2011,2014
# License: LGPL
# Version: 0.03
# Website: https://github.com/nopri/oerpapi
#
#
'''
Very simple OpenERP Client (XML-RPC API)

import oerpapi

#Create connection(s) to server
c = oerpapi.OErpClient('localhost')
c.connect()


#Working with database utils
#for more information, please refer to OErpDb class
d = c.get_db()
#create database test2 if not exists
if not d.exist('test2'):
    d.admin_password = 'myadminpassword'  #required for administrative tasks
    d.create('test2', True, 'en_US', 'test2') #with demo
#list database
print d.list()

#Login (database, user, password)
c.login('test2', 'admin', 'test2')


#Working with Model, for example res.partner
#for more information, please refer to OErpModel class
partner = c.get_model('res.partner')

#Add new partner
partner_id = partner.create({'name': 'test partner'})
print partner_id

#search for partner
search_data = ['|', ('name', 'ilike', 'test'), ('id', '>', 50)]
partner_search = partner.search(search_data)
print partner_search

#for each partner in search result, update partner data
partner.write(partner_search, {'website': 'http://domain.tld'})

#for each partner in search result, read partner data (selected fields)
partner_read = partner.read(partner_search, ['name', 'website'])
print partner_read


#Working with report
#for more information, please refer to OErpReport class
#for each partner in search result, generate PDF report, 
#    and save to /tmp/a.pdf
r = c.get_report('res.partner', partner_search)
report_result = r.get()
if report_result:
    import base64
    fout = '/tmp/a.pdf'
    f = open(fout, 'wb')
    f.write(base64.decodestring(report_result))
    f.close()
    
    import os
    print os.path.getsize(fout)
else:
    print 'failed to generate report'
'''

import xmlrpclib
import time


__version__ = '0.03'


class OErpModel:
    def __init__(self, client, model):
        self.client = client
        self.model = model
   
    def check_ids(self, ids):
        if not isinstance(ids, (list, tuple)):
            ids = [ids]
        return ids
    
    def check_context(self, context):
        if not isinstance(context, dict):
            context = {}
        return context
                
    def check_fields(self, fields):
        if not isinstance(fields, (list, tuple)):
            fields = []
        return fields
    
    def check_none(self, val, default=False):
        if val is None:
            val = default
        return val

    def create(self, values, context=None):
        return self.client.sock_object.execute(self.client.database, 
                                               self.client.uid, 
                                               self.client.password, 
                                               self.model, 'create', 
                                               values, 
                                               self.check_context(context))
        
    def write(self, ids, values, context=None):
        return self.client.sock_object.execute(self.client.database, 
                                               self.client.uid, 
                                               self.client.password, 
                                               self.model, 'write',
                                               self.check_ids(ids), 
                                               values, 
                                               self.check_context(context))
    
    def read(self, ids, fields=None, context=None):
        return self.client.sock_object.execute(self.client.database, 
                                               self.client.uid, 
                                               self.client.password, 
                                               self.model, 'read',
                                               self.check_ids(ids), 
                                               self.check_fields(fields), 
                                               self.check_context(context))

    def unlink(self, ids, context=None):
        return self.client.sock_object.execute(self.client.database, 
                                               self.client.uid, 
                                               self.client.password, 
                                               self.model, 'unlink',
                                               self.check_ids(ids), 
                                               self.check_context(context))
    
    def search(self, domain, offset=0, limit=None, order=None, context=None, 
               count=False):
        return self.client.sock_object.execute(self.client.database, 
                                               self.client.uid, 
                                               self.client.password, 
                                               self.model, 'search',
                                               domain,
                                               offset,
                                               self.check_none(limit),
                                               self.check_none(order),
                                               self.check_context(context),
                                               count)


class OErpReport:
    def __init__(self, client, model, ids, datas=False, context=False):
        self.client = client
        self.model = model
        self.ids = ids
        self.datas = datas
        self.context = context
        
        self.number_of_tries = 300
        self.delay_1 = 1
        self.delay_2 = 0.5
        self.report_type = 'pdf'
        self.data_id = 1
            
    def check_datas(self):
        if not isinstance(self.datas, dict):
            self.datas = {}
        if not self.datas.has_key('model'):
            self.datas['model'] = self.model
        if not self.datas.has_key('report_type'):
            self.datas['report_type'] = self.report_type                
        if not self.datas.has_key('id'):
            if self.ids:
                d_id = self.ids[0]
            else:
                d_id = self.data_id
            self.datas['id'] = d_id                
    
    def get(self):
        database = self.client.database
        uid = self.client.uid
        password = self.client.password
        
        self.check_datas()

        report_id =  self.client.sock_report.report(database, uid, password, 
                                              self.model, self.ids, 
                                              self.datas, self.context)
        time.sleep(self.delay_1)
        
        res = ''
        counter = 0        
        while True:
            report = self.client.sock_report.report_get(database, uid, 
                                                        password, report_id)
            state = report.get('state', False)
            if not state:
                time.sleep(self.delay_2)
                counter += 1
                if counter > self.number_of_tries:
                    break
            else:
                res = report.get('result', '')
                break

        return res
        

class OErpDb:
    def __init__(self, client):
        self.client = client
        self.admin_password = False
        
    def list(self, arg=False):
        return self.client.sock_db.list(arg)
    
    def list_lang(self):
        return self.client.sock_db.list_lang()
    
    def exist(self, name):
        return self.client.sock_db.db_exist(name)
        
    def change_admin_password(self, new_password):
        return self.client.sock_db.change_admin_password(self.admin_password,
                                                         new_password)

    def create(self, name, demo, lang, password):
        return self.client.sock_db.create_database(self.admin_password, 
                                                   name, demo, lang, 
                                                   password)
    
    def drop(self, name):
        return self.client.sock_db.drop(self.admin_password, name)
    
    def rename(self, name, new_name):
        return self.client.sock_db.rename(self.admin_password, 
                                          name, new_name)
    
    def duplicate(self, name, target_name):
        return self.client.sock_db.duplicate_database(self.admin_password, 
                                          name, target_name)
    
    def dump(self, name):
        return self.client.sock_db.dump(self.admin_password, name)
    
    def restore(self, name, data):
        return self.client.sock_db.restore(self.admin_password, name, data)
    
        
class OErpClient:
    def __init__(self, host, port=8069, data=None):
        self.host = host
        self.port = port
        self.data = data

        self.database = False
        self.user = False
        self.password = False
        
        self.resource_common = '/xmlrpc/common'
        self.resource_object = '/xmlrpc/object'
        self.resource_report = '/xmlrpc/report'
        self.resource_db = '/xmlrpc/db'
        self.protocol = 'http://'
        
        self.uid = False
        self.sock_common = False
        self.sock_object = False
        self.sock_report = False
        self.sock_db = False

    def create_url(self, resource):
        return '%s%s:%s%s' %(self.protocol, self.host, self.port, resource)
    
    def connect(self, **args):
        url = self.create_url(self.resource_common)
        self.sock_common = xmlrpclib.ServerProxy(url)

        url = self.create_url(self.resource_object)
        self.sock_object = xmlrpclib.ServerProxy(url)

        url = self.create_url(self.resource_report)
        self.sock_report = xmlrpclib.ServerProxy(url)

        url = self.create_url(self.resource_db)
        self.sock_db = xmlrpclib.ServerProxy(url)
        
    def login(self, database, user, password):
        self.database = database
        self.user = user
        self.password = password
        
        self.uid = self.sock_common.login(self.database, self.user, 
                                          self.password)
            
    def version(self):
        return self.sock_common.version()
    
    def server_environment(self):
        return self.sock_common.get_server_environment()

    def check_connectivity(self):
        return self.sock_common.check_connectivity()

    def get_model(self, model):
        o = OErpModel(self, model)
        return o
    
    def get_report(self, model, ids, datas=False, context=False):
        o = OErpReport(self, model, ids, datas, context)
        return o
        
    def get_db(self):
        o = OErpDb(self)
        return o


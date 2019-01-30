#
# oerpapi2.py
# Very simple Odoo/OpenERP Client (XML-RPC API) version 2
# for Odoo version 8 and later
#
# (c) Noprianto <nop@noprianto.com>
# 2011,2014,2017
# License: LGPL
# Version: 0.04
# Website: https://github.com/nopri/code
#
# Note:
# 1. This is not compatible with oerpapi.py (for earlier versions of
#    Odoo/OpenERP)
# 2. Only few features of new API are supported (still using old method)
# 3. Report (OErpReport) has been (temporarily?) removed
#
'''
Very simple Odoo/OpenERP Client (XML-RPC API) version 2

import oerpapi2


#Create connection to server
c = oerpapi2.OErpClient('http://localhost:8069')

#Version information
c.version()


#Working with database utils
#for more information, please refer to OErpDb class
d = c.get_db()

#Create a new database, test2, if not exists
if not d.exist('test2'):
    d.admin_password = 'myadminpassword'  #required for administrative tasks
    d.create('test2', True, 'en_US', 'test2') #with demo

#List databases
print d.list()

#Drop a database, with admin_password set
d.drop('test2')

#Duplicate a database, with admin_password set
d.duplicate('test2', 'test3')

#Rename a database, with admin_password set
d.rename('test3', 'test4')

#Dump a database, with admin_password set, to Base64-encoded ZIP format
x = d.dump('test4')

#Restore a database, with admin_password set,
#from Base64-encoded ZIP format
d.restore('test5', x)

#Change admin password, with admin_password set
#Please then manually set admin_password again
d.change_admin_password('mynewpassword')


#Login (database, user, password)
c.login('test2', 'admin', 'test2')


#Working with Model, for example res.partner
#for more information, please refer to OErpModel class
partner = c.get_model('res.partner')

#Create a new partner
partner_id = partner.create({'name': 'test partner'})
print partner_id

#Search partners
search_data = ['|', ('name', 'ilike', 'test'), ('id', '>', 50)]
partner_search = partner.search(search_data)
print partner_search

#For each partner in search result, update partner data
partner.write(partner_search, {'website': 'http://domain.tld'})

#For each partner in search result, read partner data (selected fields)
partner_read = partner.read(partner_search, ['name', 'website'])
print partner_read

#Delete a partner
partner.unlink(partner_id)
'''

import xmlrpclib


__version__ = '0.04'


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
            self.client.uid, self.client.password, self.model, 'create',
            values, self.check_context(context))

    def write(self, ids, values, context=None):
        return self.client.sock_object.execute(self.client.database,
            self.client.uid, self.client.password, self.model, 'write',
            self.check_ids(ids), values, self.check_context(context))

    def read(self, ids, fields=None, context=None):
        return self.client.sock_object.execute(self.client.database,
            self.client.uid, self.client.password, self.model, 'read',
            self.check_ids(ids), self.check_fields(fields),
            self.check_context(context))

    def unlink(self, ids, context=None):
        return self.client.sock_object.execute(self.client.database,
            self.client.uid, self.client.password, self.model, 'unlink',
            self.check_ids(ids), self.check_context(context))

    def search(self, domain, offset=0, limit=None, order=None,
        context=None):
        return self.client.sock_object.execute(self.client.database,
            self.client.uid, self.client.password, self.model, 'search',
            domain, offset, self.check_none(limit),
            self.check_none(order), self.check_context(context))


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
        return self.client.sock_db.change_admin_password(
            self.admin_password, new_password)

    def create(self, name, demo, lang, password):
        return self.client.sock_db.create_database(self.admin_password,
            name, demo, lang, password)

    def drop(self, name):
        return self.client.sock_db.drop(self.admin_password, name)

    def rename(self, name, new_name):
        return self.client.sock_db.rename(self.admin_password,
                                          name, new_name)

    def duplicate(self, name, target_name):
        return self.client.sock_db.duplicate_database(self.admin_password,
                                          name, target_name)

    def dump(self, name, backup_format='zip'):
        return self.client.sock_db.dump(self.admin_password, name,
            backup_format)

    def restore(self, name, data):
        return self.client.sock_db.restore(self.admin_password, name, data)


class OErpClient:
    def __init__(self, url, data=None):
        self.url = url
        self.data = data

        self.database = False
        self.user = False
        self.password = False
        self.uid = False

        self.resource_common = '/xmlrpc/2/common'
        self.resource_object = '/xmlrpc/2/object'
        self.resource_report = '/xmlrpc/2/report'
        self.resource_db = '/xmlrpc/2/db'

        self.sock_common = xmlrpclib.ServerProxy(
            self.create_url(self.resource_common))
        self.sock_object = xmlrpclib.ServerProxy(
            self.create_url(self.resource_object))
        self.sock_report = xmlrpclib.ServerProxy(
            self.create_url(self.resource_report))
        self.sock_db = xmlrpclib.ServerProxy(
            self.create_url(self.resource_db))

    def create_url(self, resource):
        return '%s%s' %(self.url, resource)

    def login(self, database, user, password, env={}):
        self.database = database
        self.user = user
        self.password = password

        self.uid = self.sock_common.authenticate(self.database,
            self.user, self.password, env)

    def version(self):
        return self.sock_common.version()

    def get_model(self, model):
        o = OErpModel(self, model)
        return o

    def get_db(self):
        o = OErpDb(self)
        return o


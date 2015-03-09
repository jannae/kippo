"""
 Kippo_Mongodb
 Mongodb support for Kippo honeypot
 src: https://github.com/aabed/kippo_mongodb

 Uncomment the mongodb config from kippo.cfg to begin collecting.

 Run `mongo create.js` to deploy.

 Retrieve the logs from mongodb using mongoshell

     use kippo
     db.log.find()
"""
from kippo.core import dblog
from twisted.python import log
from pymongo import MongoClient
from datetime import datetime
import uuid


class DBLogger(dblog.DBLogger):
    def start(self, cfg):
        print 'mongodb DBLogger start'

        server = cfg.get('database_mongodb', 'server')
        port = cfg.get('database_mongodb', 'port')
        username = cfg.get('database_mongodb', 'username')
        password = cfg.get('database_mongodb', 'password')
        database = cfg.get('database_mongodb', 'database')
        collection = cfg.get('database_mongodb', 'collection')

        client = MongoClient("mongodb://{0}:{1}@{2}:{3}/{4}".format(username, password, server, int(port), database))
        dbase = client.get_default_database()
        self.collection = dbase[collection]
        self.meta = {}

    # We have to return an unique ID
    def createSession(self, peerIP, peerPort, hostIP, hostPort):
        session = uuid.uuid4().hex
        startTime = datetime.now().isoformat()
        self.meta[session] = {
            'session':session,
            'startTime':startTime,
            'endTime':'',
            'peerIP': peerIP,
            'peerPort': peerPort,
            'hostIP': hostIP,
            'hostPort': hostPort,
            'loggedin': None,
            'credentials':[],
            'commands':[],
            "unknownCommands":[],
            'urls':[],
            'version': None,
            'ttylog': None
        }
        return session

    def handleConnectionLost(self, session, args):
        log.msg('publishing metadata to mongodb')
        meta = self.meta[session]
        ttylog = self.ttylog(session)
        self.meta[session]['endTime'] = datetime.now().isoformat()
        if ttylog:
            meta['ttylog'] = ttylog.encode('hex')
        self.collection.insert(meta)

    def handleLoginFailed(self, session, args):
        unm, pwd = args['username'], args['password']
        self.meta[session]['credentials'].append((unm, pwd))

    def handleLoginSucceeded(self, session, args):
        unm, pwd = args['username'], args['password']
        self.meta[session]['startTime'] = datetime.now().isoformat()
        self.meta[session]['loggedin'] = (unm, pwd)

    def handleCommand(self, session, args):
        cmds = args['input']
        self.meta[session]['commands'].append(cmds)

    def handleUnknownCommand(self, session, args):
        ucmds = args['input']
        self.meta[session]['unknownCommands'].append(ucmds)

    def handleInput(self, session, args):
        pass

    def handleTerminalSize(self, session, args):
        pass

    def handleClientVersion(self, session, args):
        ver = args['version']
        self.meta[session]['version'] = ver

    def handleFileDownload(self, session, args):
        url = args['url']
        self.meta[session]['urls'].append(url)

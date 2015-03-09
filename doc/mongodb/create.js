/***************
 *
 * Kippo_Mongodb
 * Mongodb support for Kippo honeypot
 * src: https://github.com/aabed/kippo_mongodb
 *
 * Uncomment the mongodb config from kippo.cfg to begin collecting.
 *
 * Run `mongo create.js` to deploy.
 *
 * Retrieve the logs from mongodb using mongoshell
 *
 *     use kippo
 *     db.log.find()
 *
 **************/

new Mongo()
conn = new Mongo()
db = conn.getDB("kippo")

// You should edit the pwd value. Obviously.
db.createUser({
    user: "kippo",
    pwd: "kippo_pass",
    roles: [{
        role: "userAdmin",
        db: "kippo"
    }]
})

db.createCollection("log")

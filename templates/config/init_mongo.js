/* These are Mongo Shell commands, as documented at https://docs.mongodb.com/manual/mongo/ */

db.createUser(
    {
        user: "${MONGO_USER}",
        pwd: "${MONGO_PASSWORD}",
        roles:[
            {
                role: "readWrite",
                db:   "${MONGO_DB}",
            }
        ]
    }
);

db.createCollection("${MONGO_COLLECTION}");

db.getCollection("${MONGO_COLLECTION}").insert({
    "user" : "guest",
    "am" : {
        "read_groups" : [
            "public"
        ],
        "write_groups" : [],
        "admin_access" : false
    },
    "password" : "$argon2i$v=19$m=102400,t=2,p=8$S4lRqpWSck7JGWMMgTDGGA$MRa3VgoE5o1qZET5/yBRBA"
});
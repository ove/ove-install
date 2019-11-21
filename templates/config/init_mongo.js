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

db.createCollection('auth');

db.getCollection('auth').insert({
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
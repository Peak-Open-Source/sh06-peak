db.createUser({
    user: "proteinLovers",
    pwd: "protein-Lovers2",
    roles: [
        {
            role: "readWrite",
            db: "protein_collection"
        }
    ]
});
//var jsonData = cat('/docker-entrypoint-initdb.d/init-mongo.json');
//var data = JSON.parse(jsonData);

// db.sampledocuments.insert(data);

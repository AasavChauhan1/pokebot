// MongoDB initialization script
db = db.getSiblingDB('pokebot');

// Create collections with validation
db.createCollection('users', {
   validator: {
      $jsonSchema: {
         bsonType: 'object',
         required: ['user_id'],
         properties: {
            user_id: {
               bsonType: 'long',
               description: 'Telegram user ID - required'
            },
            trainer_level: {
               bsonType: 'int',
               minimum: 1,
               maximum: 100
            },
            coins: {
               bsonType: 'int',
               minimum: 0
            }
         }
      }
   }
});

db.createCollection('pokemon', {
   validator: {
      $jsonSchema: {
         bsonType: 'object',
         required: ['pokemon_id', 'owner_id', 'species'],
         properties: {
            owner_id: {
               bsonType: 'long',
               description: 'Owner user ID - required'
            },
            level: {
               bsonType: 'int',
               minimum: 1,
               maximum: 100
            }
         }
      }
   }
});

db.createCollection('spawns');
db.createCollection('battles');
db.createCollection('trades');

print('MongoDB collections created successfully!');

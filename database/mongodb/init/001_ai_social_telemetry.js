const dbName = process.env.MONGO_INITDB_DATABASE || "all_in_one";
db = db.getSiblingDB(dbName);

function createValidatedCollection(name, validator) {
  db.createCollection(name, {
    validator: { $jsonSchema: validator },
    validationLevel: "strict",
    validationAction: "error",
  });
}

createValidatedCollection("ai_memory", {
  bsonType: "object",
  required: ["user_id", "memory_type", "consent_scope", "created_at"],
  properties: {
    user_id: { bsonType: "string", description: "UUID identity.users.id" },
    memory_type: { enum: ["preference", "context", "summary", "moderation"] },
    content_encrypted: { bsonType: "string" },
    consent_scope: { bsonType: "string" },
    retention_until: { bsonType: "date" },
    created_at: { bsonType: "date" },
    metadata: { bsonType: "object" },
  },
});
db.ai_memory.createIndex({ user_id: 1, created_at: -1 });
db.ai_memory.createIndex({ retention_until: 1 }, { expireAfterSeconds: 0 });

createValidatedCollection("social_videos", {
  bsonType: "object",
  required: ["user_id", "asset_key", "status", "created_at"],
  properties: {
    user_id: { bsonType: "string" },
    asset_key: { bsonType: "string" },
    caption: { bsonType: "string" },
    commission_links: { bsonType: "array", items: { bsonType: "string" } },
    moderation: { bsonType: "object" },
    views: { bsonType: "long" },
    likes: { bsonType: "long" },
    status: { bsonType: "string" },
    created_at: { bsonType: "date" },
  },
});
db.social_videos.createIndex({ user_id: 1, created_at: -1 });

createValidatedCollection("influencer_metrics", {
  bsonType: "object",
  required: ["user_id", "period", "created_at"],
  properties: {
    user_id: { bsonType: "string" },
    period: { bsonType: "string" },
    clicks: { bsonType: "long" },
    conversions: { bsonType: "long" },
    commissions_brl: { bsonType: "decimal" },
    created_at: { bsonType: "date" },
  },
});
db.influencer_metrics.createIndex({ user_id: 1, period: 1 }, { unique: true });

createValidatedCollection("telemetry_logs", {
  bsonType: "object",
  required: ["user_id", "source", "occurred_at", "payload"],
  properties: {
    user_id: { bsonType: "string" },
    source: {
      enum: ["rider_gps", "mobility_gps", "vision_sensor", "home_sensor", "medical_device"],
    },
    device_id: { bsonType: "string" },
    occurred_at: { bsonType: "date" },
    location: {
      bsonType: "object",
      properties: {
        type: { enum: ["Point"] },
        coordinates: { bsonType: "array", minItems: 2, maxItems: 2 },
      },
    },
    payload: { bsonType: "object" },
    retention_until: { bsonType: "date" },
  },
});
db.telemetry_logs.createIndex({ location: "2dsphere" });
db.telemetry_logs.createIndex({ user_id: 1, occurred_at: -1 });
db.telemetry_logs.createIndex({ retention_until: 1 }, { expireAfterSeconds: 0 });

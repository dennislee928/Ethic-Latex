import { integer, real, sqliteTable, text } from "drizzle-orm/sqlite-core";

// One value-alignment profile per user: the boundaries the guardian enforces.
export const profiles = sqliteTable("profiles", {
  id: text("id").primaryKey(),
  name: text("name").notNull().default("default"),
  riskThreshold: real("risk_threshold").notNull().default(40),
  protectedTopics: text("protected_topics", { mode: "json" })
    .$type<string[]>()
    .notNull()
    .default([]),
  autoApproveTools: text("auto_approve_tools", { mode: "json" })
    .$type<string[]>()
    .notNull()
    .default([]),
  updatedAt: integer("updated_at", { mode: "timestamp" }).notNull(),
});

// Every gate decision the agent makes, for the transparency panel.
export const decisions = sqliteTable("decisions", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  profileId: text("profile_id").notNull(),
  toolName: text("tool_name").notNull(),
  actionText: text("action_text").notNull(),
  riskScore: real("risk_score").notNull(),
  ethicalValue: real("ethical_value").notNull(),
  erhSatisfied: integer("erh_satisfied", { mode: "boolean" }),
  estimatedExponent: real("estimated_exponent"),
  verdict: text("verdict", {
    enum: ["auto_approved", "human_approved", "blocked"],
  }).notNull(),
  createdAt: integer("created_at", { mode: "timestamp" }).notNull(),
});

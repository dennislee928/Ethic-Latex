CREATE TABLE `decisions` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`profile_id` text NOT NULL,
	`tool_name` text NOT NULL,
	`action_text` text NOT NULL,
	`risk_score` real NOT NULL,
	`ethical_value` real NOT NULL,
	`erh_satisfied` integer,
	`estimated_exponent` real,
	`verdict` text NOT NULL,
	`created_at` integer NOT NULL
);
--> statement-breakpoint
CREATE TABLE `profiles` (
	`id` text PRIMARY KEY NOT NULL,
	`name` text DEFAULT 'default' NOT NULL,
	`risk_threshold` real DEFAULT 40 NOT NULL,
	`protected_topics` text DEFAULT '[]' NOT NULL,
	`auto_approve_tools` text DEFAULT '[]' NOT NULL,
	`updated_at` integer NOT NULL
);

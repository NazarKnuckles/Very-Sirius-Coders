CREATE TABLE IF NOT EXISTS "project_statuses" (
	"id" SERIAL,
	"name" VARCHAR(50) NOT NULL UNIQUE,
	PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "roles" (
	"id" SERIAL,
	"name" VARCHAR(50) NOT NULL UNIQUE,
	PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "programming_languages" (
	"id" SERIAL,
	"name" VARCHAR(50) NOT NULL UNIQUE,
	PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "submission_statuses" (
	"id" SERIAL,
	"name" VARCHAR(50) NOT NULL UNIQUE,
	PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "difficulties" (
	"id" SERIAL,
	"name" VARCHAR(50) NOT NULL UNIQUE,
	"base_points" INTEGER NOT NULL CHECK (base_points > 0),
	PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "categories" (
	"id" SERIAL,
	"name" VARCHAR(100) NOT NULL UNIQUE,
	PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "users" (
	"id" SERIAL,
	"username" VARCHAR(100) NOT NULL UNIQUE,
	"email" VARCHAR(150) NOT NULL UNIQUE,
	"password_hash" VARCHAR(255) NOT NULL,
	"level" INTEGER DEFAULT 1 CHECK (level > 0),
	"experience_points" INTEGER DEFAULT 0 CHECK (experience_points >= 0),
	"created_at" TIMESTAMP DEFAULT now(),
	PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "achievements" (
	"id" SERIAL,
	"name" VARCHAR(100) NOT NULL UNIQUE,
	"description" TEXT,
	"icon_url" VARCHAR(255),
	PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "user_achievements" (
	"id" SERIAL,
	"user_id" INTEGER NOT NULL,
	"achievement_id" INTEGER NOT NULL,
	"earned_at" TIMESTAMP DEFAULT now(),
	PRIMARY KEY("id"),
	UNIQUE("user_id", "achievement_id")
);

CREATE TABLE IF NOT EXISTS "tasks" (
	"id" SERIAL,
	"title" VARCHAR(200) NOT NULL,
	"description" TEXT NOT NULL,
	"difficulty_id" INTEGER,
	"time_limit_ms" INTEGER CHECK (time_limit_ms > 0),
	"memory_limit_kb" INTEGER CHECK (memory_limit_kb > 0),
	"author_id" INTEGER,
	"created_at" TIMESTAMP DEFAULT now(),
	PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "task_categories_link" (
	"task_id" INTEGER NOT NULL,
	"category_id" INTEGER NOT NULL,
	PRIMARY KEY("task_id", "category_id")
);

CREATE TABLE IF NOT EXISTS "test_cases" (
	"id" SERIAL,
	"task_id" INTEGER NOT NULL,
	"input_data" TEXT NOT NULL,
	"expected_output" TEXT NOT NULL,
	"is_hidden" BOOLEAN DEFAULT false,
	PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "submissions" (
	"id" SERIAL,
	"task_id" INTEGER NOT NULL,
	"user_id" INTEGER NOT NULL,
	"source_code" TEXT NOT NULL,
	"language_id" INTEGER NOT NULL,
	"status_id" INTEGER NOT NULL,
	"execution_time_ms" INTEGER,
	"memory_used_kb" INTEGER,
	"submitted_at" TIMESTAMP DEFAULT now(),
	PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "published_solutions" (
	"id" SERIAL,
	"submission_id" INTEGER NOT NULL UNIQUE,
	"author_id" INTEGER NOT NULL,
	"description" TEXT,
	"upvotes" INTEGER DEFAULT 0 CHECK (upvotes >= 0),
	"published_at" TIMESTAMP DEFAULT now(),
	PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "comments" (
	"id" SERIAL,
	"user_id" INTEGER NOT NULL,
	"task_id" INTEGER,
	"solution_id" INTEGER,
	"content" TEXT NOT NULL,
	"created_at" TIMESTAMP DEFAULT now(),
	PRIMARY KEY("id"),
	CHECK (task_id IS NOT NULL OR solution_id IS NOT NULL)
);

CREATE TABLE IF NOT EXISTS "courses" (
	"id" SERIAL,
	"title" VARCHAR(200) NOT NULL,
	"description" TEXT,
	"author_id" INTEGER NOT NULL,
	"created_at" TIMESTAMP DEFAULT now(),
	PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "course_modules" (
	"id" SERIAL,
	"course_id" INTEGER NOT NULL,
	"title" VARCHAR(200) NOT NULL,
	"order_index" INTEGER NOT NULL CHECK (order_index >= 0),
	PRIMARY KEY("id"),
	UNIQUE("course_id", "order_index")
);

CREATE TABLE IF NOT EXISTS "course_tasks" (
	"id" SERIAL,
	"module_id" INTEGER NOT NULL,
	"task_id" INTEGER NOT NULL,
	"order_index" INTEGER NOT NULL CHECK (order_index >= 0),
	PRIMARY KEY("id"),
	UNIQUE("module_id", "order_index"),
	UNIQUE("module_id", "task_id")
);

CREATE TABLE IF NOT EXISTS "course_enrollments" (
	"id" SERIAL,
	"user_id" INTEGER NOT NULL,
	"course_id" INTEGER NOT NULL,
	"progress_percent" INTEGER DEFAULT 0 CHECK (progress_percent >= 0 AND progress_percent <= 100),
	"enrolled_at" TIMESTAMP DEFAULT now(),
	PRIMARY KEY("id"),
	UNIQUE("user_id", "course_id")
);

CREATE TABLE IF NOT EXISTS "projects" (
	"id" SERIAL,
	"title" VARCHAR(150) NOT NULL,
	"description" TEXT,
	"status_id" INTEGER,
	"repository_url" VARCHAR(255),
	"created_by" INTEGER NOT NULL,
	"created_at" TIMESTAMP DEFAULT now(),
	PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "project_members" (
	"id" SERIAL,
	"project_id" INTEGER NOT NULL,
	"user_id" INTEGER NOT NULL,
	"role_id" INTEGER NOT NULL,
	"joined_at" TIMESTAMP DEFAULT now(),
	PRIMARY KEY("id"),
	UNIQUE("project_id", "user_id")
);

CREATE TABLE IF NOT EXISTS "project_vacancies" (
	"id" SERIAL,
	"project_id" INTEGER NOT NULL,
	"role_id" INTEGER NOT NULL,
	"description" TEXT,
	"is_active" BOOLEAN DEFAULT true,
	PRIMARY KEY("id")
);

ALTER TABLE "tasks"
ADD FOREIGN KEY("difficulty_id") REFERENCES "difficulties"("id")
ON UPDATE CASCADE ON DELETE SET NULL; рестрикт

ALTER TABLE "tasks"
ADD FOREIGN KEY("author_id") REFERENCES "users"("id")
ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE "user_achievements"
ADD FOREIGN KEY("user_id") REFERENCES "users"("id")
ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE "user_achievements"
ADD FOREIGN KEY("achievement_id") REFERENCES "achievements"("id")
ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE "task_categories_link"
ADD FOREIGN KEY("task_id") REFERENCES "tasks"("id")
ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE "task_categories_link"
ADD FOREIGN KEY("category_id") REFERENCES "categories"("id")
ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE "test_cases"
ADD FOREIGN KEY("task_id") REFERENCES "tasks"("id")
ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE "submissions"
ADD FOREIGN KEY("task_id") REFERENCES "tasks"("id")
ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE "submissions"
ADD FOREIGN KEY("user_id") REFERENCES "users"("id")
ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE "submissions"
ADD FOREIGN KEY("language_id") REFERENCES "programming_languages"("id")
ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE "submissions"
ADD FOREIGN KEY("status_id") REFERENCES "submission_statuses"("id")
ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE "published_solutions"
ADD FOREIGN KEY("submission_id") REFERENCES "submissions"("id")
ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE "published_solutions"
ADD FOREIGN KEY("author_id") REFERENCES "users"("id")
ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE "comments"
ADD FOREIGN KEY("user_id") REFERENCES "users"("id")
ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE "comments"
ADD FOREIGN KEY("task_id") REFERENCES "tasks"("id")
ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE "comments"
ADD FOREIGN KEY("solution_id") REFERENCES "published_solutions"("id")
ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE "courses"
ADD FOREIGN KEY("author_id") REFERENCES "users"("id")
ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE "course_modules"
ADD FOREIGN KEY("course_id") REFERENCES "courses"("id")
ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE "course_tasks"
ADD FOREIGN KEY("module_id") REFERENCES "course_modules"("id")
ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE "course_tasks"
ADD FOREIGN KEY("task_id") REFERENCES "tasks"("id")
ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE "course_enrollments"
ADD FOREIGN KEY("user_id") REFERENCES "users"("id")
ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE "course_enrollments"
ADD FOREIGN KEY("course_id") REFERENCES "courses"("id")
ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE "projects"
ADD FOREIGN KEY("status_id") REFERENCES "project_statuses"("id")
ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE "projects"
ADD FOREIGN KEY("created_by") REFERENCES "users"("id")
ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE "project_members"
ADD FOREIGN KEY("project_id") REFERENCES "projects"("id")
ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE "project_members"
ADD FOREIGN KEY("user_id") REFERENCES "users"("id")
ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE "project_members"
ADD FOREIGN KEY("role_id") REFERENCES "roles"("id")
ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE "project_vacancies"
ADD FOREIGN KEY("project_id") REFERENCES "projects"("id")
ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE "project_vacancies"
ADD FOREIGN KEY("role_id") REFERENCES "roles"("id")
ON UPDATE CASCADE ON DELETE RESTRICT;
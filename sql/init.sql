CREATE TABLE "Roles"
(
    "id"   SERIAL PRIMARY KEY,
    "name" varchar
);

CREATE TABLE "Status"
(
    "id"   SERIAL PRIMARY KEY,
    "name" varchar
);

CREATE TABLE "Priority"
(
    "id"   SERIAL PRIMARY KEY,
    "name" varchar
);

CREATE TABLE "FieldType"
(
    "id"   SERIAL PRIMARY KEY,
    "name" varchar
);

CREATE TABLE "ReminderType"
(
    "id"   SERIAL PRIMARY KEY,
    "name" varchar
);

CREATE TABLE "Connections"
(
    "id"   SERIAL PRIMARY KEY,
    "name" varchar
);

CREATE TABLE "Users"
(
    "id"            SERIAL PRIMARY KEY,
    "email"          varchar UNIQUE NOT NULL UNIQUE,
    "nickname"      varchar        NOT NULL UNIQUE,
    "password_hash" varchar        NOT NULL
);

CREATE TABLE "Teams"
(
    "id"   SERIAL PRIMARY KEY,
    "name" varchar NOT NULL
);

CREATE TABLE "Projects"
(
    "id"      SERIAL PRIMARY KEY,
    "team_id" integer NOT NULL,
    "name"    varchar NOT NULL
);

CREATE TABLE "Streams"
(
    "id"         SERIAL PRIMARY KEY,
    "project_id" integer NOT NULL,
    "name"       varchar NOT NULL
);

CREATE TABLE "Goals"
(
    "id"          SERIAL PRIMARY KEY,
    "stream_id"   integer NOT NULL,
    "name"        varchar NOT NULL,
    "description" text,
    "deadline"    timestamp -- ИСПРАВЛЕНО: datetime → timestamp
);

CREATE TABLE "Tasks"
(
    "id"          SERIAL PRIMARY KEY,
    "stream_id"   integer NOT NULL,
    "name"        varchar,
    "description" text,
    "status_id"   integer,
    "priority_id" integer,
    "start_date"  timestamp,
    "deadline"    timestamp
);

CREATE TABLE "UserTeam"
(
    "id"      SERIAL PRIMARY KEY,
    "user_id" integer NOT NULL,
    "team_id" integer NOT NULL,
    "role_id" integer
);

CREATE TABLE "UserTask"
(
    "id"      SERIAL PRIMARY KEY,
    "user_id" integer NOT NULL,
    "task_id" integer NOT NULL
);

CREATE TABLE "TaskRelations"
(
    "id"            SERIAL PRIMARY KEY,
    "task_id_1"     integer NOT NULL,
    "task_id_2"     integer NOT NULL,
    "connection_id" integer NOT NULL
);

CREATE TABLE "Tags"
(
    "id"         SERIAL PRIMARY KEY,
    "name"       varchar NOT NULL,
    "created_at" timestamp
);

CREATE TABLE "TagTeam"
(
    "id"      SERIAL PRIMARY KEY,
    "tag_id"  integer NOT NULL,
    "team_id" integer NOT NULL
);

CREATE TABLE "TagTask"
(
    "id"      SERIAL PRIMARY KEY,
    "tag_id"  integer NOT NULL,
    "task_id" integer NOT NULL
);

CREATE TABLE "Fields"
(
    "id"            SERIAL PRIMARY KEY,
    "team_id"       integer NOT NULL,
    "field_name"    varchar NOT NULL,
    "field_type_id" integer
);

CREATE TABLE "FieldValues"
(
    "id"       SERIAL PRIMARY KEY,
    "field_id" integer NOT NULL,
    "task_id"  integer NOT NULL,
    "value"    text
);

CREATE TABLE "TaskHistory"
(
    "id"            SERIAL PRIMARY KEY,
    "task_id"       integer NOT NULL,
    "new_status_id" integer,
    "changed_at"    timestamp
);

CREATE TABLE "TaskReminders"
(
    "id"               SERIAL PRIMARY KEY,
    "task_id"          integer NOT NULL,
    "user_id"          integer NOT NULL,
    "reminder_type_id" integer
);

-- Остальная часть скрипта (индексы, комментарии, внешние ключи) остается без изменений

CREATE UNIQUE INDEX ON "Roles" ("id");
CREATE UNIQUE INDEX ON "Status" ("id");
CREATE UNIQUE INDEX ON "Priority" ("id");
CREATE UNIQUE INDEX ON "FieldType" ("id");
CREATE UNIQUE INDEX ON "ReminderType" ("id");
CREATE UNIQUE INDEX ON "Connections" ("id");
CREATE UNIQUE INDEX ON "Users" ("id");
CREATE UNIQUE INDEX ON "Teams" ("id");
CREATE UNIQUE INDEX ON "Projects" ("id");
CREATE UNIQUE INDEX ON "Streams" ("id");
CREATE UNIQUE INDEX ON "Goals" ("id");
CREATE UNIQUE INDEX ON "Tasks" ("id");
CREATE UNIQUE INDEX ON "UserTeam" ("id");
CREATE UNIQUE INDEX ON "UserTask" ("id");
CREATE UNIQUE INDEX ON "TaskRelations" ("id");
CREATE UNIQUE INDEX ON "Tags" ("id");
CREATE UNIQUE INDEX ON "TagTeam" ("id");
CREATE UNIQUE INDEX ON "TagTask" ("id");
CREATE UNIQUE INDEX ON "Fields" ("id");
CREATE UNIQUE INDEX ON "FieldValues" ("id");
CREATE UNIQUE INDEX ON "TaskHistory" ("id");
CREATE UNIQUE INDEX ON "TaskReminders" ("id");


COMMENT
ON TABLE "Roles" IS 'Reader, Editor';
COMMENT
ON TABLE "Status" IS 'No status, To do, Doing, Done, Custom';
COMMENT
ON TABLE "Priority" IS 'No, Low, Medium, High, Highest, Custom';
COMMENT
ON TABLE "FieldType" IS 'Short text, Long text, Date, Datetime, etc.';
COMMENT
ON TABLE "ReminderType" IS 'Email, Push notification';
COMMENT
ON TABLE "Connections" IS 'Blocks, duplicates, related';
COMMENT
ON TABLE "UserTask" IS 'Юзеры, назначенные ответственными за таск';
COMMENT
ON TABLE "TaskRelations" IS 'Сложные связи между задачами';
COMMENT
ON TABLE "Tags" IS 'Все существующие теги';
COMMENT
ON TABLE "TagTeam" IS 'Каким командам принадлежат теги (команда может создать свой тег - этот тег не должен появляться в других командах';
COMMENT
ON TABLE "Fields" IS 'По аналогии с тегами - команды могут создавать кастомные поля у задач';

-- Внешние ключи остаются без изменений
ALTER TABLE "Projects"
    ADD FOREIGN KEY ("team_id") REFERENCES "Teams" ("id");
ALTER TABLE "Streams"
    ADD FOREIGN KEY ("project_id") REFERENCES "Projects" ("id");
ALTER TABLE "Goals"
    ADD FOREIGN KEY ("stream_id") REFERENCES "Streams" ("id");
ALTER TABLE "Tasks"
    ADD FOREIGN KEY ("stream_id") REFERENCES "Streams" ("id");
ALTER TABLE "Tasks"
    ADD FOREIGN KEY ("status_id") REFERENCES "Status" ("id");
ALTER TABLE "Tasks"
    ADD FOREIGN KEY ("priority_id") REFERENCES "Priority" ("id");
ALTER TABLE "UserTeam"
    ADD FOREIGN KEY ("user_id") REFERENCES "Users" ("id");
ALTER TABLE "UserTeam"
    ADD FOREIGN KEY ("team_id") REFERENCES "Teams" ("id");
ALTER TABLE "UserTeam"
    ADD FOREIGN KEY ("role_id") REFERENCES "Roles" ("id");
ALTER TABLE "UserTask"
    ADD FOREIGN KEY ("user_id") REFERENCES "Users" ("id");
ALTER TABLE "UserTask"
    ADD FOREIGN KEY ("task_id") REFERENCES "Tasks" ("id");
ALTER TABLE "TaskRelations"
    ADD FOREIGN KEY ("task_id_1") REFERENCES "Tasks" ("id");
ALTER TABLE "TaskRelations"
    ADD FOREIGN KEY ("task_id_2") REFERENCES "Tasks" ("id");
ALTER TABLE "TaskRelations"
    ADD FOREIGN KEY ("connection_id") REFERENCES "Connections" ("id");
ALTER TABLE "TagTeam"
    ADD FOREIGN KEY ("tag_id") REFERENCES "Tags" ("id");
ALTER TABLE "TagTeam"
    ADD FOREIGN KEY ("team_id") REFERENCES "Teams" ("id");
ALTER TABLE "TagTask"
    ADD FOREIGN KEY ("tag_id") REFERENCES "Tags" ("id");
ALTER TABLE "TagTask"
    ADD FOREIGN KEY ("task_id") REFERENCES "Tasks" ("id");
ALTER TABLE "Fields"
    ADD FOREIGN KEY ("team_id") REFERENCES "Teams" ("id");
ALTER TABLE "Fields"
    ADD FOREIGN KEY ("field_type_id") REFERENCES "FieldType" ("id");
ALTER TABLE "FieldValues"
    ADD FOREIGN KEY ("field_id") REFERENCES "Fields" ("id");
ALTER TABLE "FieldValues"
    ADD FOREIGN KEY ("task_id") REFERENCES "Tasks" ("id");
ALTER TABLE "TaskHistory"
    ADD FOREIGN KEY ("task_id") REFERENCES "Tasks" ("id");
ALTER TABLE "TaskHistory"
    ADD FOREIGN KEY ("new_status_id") REFERENCES "Status" ("id");
ALTER TABLE "TaskReminders"
    ADD FOREIGN KEY ("task_id") REFERENCES "Tasks" ("id");
ALTER TABLE "TaskReminders"
    ADD FOREIGN KEY ("user_id") REFERENCES "Users" ("id");
ALTER TABLE "TaskReminders"
    ADD FOREIGN KEY ("reminder_type_id") REFERENCES "ReminderType" ("id");
ALTER TABLE "UserTask"
ADD CONSTRAINT usertask_user_id_fkey FOREIGN KEY (user_id) REFERENCES "Users"(id),
ADD CONSTRAINT usertask_task_id_fkey FOREIGN KEY (task_id) REFERENCES "Tasks"(id);

INSERT INTO "Status" ("name")
VALUES ('No status'),
       ('To do'),
       ('Doing'),
       ('Done');

INSERT INTO "Priority" ("name")
VALUES ('No priority'),
       ('Low'),
       ('Medium'),
       ('High'),
       ('Highest');

INSERT INTO "Roles" ("name")
VALUES ('Reader'),
       ('Editor');

INSERT INTO "Connections" ("name")
VALUES ('T1 blocks T2'),
       ('T1 duplicates T2'),
       ('T1 related to T2');

INSERT INTO "ReminderType" ("name")
VALUES ('Email'),
       ('Push notification');

INSERT INTO "FieldType" ("name")
VALUES ('Short text'),
       ('Long text'),
       ('Date'),
       ('Datetime'),
       ('Number'),
       ('Checkbox');

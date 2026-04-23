BEGIN;
--
-- Add field student to userprofile
--
CREATE TABLE "new__students_userprofile" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "student_id" bigint NULL UNIQUE REFERENCES "students_student" ("id") DEFERRABLE INITIALLY DEFERRED, "role" varchar(20) NOT NULL, "status" varchar(20) NOT NULL, "user_id" integer NOT NULL UNIQUE REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
INSERT INTO "new__students_userprofile" ("id", "role", "status", "user_id", "student_id") SELECT "id", "role", "status", "user_id", NULL FROM "students_userprofile";
DROP TABLE "students_userprofile";
ALTER TABLE "new__students_userprofile" RENAME TO "students_userprofile";
--
-- Alter field trang_thai on enrollment
--
-- (no-op)
--
-- Alter field trang_thai on student
--
-- (no-op)
--
-- Alter field role on userprofile
--
CREATE TABLE "new__students_userprofile" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "status" varchar(20) NOT NULL, "user_id" integer NOT NULL UNIQUE REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "student_id" bigint NULL UNIQUE REFERENCES "students_student" ("id") DEFERRABLE INITIALLY DEFERRED, "role" varchar(20) NOT NULL);
INSERT INTO "new__students_userprofile" ("id", "status", "user_id", "student_id", "role") SELECT "id", "status", "user_id", "student_id", "role" FROM "students_userprofile";
DROP TABLE "students_userprofile";
ALTER TABLE "new__students_userprofile" RENAME TO "students_userprofile";
--
-- Alter field status on userprofile
--
-- (no-op)
--
-- Raw Python operation
--
-- THIS OPERATION CANNOT BE WRITTEN AS SQL
--
-- Create model Classroom
--
CREATE TABLE "students_classroom" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "ma_lop_hp" varchar(30) NOT NULL UNIQUE, "hoc_ky" varchar(10) NOT NULL, "nam_hoc" varchar(20) NOT NULL, "phong_hoc" varchar(50) NOT NULL, "lich_hoc" varchar(120) NOT NULL, "si_so_toi_da" smallint unsigned NOT NULL CHECK ("si_so_toi_da" >= 0), "trang_thai" varchar(20) NOT NULL, "created_at" datetime NOT NULL, "course_id" bigint NOT NULL REFERENCES "students_course" ("id") DEFERRABLE INITIALLY DEFERRED, "giang_vien_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model Attendance
--
CREATE TABLE "students_attendance" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "ngay_hoc" date NOT NULL, "trang_thai" varchar(20) NOT NULL, "ghi_chu" varchar(255) NOT NULL, "updated_at" datetime NOT NULL, "enrollment_id" bigint NOT NULL REFERENCES "students_enrollment" ("id") DEFERRABLE INITIALLY DEFERRED, "updated_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "classroom_id" bigint NOT NULL REFERENCES "students_classroom" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Add field classroom to enrollment
--
ALTER TABLE "students_enrollment" ADD COLUMN "classroom_id" bigint NULL REFERENCES "students_classroom" ("id") DEFERRABLE INITIALLY DEFERRED;
--
-- Raw Python operation
--
-- THIS OPERATION CANNOT BE WRITTEN AS SQL
--
-- Create constraint uniq_student_classroom on model enrollment
--
CREATE UNIQUE INDEX "uniq_student_classroom" ON "students_enrollment" ("student_id", "classroom_id") WHERE "classroom_id" IS NOT NULL;
--
-- Create constraint uniq_attendance_per_session on model attendance
--
CREATE TABLE "new__students_attendance" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "ngay_hoc" date NOT NULL, "trang_thai" varchar(20) NOT NULL, "ghi_chu" varchar(255) NOT NULL, "updated_at" datetime NOT NULL, "enrollment_id" bigint NOT NULL REFERENCES "students_enrollment" ("id") DEFERRABLE INITIALLY DEFERRED, "updated_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "classroom_id" bigint NOT NULL REFERENCES "students_classroom" ("id") DEFERRABLE INITIALLY DEFERRED, CONSTRAINT "uniq_attendance_per_session" UNIQUE ("classroom_id", "enrollment_id", "ngay_hoc"));
INSERT INTO "new__students_attendance" ("id", "ngay_hoc", "trang_thai", "ghi_chu", "updated_at", "enrollment_id", "updated_by_id", "classroom_id") SELECT "id", "ngay_hoc", "trang_thai", "ghi_chu", "updated_at", "enrollment_id", "updated_by_id", "classroom_id" FROM "students_attendance";
DROP TABLE "students_attendance";
ALTER TABLE "new__students_attendance" RENAME TO "students_attendance";
CREATE INDEX "students_classroom_course_id_cde03475" ON "students_classroom" ("course_id");
CREATE INDEX "students_classroom_giang_vien_id_f539aeff" ON "students_classroom" ("giang_vien_id");
CREATE INDEX "students_enrollment_classroom_id_01c62a49" ON "students_enrollment" ("classroom_id");
CREATE INDEX "students_attendance_enrollment_id_4ea0661f" ON "students_attendance" ("enrollment_id");
CREATE INDEX "students_attendance_updated_by_id_e217cc0e" ON "students_attendance" ("updated_by_id");
CREATE INDEX "students_attendance_classroom_id_8290349a" ON "students_attendance" ("classroom_id");
COMMIT;

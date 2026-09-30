-- Sample HR data for bigquery_agent.
-- Creates dataset `hr_data` with two tables that share emp_id (no foreign key).
--
-- Run once (from the adk-fundamentals folder):
--   bq query --project_id=YOUR_PROJECT_ID --use_legacy_sql=false < bigquery_agent/setup_hr_data.sql
-- Or paste it into the BigQuery Studio SQL editor in the Console.

CREATE SCHEMA IF NOT EXISTS hr_data
OPTIONS (location = 'US', description = 'Sample HR data for the ADK BigQuery agent');

-- Employee details: one row per employee.
CREATE OR REPLACE TABLE hr_data.employee_info (
  emp_id STRING OPTIONS (description = 'Employee ID, e.g. emp1'),
  emp_name STRING OPTIONS (description = 'Employee full name'),
  designation STRING OPTIONS (description = 'Job title'),
  salary INT64 OPTIONS (description = 'Annual salary in USD')
);

INSERT INTO hr_data.employee_info (emp_id, emp_name, designation, salary) VALUES
  ('emp1', 'Aarav Sharma', 'Software Engineer', 95000),
  ('emp2', 'Priya Nair', 'Senior Software Engineer', 125000),
  ('emp3', 'Rahul Verma', 'Data Analyst', 80000),
  ('emp4', 'Sneha Reddy', 'Data Scientist', 115000),
  ('emp5', 'Vikram Singh', 'Engineering Manager', 150000),
  ('emp6', 'Ananya Iyer', 'Product Manager', 130000),
  ('emp7', 'Karthik Rao', 'DevOps Engineer', 105000),
  ('emp8', 'Meera Joshi', 'QA Engineer', 78000),
  ('emp9', 'Arjun Patel', 'Software Engineer', 92000),
  ('emp10', 'Divya Menon', 'HR Specialist', 70000);

-- Leave requests: one row per leave day applied. Same emp_id values as employee_info.
CREATE OR REPLACE TABLE hr_data.employee_leaves (
  emp_id STRING OPTIONS (description = 'Employee ID, matches employee_info.emp_id'),
  leave_date DATE OPTIONS (description = 'Date the leave was applied for')
);

INSERT INTO hr_data.employee_leaves (emp_id, leave_date) VALUES
  ('emp1', DATE '2026-01-12'),
  ('emp1', DATE '2026-03-05'),
  ('emp2', DATE '2026-02-14'),
  ('emp3', DATE '2026-01-20'),
  ('emp3', DATE '2026-01-21'),
  ('emp3', DATE '2026-06-10'),
  ('emp4', DATE '2026-04-01'),
  ('emp5', DATE '2026-05-18'),
  ('emp5', DATE '2026-05-19'),
  ('emp6', DATE '2026-07-07'),
  ('emp7', DATE '2026-02-02'),
  ('emp7', DATE '2026-08-15'),
  ('emp9', DATE '2026-03-23'),
  ('emp9', DATE '2026-09-01'),
  ('emp9', DATE '2026-09-02');
-- emp8 and emp10 have no leaves (useful for "who hasn't taken leave?" questions).

# WsCube Tech Workday & Daily Report — prototype

A small Python/Streamlit prototype for daily office/WFH attendance, task-block logging, mandatory report submission during clock-out, and employee-side locking after submission. SQLite is used for local demonstration.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL Streamlit prints. The prototype creates `attendance.db` in its working directory.

## Workflow

1. Employee enters a name and selects Office or Work from home.
2. Clock in creates one daily record.
3. Employee records work blocks with start/end, work item and outcome.
4. At clock out, the employee must provide at least one task and a daily summary.
5. Submission stores clock-out time and locks the report in the employee UI.
6. The manager snapshot lists daily check-ins and report state.

## Before production

- Replace name entry with company SSO or verified employee accounts; enforce role-based employee/manager/admin access.
- Use PostgreSQL (or the organization’s managed database), migrations, backups, TLS, secrets management, and deployment monitoring.
- Make the server the source of timestamps; store UTC plus the configured business timezone and handle overnight shifts.
- Enforce one attendance record per employee per workday in the database, idempotent clock-in/out operations, and transaction-safe report locking.
- Add manager corrections as append-only adjustments with reason, actor, timestamp, and before/after values. Never silently rewrite submitted employee entries.
- Define policy for breaks, leave/holiday, missed punches, work from home, late/early attendance, overtime, grace periods, and attendance regularization.
- Add access-controlled filters, audit history, exports, notifications/reminders, retention/deletion policy, and privacy notice.
- The demo manager snapshot has no authentication and is not safe for internet deployment. SQLite is intended only for local review.

## Product references

- greytHR ESS sign-in/sign-out and attendance context: https://www.greythr.com/help-ess-web/get-started-greythr-ess-portal/ess-home-page-guide/
- greytHR timesheet policy setup, including limiting logs to attendance hours: https://www.greythr.com/help-admin/admin-tools/setup-timesheet-policies/
- Odoo Attendances (time clock, work hours, exception handling): https://www.odoo.com/documentation/18.0/applications/hr/attendances.html
- Odoo Timesheets (log, view and validate work time): https://www.odoo.com/documentation/master/applications/services/timesheets.html
- Odoo Timesheet features (validation and date locking): https://www.odoo.com/app/timesheet-features
- Django (alternative framework if the team wants a fuller multi-user web application with built-in authentication/admin): https://www.djangoproject.com/start/

These are feature references, not a claim of exact product parity. The suggested next step is a production specification, then rebuild this flow in the team’s chosen stack with HR policy and access controls confirmed.

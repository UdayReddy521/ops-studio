# Lead follow-up release checks

A small software team needs to know that an enquiry gets saved, its overdue reminder reaches the inbox, and a rerun produces no duplicate. This staging example turns those manual checks into a repeatable test suite.

| Check | Evidence |
| --- | --- |
| Save a new enquiry | Submit through the API and read it back after reopening the application. |
| Notify only when due | Submit an overdue and a future enquiry. Only the overdue enquiry appears in the test inbox. |
| Prevent duplicates | Run two reminder workers concurrently and rerun after a restart. The inbox still has one record. |

The reminder is a durable row in a simulated inbox. SQLite makes insertion and duplicate protection part of the same operation. This example tests the API and SQLite boundary. Actual Google Sheets, n8n, and email delivery require separate integration tests in the target environment.

## Run the example

From the repository root, run the [installation and test commands](../../README.md#run-the-release-checks). Then start the local API:

```bash
python -m uvicorn --app-dir lead-followup/release-checks app:create_app --factory
```

Open [the local API console](http://127.0.0.1:8000/docs), or use the commands below from a second terminal. Keep the example on localhost and use fictional enquiries. It has no authentication.

```bash
curl -fsS -X POST http://127.0.0.1:8000/enquiries \
  -H 'Content-Type: application/json' \
  -d '{"id":"L101","owner":"Priya","due_at":"2020-01-01T00:00:00Z"}'
curl -fsS http://127.0.0.1:8000/enquiries/L101
curl -fsS -X POST http://127.0.0.1:8000/reminders/run
curl -fsS -X POST http://127.0.0.1:8000/reminders/run
curl -fsS http://127.0.0.1:8000/reminders
```

On a fresh database, the two reminder runs report 1 and 0. The inbox contains one record for L101. Use a new enquiry ID if you try it again. The local database lives in `reports/`, which Git ignores.

[View CI runs](https://github.com/UdayReddy521/ops-studio/actions/workflows/release-checks.yml)

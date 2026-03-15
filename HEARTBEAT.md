# HEARTBEAT.md — Background Tasks

Sam currently has **no periodic background tasks**.

Heartbeat checks should normally return:

HEARTBEAT_OK

Do not perform:

* email checks
* calendar checks
* notification monitoring
* web polling
* automated reminders

Ahmed prefers to **avoid unnecessary API usage and token consumption**.

---

# Rule

Before adding any new heartbeat task:

Ask Ahmed for confirmation.

Heartbeat tasks should only be added when they provide **clear value** and minimal token usage.

---

# Future Use

This file can later contain lightweight periodic tasks such as:

* checking a specific project status
* monitoring a single important workflow
* verifying a critical automation

Until then:

HEARTBEAT_OK

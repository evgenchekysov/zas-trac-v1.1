ADR‑00X — Separation of creator and owner roles in ZAS‑TRAC
Status: Accepted
Date: 2026‑04‑10
Context: ZAS‑TRAC backend architecture (Day 29 decisions)
Scope: Ticket lifecycle, ownership, batch operations (D+30)

Context
In ZAS‑TRAC, tickets have multiple user‑related roles serving different purposes:

created_by (creator) — identifies the user who initiated the ticket.
owner — represents the current operational responsibility for the ticket.
participant — represents users participating in the work on the ticket.

During backend implementation and lifecycle automation (including batch operations such as D+30 handling), a potential ambiguity arose regarding whether creator could be used as a fallback value for owner in cases where owner is not explicitly set.
The backend architecture and business model were formally fixed on Day 29, where these roles were intentionally separated to reflect real operational responsibility and accountability.

Decision
The creator (created_by) field MUST NOT be used as a fallback or implicit source for the owner field under any circumstances.
This rule applies universally, including but not limited to:

ticket creation;
status transitions;
automated or batch operations (e.g. D+30 processing);
normalization or data‑repair logic;
migrations or background jobs.

Ownership of a ticket may change only as a result of explicit business rules or deliberate administrative actions.

Rationale


Different semantic meaning

creator is a historical fact.
owner is an active management responsibility.

Conflating them introduces incorrect semantics into the system.


Avoiding implicit business decisions
Automatically assigning owner based on creator causes the system to take a management decision without an explicit event, action, or authorization.


Preserving accountability and SLA logic
The owner role controls:

permission to close tickets (DONE → CLOSED);
responsibility for final outcomes;
escalation and reporting logic.

Implicit reassignment breaks accountability expectations.


Consistency with Day 29 architecture
Day 29 decisions explicitly separated:

historical data;
operational responsibility;
participation in work.

Using creator as a fallback violates that separation.


Predictability for users and integrators
Users must never become ticket owners “by surprise”.
External systems (reports, Telegram, analytics) must rely on explicit ownership state.



Consequences
✅ Positive

Clear and predictable ownership semantics.
No hidden side‑effects during lifecycle automation.
Stable foundation for SLA, reporting, and integrations.
Reduced risk of silent responsibility shifts.

⚠️ Trade‑offs

Tickets may temporarily exist without an owner.
Ownership assignment must be handled explicitly (user action, queue assignment, admin workflow).

These trade‑offs are considered acceptable and preferable to implicit responsibility reassignment.

Implementation Notes

ticket_service.py must not contain any logic equivalent to:

if owner is None: owner = created_by


Batch and lifecycle handlers (including D+30 logic) must preserve existing owner state or leave it unchanged.
If ownership is required by a process, it must be assigned explicitly (e.g. queue, admin, dispatcher logic).


Status
This decision is final and fixed by design.
Any deviation requires a new ADR explicitly revisiting ownership semantics.

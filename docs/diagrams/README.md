# Diagrams

Four diagram categories for the Civic Issue Tracker. Sources are PlantUML
(`.puml`); exports are black-and-white PNGs generated with PlantUML 1.2023.13:

    java -jar ../../tools/plantuml.jar -tpng <file>.puml

## 1. Data Flow Diagram (three levels)

- `dfd-level-0.puml` / *Civic Issue Tracker - DFD Level 0*: the whole system as
  one process exchanging data with the Citizen, Administrator and Department
  Staff external entities (reports in; IDs, statuses and notifications out).
- `dfd-level-1.puml` / *DFD Level 1*: decomposes the system into the six
  processes P1 Authentication, P2 Issue Reporting, P3 Search & Map, P4 Issue
  Management & Status, P5 Upvotes, P6 Notifications & Analytics, with data
  stores D1-D8 matching the database tables.
- `dfd-level-2.puml` / *DFD Level 2 - P2 Issue Reporting*: expands P2 into
  P2.1 validate input, P2.2 validate & store image, P2.3 store issue record,
  P2.4 generate public ID, P2.5 create notifications - the exact backend flow
  in `api/issues.py::create_issue`.

## 2. Use Case Diagram

`use-case.puml` - actors Citizen, Administrator and Department Staff with the
implemented use cases. `<<include>>` marks mandatory sub-flows (reporting and
upvoting include login; status changes and announcements include
notifications); `<<extend>>` marks optional add-ons (image upload, map pin).

## 3. Class Diagram

`class-diagram.puml` - the SQLAlchemy model layer: User with the Citizen /
Administrator / DepartmentStaff role subclasses, the Issue aggregate with its
images, status history, upvotes, assignments and comments, plus catalog
(Sector/Category/Department), Notification and Announcement classes. Shown
multiplicities match the foreign keys in `backend/app/models/`.

## 4. Activity Diagram

`activity-diagram.puml` - the issue resolution workflow across four swimlanes
(Citizen, System, Administrator, Department Staff), including the validation
loop, the reject-with-reason path, the clarification loop, assignment, staff
resolution, the reopen path when a resolution is not accepted, and final
notification.

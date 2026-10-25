"""Database initialization with realistic fictional demo data.

Seed issues that carry coordinates use real, publicly known Chennai landmark
locations (e.g. Marina Beach, T. Nagar) purely as demonstration anchors; the
reports themselves are fictional. Issues without a confirmed location have no
coordinates and therefore appear in lists only, never on the map.

Run:  python -m app.seed        (from backend/)
"""
import os
from datetime import datetime, timedelta

from .database.base import Base
from .database.session import engine, SessionLocal
from . import models
from .models import (User, UserRole, Sector, Category, Department, Issue,
                     IssueStatus, IssueStatusHistory, Upvote, Comment,
                     Notification, Announcement, IssueAssignment)
from .services import auth_service

DEMO_PASSWORDS = {"admin@example.com": os.getenv("SEED_ADMIN_PASSWORD", "Admin@123"),
                  "staff@example.com": os.getenv("SEED_STAFF_PASSWORD", "Staff@123"),
                  "citizen@example.com": os.getenv("SEED_CITIZEN_PASSWORD", "Citizen@123"),
                  "meena@example.com": os.getenv("SEED_CITIZEN_PASSWORD", "Citizen@123"),
                  "arun@example.com": os.getenv("SEED_CITIZEN_PASSWORD", "Citizen@123")}

SECTORS = {
    "Municipal & Civic Services": ["Potholes & Roads", "Garbage & Sanitation",
                                   "Street Lighting", "Water Supply & Leaks", "Drainage"],
    "Education & Campus": ["Classroom Equipment", "Campus Cleanliness", "Library Services"],
    "Healthcare Facilities": ["Facility Maintenance", "Equipment Faults", "Sanitation"],
    "Offices & Companies": ["Building Maintenance", "IT Infrastructure"],
    "Apartments & Communities": ["Common Area Maintenance", "Plumbing", "Security"],
    "Transportation": ["Bus Stop & Shelter", "Traffic Signals", "Footpaths"],
    "Industry": ["Safety Hazards", "Waste Management"],
    "Environment": ["Tree Damage", "Pollution", "Park Maintenance"],
}

DEPARTMENTS = [
    ("Roads & Infrastructure Dept", "Municipal & Civic Services"),
    ("Sanitation Dept", "Municipal & Civic Services"),
    ("Electrical Dept", "Municipal & Civic Services"),
    ("Campus Maintenance Office", "Education & Campus"),
    ("Parks & Environment Cell", "Environment"),
    ("Transport Engineering Cell", "Transportation"),
]


def seed():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        sectors = {}
        for s_name, cats in SECTORS.items():
            s = Sector(name=s_name, description=f"Issues related to {s_name.lower()}.")
            db.add(s)
            db.flush()
            sectors[s_name] = s
            for c_name in cats:
                db.add(Category(sector_id=s.id, name=c_name))

        depts = {}
        for d_name, s_name in DEPARTMENTS:
            d = Department(name=d_name, sector_id=sectors[s_name].id,
                           contact_email=d_name.lower().replace(" ", ".").replace("&", "and") + "@example.com")
            db.add(d)
            db.flush()
            depts[d_name] = d

        users = {}
        users["admin"] = User(name="Demo Admin", email="admin@example.com",
                              password_hash=auth_service.hash_password(DEMO_PASSWORDS["admin@example.com"]),
                              role=UserRole.ADMIN)
        users["staff"] = User(name="Ravi Kumar (Staff)", email="staff@example.com",
                              password_hash=auth_service.hash_password(DEMO_PASSWORDS["staff@example.com"]),
                              role=UserRole.STAFF, department_id=depts["Roads & Infrastructure Dept"].id)
        users["citizen"] = User(name="Demo Citizen", email="citizen@example.com",
                                password_hash=auth_service.hash_password(DEMO_PASSWORDS["citizen@example.com"]),
                                role=UserRole.CITIZEN)
        users["meena"] = User(name="Meena S", email="meena@example.com",
                              password_hash=auth_service.hash_password(DEMO_PASSWORDS["meena@example.com"]),
                              role=UserRole.CITIZEN)
        users["arun"] = User(name="Arun Prakash", email="arun@example.com",
                             password_hash=auth_service.hash_password(DEMO_PASSWORDS["arun@example.com"]),
                             role=UserRole.CITIZEN)
        db.add_all(users.values())
        db.flush()

        cat = {}
        for c in db.query(Category).all():
            cat[(c.sector.name, c.name)] = c

        now = datetime.utcnow()
        # (reporter, sector, category, title, desc, location, lat, lng, status, age_days)
        ISSUES = [
            ("citizen", "Municipal & Civic Services", "Potholes & Roads",
             "Large pothole near Marina Beach service road",
             "A deep pothole has formed near the Marina Beach service road exit. Two-wheelers are swerving dangerously, especially at night.",
             "Marina Beach Service Road, Chennai", 13.0500, 80.2824, IssueStatus.IN_PROGRESS, 9),
            ("meena", "Municipal & Civic Services", "Garbage & Sanitation",
             "Garbage not collected for a week in T. Nagar",
             "Household waste has been piling up near the market entrance for over a week. Stray animals are scattering it across the pavement.",
             "Ranganathan Street, T. Nagar, Chennai", 13.0418, 80.2341, IssueStatus.UNDER_REVIEW, 6),
            ("arun", "Municipal & Civic Services", "Street Lighting",
             "Streetlight not working near Nungambakkam station",
             "Three consecutive streetlights are dark on the approach road to Nungambakkam railway station. The stretch feels unsafe after 8 pm.",
             "Nungambakkam Station Road, Chennai", 13.0604, 80.2373, IssueStatus.REPORTED, 2),
            ("citizen", "Municipal & Civic Services", "Water Supply & Leaks",
             "Drinking water pipe leaking on Cathedral Road",
             "A supply pipe is leaking steadily near the Cathedral Road flyover. Clean water has been running onto the road since Monday.",
             "Cathedral Road, Chennai", 13.0447, 80.2490, IssueStatus.RESOLVED, 20),
            ("meena", "Education & Campus", "Classroom Equipment",
             "Projector not working in Block C seminar hall",
             "The ceiling projector in the Block C seminar hall powers on but shows no signal. Classes are being shifted to smaller rooms.",
             "Block C, Anna University Campus, Chennai", 13.0112, 80.2357, IssueStatus.IN_PROGRESS, 4),
            ("arun", "Environment", "Park Maintenance",
             "Broken bench and overgrown plants in Semmozhi Poonga",
             "Two benches near the east gate are broken and the walking path is overgrown. Senior citizens who use the park daily are affected.",
             "Semmozhi Poonga, Chennai", 13.0478, 80.2479, IssueStatus.REPORTED, 3),
            ("citizen", "Transportation", "Bus Stop & Shelter",
             "Bus shelter roof damaged at Adyar depot stop",
             "The shelter roof at the Adyar depot bus stop was damaged in the recent rain. Commuters have no cover during showers.",
             "Adyar Depot Bus Stop, Chennai", 13.0012, 80.2565, IssueStatus.UNDER_REVIEW, 5),
            ("meena", "Municipal & Civic Services", "Drainage",
             "Stagnant water after rain near Velachery main road",
             "Rainwater stagnates for days near the Velachery main road junction, breeding mosquitoes and blocking the footpath.",
             "Velachery Main Road, Chennai", 12.9815, 80.2180, IssueStatus.REPORTED, 1),
            ("arun", "Municipal & Civic Services", "Potholes & Roads",
             "Uneven speed breaker near Guindy signal",
             "An unmarked, uneven speed breaker near the Guindy signal is causing sudden braking. It needs repainting and levelling.",
             "Guindy Signal, Chennai", 13.0067, 80.2206, IssueStatus.RESOLVED, 30),
            ("citizen", "Healthcare Facilities", "Sanitation",
             "Overflowing bins at community health centre",
             "The waste bins behind the community health centre are overflowing. Sanitation staff should clear them daily.",
             "Community Health Centre, Saidapet, Chennai", None, None, IssueStatus.REPORTED, 2),
            ("meena", "Apartments & Communities", "Plumbing",
             "Water seepage in apartment basement parking",
             "Water is seeping through the basement wall of our apartment block, damaging parked vehicles.",
             "Sunrise Apartments, Porur, Chennai", None, None, IssueStatus.UNDER_REVIEW, 7),
            ("arun", "Environment", "Pollution",
             "Smoke from waste burning near industrial estate",
             "Waste is being burnt in the open near the industrial estate every evening, causing heavy smoke in the residential lane.",
             "Guindy Industrial Estate, Chennai", None, None, IssueStatus.REJECTED, 12),
        ]
        issues = []
        for (reporter, s_name, c_name, title, desc, loc, lat, lng, st, age) in ISSUES:
            issue = Issue(public_id="PENDING", reporter_id=users[reporter].id,
                          title=title, description=desc,
                          sector_id=sectors[s_name].id, category_id=cat[(s_name, c_name)].id,
                          location_text=loc, latitude=lat, longitude=lng, status=st,
                          created_at=now - timedelta(days=age),
                          resolved_at=(now - timedelta(days=max(age - 3, 0)))
                          if st == IssueStatus.RESOLVED else None,
                          rejection_reason=("Report does not fall under civic jurisdiction; "
                                            "referred to the pollution control board."
                                            if st == IssueStatus.REJECTED else None))
            db.add(issue)
            db.flush()
            issue.public_id = f"CIV-{issue.created_at.year}-{issue.id:05d}"
            issues.append(issue)

        # status history trail for every issue
        for issue in issues:
            db.add(IssueStatusHistory(issue_id=issue.id, old_status=None,
                                      new_status=IssueStatus.REPORTED,
                                      comment="Issue reported.",
                                      changed_by_id=issue.reporter_id,
                                      created_at=issue.created_at))
            if issue.status in (IssueStatus.UNDER_REVIEW, IssueStatus.IN_PROGRESS,
                                IssueStatus.RESOLVED):
                db.add(IssueStatusHistory(issue_id=issue.id,
                                          old_status=IssueStatus.REPORTED,
                                          new_status=IssueStatus.UNDER_REVIEW,
                                          comment="Under review by the municipal team.",
                                          changed_by_id=users["admin"].id,
                                          created_at=issue.created_at + timedelta(hours=8)))
            if issue.status in (IssueStatus.IN_PROGRESS, IssueStatus.RESOLVED):
                db.add(IssueStatusHistory(issue_id=issue.id,
                                          old_status=IssueStatus.UNDER_REVIEW,
                                          new_status=IssueStatus.IN_PROGRESS,
                                          comment="Assigned and work started.",
                                          changed_by_id=users["admin"].id,
                                          created_at=issue.created_at + timedelta(days=1)))
            if issue.status == IssueStatus.RESOLVED:
                db.add(IssueStatusHistory(issue_id=issue.id,
                                          old_status=IssueStatus.IN_PROGRESS,
                                          new_status=IssueStatus.RESOLVED,
                                          comment="Work completed and verified on site.",
                                          changed_by_id=users["staff"].id,
                                          created_at=issue.resolved_at))
            if issue.status == IssueStatus.REJECTED:
                db.add(IssueStatusHistory(issue_id=issue.id,
                                          old_status=IssueStatus.REPORTED,
                                          new_status=IssueStatus.REJECTED,
                                          comment=issue.rejection_reason,
                                          changed_by_id=users["admin"].id,
                                          created_at=issue.created_at + timedelta(days=2)))

        # assignments on active issues
        roads = depts["Roads & Infrastructure Dept"]
        db.add(IssueAssignment(issue_id=issues[0].id, department_id=roads.id,
                               assigned_to_id=users["staff"].id,
                               assigned_by_id=users["admin"].id,
                               note="Patching crew scheduled for this week."))
        db.add(IssueAssignment(issue_id=issues[4].id,
                               department_id=depts["Campus Maintenance Office"].id,
                               assigned_to_id=None, assigned_by_id=users["admin"].id,
                               note="AV vendor visit requested."))

        # upvotes (no duplicates per user/issue - enforced by unique constraint)
        upvote_pairs = [(0, "meena"), (0, "arun"), (1, "citizen"), (1, "arun"),
                        (2, "citizen"), (2, "meena"), (2, "arun"), (7, "citizen")]
        for idx, who in upvote_pairs:
            db.add(Upvote(issue_id=issues[idx].id, user_id=users[who].id))

        # comments
        db.add(Comment(issue_id=issues[0].id, author_id=users["admin"].id,
                       body="Inspection completed. Patch work scheduled this week.",
                       is_admin=True))
        db.add(Comment(issue_id=issues[0].id, author_id=users["meena"].id,
                       body="Saw two bikes skid here yesterday evening. Please fix soon.",
                       is_admin=False))
        db.add(Comment(issue_id=issues[2].id, author_id=users["staff"].id,
                       body="Electrical dept informed; cable fault suspected.",
                       is_admin=True))

        # a couple of notifications for the demo citizen
        db.add(Notification(user_id=users["citizen"].id, type="status_change",
                            title=f"Issue {issues[0].public_id}: In Progress",
                            message=f'"{issues[0].title}" moved from Under Review to In Progress.',
                            issue_id=issues[0].id))
        db.add(Notification(user_id=users["citizen"].id, type="announcement",
                            title="Ward-level grievance camp this Saturday",
                            message="Bring your unresolved civic complaints to the ward office camp, 9 am - 1 pm."))

        db.add(Announcement(title="Ward-level grievance camp this Saturday",
                            body="Residents can bring unresolved civic complaints to the ward office camp on Saturday, 9 am - 1 pm. Carry your issue ID for faster lookup.",
                            created_by_id=users["admin"].id))

        db.commit()

        n = {t: db.query(m).count() for t, m in
             [("users", User), ("sectors", Sector), ("categories", Category),
              ("departments", Department), ("issues", Issue),
              ("status_history", IssueStatusHistory), ("upvotes", Upvote),
              ("comments", Comment), ("notifications", Notification),
              ("announcements", Announcement), ("assignments", IssueAssignment)]}
        print("Seed complete:", n)
        print("Demo accounts:", {k: v for k, v in DEMO_PASSWORDS.items()})
    finally:
        db.close()


if __name__ == "__main__":
    seed()

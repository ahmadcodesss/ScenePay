ScenePay is a collaborative expense-splitting web app built with Flask and SQLAlchemy. It allows users to create groups, manually or via receipts input itemized bills, invite others to join via links, and track who owes what and who has paid. Ideal for roommates, trip groups, or food-sharing buddies.
Features + Core Functionality:
- Create Groups with a name, description, and number of members.
- Manual Bill Entry:
  - Add multiple members.
  - Enter individual items, prices, and share ratios.
  - Choose who paid.
  - Add tax.
- Invite Members by Link:
  - Guest users are entered with names.
  - Once a real user logs in with a matching name, their guest entry is converted to a member.
-Payment Tracking:
  - For each member, track individual dues.
  - Update payment status (paid/unpaid).
-Dashboard:
  - View groups created.
  - View groups you’ve joined via invite link.
-Group Detail Page:
  - See full payment summary.
  - Update payment statuses.
- Logout and CSRF protection included.


Project Structure
billSplitter/
│
├── templates
│ ├── base.html
│ ├── dashboard.html
│ ├── login.html
│ ├── register.html
│ ├── manual_form.html
│ ├── group_detail.html
│ └── ...
│
├── main.py # Entry point (if run as a module)
├── routes # Flask blueprint (routes)
│ ├──__init__.py
│ ├── upload_routes.py
│ ├── main_routes.py
├── routes # Flask blueprint (routes)
│ ├──__init__.py
│ ├── oarse.py
├── forms.py # WTForms for Login, Register, CreateGroup
├── models.py # SQLAlchemy Models (User, Group, Expense...)
├── extensions.py # setup
├── config.py
├── upload/ # (Future) OCR and image processing
│
├── migrations/ # Alembic migration folder
│
└── README.md

Work done:
-Database models created and integrated
-User registration, login, logout flow complete
-Manual form for detailed item input working
-Expense tracking and splitting logic in place
-Invite link system implemented
-Joined groups show up on dashboard
-Dashboard and views styled and working
-Change payment feature added

Features To Add (Optional)
-OCR-based auto-fill for items with live JS-based suggestions on pricing(Pending)
- Member initiation for payment approval and owner approval of payments (Pending)
- UI polish (Basic styling done)

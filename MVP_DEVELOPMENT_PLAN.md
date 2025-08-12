# MVP Development Plan (Agent Instructions)

You MUST build this application in PHASES.  
Do NOT skip ahead — finish one phase, test it, then move to the next.

---

## Phase 1: Core Foundation
- Create main window with PySide6
- Add static sidebar navigation (no animations yet)
- Set up SQLite connection
- Create `medicines` table
- Add "Add Medicine" form → save to DB
- Add "View Medicines" table → display data

Deliverable: Basic app where I can add and view medicines.

---

## Phase 2: Inventory Management
- Implement edit & delete medicine features
- Add low-stock check
- Add expiry check

Deliverable: Inventory management working.

---

## Phase 3: Billing System
- Search products by name/barcode
- Add billing cart
- Auto total calculation
- Save bill to DB

Deliverable: Billing system functional.

---

## Phase 4: User Accounts
- Add login system (Admin/Cashier)
- Restrict page access by role

Deliverable: User-based access control.

---

## Phase 5: Reports
- Show sales reports
- Filter by date range
- Export to CSV

Deliverable: Reports working.

---

## Phase 6: UI Upgrade
- Apply color palette & fonts from UI_DESIGN_GUIDE.md
- Add sidebar animation
- Add icons

Deliverable: Modern, animated UI.

---

## Phase 7: Advanced Features
- Tax & discount in billing
- Printable invoices (PDF/Thermal)
- Backup & restore

Deliverable: Production-ready medical store app.

# Database Schema

## medicines
- id (INTEGER, PK)
- name (TEXT)
- category (TEXT)
- batch_no (TEXT)
- expiry_date (TEXT)
- quantity (INTEGER)
- purchase_price (REAL)
- selling_price (REAL)
- barcode (TEXT)

## sales
- id (INTEGER, PK)
- date (TEXT)
- items (TEXT - JSON)
- total (REAL)
- payment_method (TEXT)

## users
- id (INTEGER, PK)
- username (TEXT)
- password_hash (TEXT)
- role (TEXT)

## settings
- key (TEXT, PK)
- value (TEXT)

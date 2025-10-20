# 📊 Database Export & Backup System

## ✅ Full Database Export Available

**Location**: `/app/database_full_export.json`

**Export Details**:
- Database: MongoDB (crypto_exchange)
- Export Date: $(date)
- Total Collections: 5
- Total Documents: 6

### Collections Exported:

1. **users** (2 documents)
   - User accounts (admin, test users)
   - Authentication data
   - KYC information
   - Wallet balances

2. **trading_holdings** 
   - User cryptocurrency holdings
   - Portfolio data

3. **trading_orders**
   - Buy/Sell orders
   - Order history
   - Admin approvals

4. **wallet_addresses** (1 document)
   - User crypto wallet addresses
   - Verification status

5. **transactions** (1 document)
   - Transaction history
   - Deposit/withdrawal records

6. **notifications** (1 document)
   - User notifications
   - System alerts

7. **deposits** (1 document)
   - Card-to-card deposits
   - Admin approvals

---

## 🔧 NEW: Admin Backup Features

### Backend API Endpoints

All endpoints require admin authentication:

#### 1. Export Full Database (JSON)
```bash
GET /api/admin/backup/database
```
Returns complete database as JSON in response

#### 2. Create Backup File
```bash
POST /api/admin/backup/create
```
Creates timestamped backup file on server in `/app/backups/`

#### 3. List All Backups
```bash
GET /api/admin/backup/list
```
Returns list of all backup files with metadata

#### 4. Get Database Statistics
```bash
GET /api/admin/backup/stats
```
Returns collection counts, sizes, document counts

#### 5. Delete Backup
```bash
DELETE /api/admin/backup/{filename}
```
Removes a specific backup file

#### 6. Export Single Collection
```bash
GET /api/admin/backup/collection/{collection_name}
```
Exports only one collection (e.g., "users", "trading_orders")

---

## 📥 How to Access Your Database Export

### Option 1: Download Current Export
The file `/app/database_full_export.json` contains your complete database.

### Option 2: Use API (From Admin Panel - Coming Soon)
Access backup features through the admin dashboard.

### Option 3: Manual MongoDB Export
```bash
# Export specific collection
mongoexport --db=crypto_exchange --collection=users --out=users.json

# Export entire database
mongodump --db=crypto_exchange --out=/app/mongodump/
```

---

## 🔐 Database Structure

### Your Current Database Schema:

```
crypto_exchange/
├── users
│   ├── id (UUID)
│   ├── email
│   ├── password_hash
│   ├── first_name, last_name
│   ├── phone
│   ├── is_admin
│   ├── kyc_level (0-2)
│   ├── kyc_status (pending/approved/rejected)
│   ├── wallet_balance_tmn
│   └── created_at
│
├── trading_orders
│   ├── id (UUID)
│   ├── user_id
│   ├── order_type (buy/sell/trade)
│   ├── coin_symbol (BTC, ETH, USDT, etc.)
│   ├── amount_tmn
│   ├── crypto_amount
│   ├── status (pending/completed/rejected)
│   ├── wallet_address
│   └── created_at
│
├── trading_holdings
│   ├── id (UUID)
│   ├── user_id
│   ├── coin_symbol
│   ├── amount
│   └── last_updated
│
├── wallet_addresses
│   ├── id (UUID)
│   ├── user_id
│   ├── coin_symbol
│   ├── address
│   ├── is_verified
│   └── created_at
│
├── transactions
│   ├── id (UUID)
│   ├── user_id
│   ├── type (order_buy/order_sell/deposit)
│   ├── amount
│   ├── description
│   └── created_at
│
├── notifications
│   ├── id (UUID)
│   ├── user_id
│   ├── title
│   ├── message
│   ├── type (success/info/warning)
│   ├── is_read
│   └── created_at
│
└── deposits
    ├── id (UUID)
    ├── user_id
    ├── amount_tmn
    ├── card_number
    ├── transaction_id
    ├── status (pending/approved/rejected)
    ├── receipt_image
    └── created_at
```

---

## 🚨 Important Notes

1. **Backup Location**: All backups are stored in `/app/backups/`
2. **Automatic Backups**: Currently manual, can be automated
3. **Database Type**: MongoDB (NOT MySQL)
4. **Data Format**: JSON (human-readable)
5. **Security**: All backup endpoints require admin authentication

---

## 🔄 Next: Admin Backup UI Panel

Coming up: Web interface in admin panel to:
- View database statistics
- Create backups with one click
- Download backup files
- Manage backup history
- Schedule automatic backups


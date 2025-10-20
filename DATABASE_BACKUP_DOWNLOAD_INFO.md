# 📦 Full Database Backup - Ready for Download

## ✅ Backup Complete!

**Date**: October 20, 2025  
**Time**: 13:16:14 UTC  
**Status**: SUCCESS

---

## 📊 Backup Details

### Database Information:
- **Database Name**: crypto_exchange
- **Database Type**: MongoDB (NOT MySQL)
- **Backup Type**: FULL_COMPLETE_EXPORT
- **Format**: JSON (human-readable)

### Backup Statistics:
- **Total Collections**: 6
- **Total Documents**: 9
- **File Size**: 0.01 MB (6,094 bytes)
- **Status**: All collections exported successfully ✅

---

## 📁 Files Available for Download

### Main Backup File:
**Filename**: `FULL_DATABASE_BACKUP_20251020_131614.json`  
**Location**: `/app/FULL_DATABASE_BACKUP_20251020_131614.json`  
**Size**: 6 KB

### Easy Access Link:
**Filename**: `LATEST_BACKUP.json`  
**Location**: `/app/LATEST_BACKUP.json`  
**Note**: This is a symlink that always points to the most recent backup

---

## 📋 Collections Exported

| Collection Name | Document Count | Status |
|----------------|----------------|---------|
| users | 2 | ✅ |
| trading_orders | 2 | ✅ |
| wallet_addresses | 2 | ✅ |
| transactions | 1 | ✅ |
| notifications | 1 | ✅ |
| deposits | 1 | ✅ |

---

## 🔍 Collection Contents

### 1. users (2 documents)
- Admin user account
- Test user account
- Fields: email, password_hash, first_name, last_name, phone, is_admin, kyc_level, kyc_status, wallet_balance_tmn, created_at

### 2. trading_orders (2 documents)
- User buy orders for BTC and USDT
- Fields: id, user_id, order_type, coin_symbol, amount_crypto, amount_tmn, wallet_address, status, created_at

### 3. wallet_addresses (2 documents)
- User crypto wallet addresses
- Fields: id, user_id, coin_symbol, address, verified, created_at

### 4. transactions (1 document)
- Transaction history
- Fields: id, user_id, type, amount, description, created_at

### 5. notifications (1 document)
- User notification system
- Fields: id, user_id, title, message, type, is_read, created_at

### 6. deposits (1 document)
- Card-to-card deposit requests
- Fields: id, user_id, amount_tmn, card_number, transaction_id, status, receipt_image, created_at

---

## 📥 How to Download

### Option 1: Direct File Access
The backup file is located at:
```
/app/FULL_DATABASE_BACKUP_20251020_131614.json
```

### Option 2: Via Admin Panel (Recommended)
1. Login to admin panel: `https://exchange-farsi.preview.emergentagent.com/admin`
2. Go to "💾 پشتیبان‌گیری" (Backup)
3. Click "دانلود کامل دیتابیس" (Download Full Database)
4. File downloads automatically

### Option 3: Via Backend API
```bash
curl -X GET "https://exchange-farsi.preview.emergentagent.com/api/admin/backup/database" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -o database_backup.json
```

---

## 📄 Backup File Structure

```json
{
  "backup_metadata": {
    "database_name": "crypto_exchange",
    "database_type": "MongoDB",
    "backup_timestamp": "2025-10-20T13:16:14.486895+00:00",
    "backup_type": "FULL_COMPLETE_EXPORT",
    "backup_version": "2.0",
    "exported_by": "Admin Backup System"
  },
  "collections": {
    "users": {
      "document_count": 2,
      "documents": [ /* user data */ ],
      "export_timestamp": "..."
    },
    "trading_orders": {
      "document_count": 2,
      "documents": [ /* order data */ ],
      "export_timestamp": "..."
    },
    // ... other collections
  },
  "backup_summary": {
    "total_collections": 6,
    "total_documents": 9,
    "successful_collections": 6,
    "failed_collections": 0
  }
}
```

---

## 🔐 Security Notes

1. **Sensitive Data**: This backup contains user passwords (hashed with bcrypt), personal information, and financial data
2. **Storage**: Store securely, preferably encrypted
3. **Access**: Keep backup files private and secure
4. **Password**: User passwords are hashed and cannot be reversed

---

## 🔄 Restore Instructions

### To restore this backup:

1. **Stop the application**:
   ```bash
   sudo supervisorctl stop backend
   ```

2. **Connect to MongoDB**:
   ```bash
   mongo crypto_exchange
   ```

3. **Clear existing data** (CAUTION):
   ```javascript
   db.users.deleteMany({});
   db.trading_orders.deleteMany({});
   // ... etc for each collection
   ```

4. **Import from backup**:
   ```bash
   mongoimport --db crypto_exchange --collection users --file users_export.json
   # ... repeat for each collection
   ```

5. **Restart application**:
   ```bash
   sudo supervisorctl start backend
   ```

---

## 📊 Database Schema

### MongoDB Collections Schema:

#### users
```javascript
{
  id: String (UUID),
  email: String,
  password_hash: String (bcrypt),
  first_name: String,
  last_name: String,
  phone: String,
  is_admin: Boolean,
  kyc_level: Number (0-2),
  kyc_status: String (pending/approved/rejected),
  wallet_balance_tmn: Number,
  created_at: DateTime
}
```

#### trading_orders
```javascript
{
  id: String (UUID),
  user_id: String (UUID reference),
  order_type: String (buy/sell/trade),
  coin_symbol: String (BTC/USDT/ETH),
  coin_id: String (bitcoin/tether/ethereum),
  amount_crypto: Number,
  amount_tmn: Number,
  price_at_order: Number,
  total_value_tmn: Number,
  status: String (pending/approved/completed/rejected),
  wallet_address: String,
  created_at: DateTime,
  updated_at: DateTime
}
```

#### wallet_addresses
```javascript
{
  id: String (UUID),
  user_id: String (UUID reference),
  coin_symbol: String (BTC/USDT/ETH),
  coin_id: String (bitcoin/tether/ethereum),
  address: String (crypto wallet address),
  verified: Boolean,
  created_at: DateTime
}
```

---

## ✅ Verification

**Backup Integrity**: ✅ All collections exported successfully  
**Data Completeness**: ✅ All documents included  
**File Format**: ✅ Valid JSON  
**File Size**: ✅ 6 KB (reasonable for 9 documents)  
**Timestamp**: ✅ 2025-10-20T13:16:14.486895+00:00  

---

## 📞 Support

If you need help with the backup:
1. Check that the file exists at the location shown above
2. Verify file size is correct (6 KB)
3. Ensure JSON format is valid
4. Test by downloading via admin panel

---

## 🎯 Quick Commands

### View backup metadata:
```bash
cat /app/LATEST_BACKUP.json | jq '.backup_metadata'
```

### Count documents per collection:
```bash
cat /app/LATEST_BACKUP.json | jq '.backup_summary'
```

### Extract specific collection:
```bash
cat /app/LATEST_BACKUP.json | jq '.collections.users'
```

---

**✅ Your complete database backup is ready for download!**

**Note**: This is MongoDB (NoSQL), not MySQL (SQL). The data is in JSON format, which is MongoDB's native document format.

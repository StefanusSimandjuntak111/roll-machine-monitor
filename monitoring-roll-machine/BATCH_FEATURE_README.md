# 📊 Batch Tracking & Recap Feature

## Overview

This feature implements automatic batch generation and summary/recap functionality for the Roll Machine Monitor. Production data is now stored in **Supabase** (cloud database) with automatic batch tracking based on product changes.

## 🎯 Features

### 1. **Auto Batch Generation**
- **Format**: Number only (example: `1`, `2`, `3`)
- **Logic**:
  - First time rolling fabric → batch = `1`
  - Same product code → same batch number
  - Different product code → batch counter increments
  - Counter is continuous (not reset per day)

**Example Flow**:
```
First run:
Roll K-CR-1 → Batch: 1
Roll K-CR-1 again → Batch: 1 (same product, same batch)
Roll K-CR-1 again → Batch: 1 (same product, same batch)
Roll K-CR-2 → Batch: 2 (different product, new batch)
Roll K-CR-2 again → Batch: 2 (same product, same batch)
Roll K-CR-3 → Batch: 3 (different product, new batch)
Roll K-CR-1 again → Batch: 4 (different from current, new batch)

Next day:
Roll K-CR-2 → Batch: 5 (different from current, new batch)
Roll K-CR-3 → Batch: 6 (different from current, new batch)
```

### 2. **Batch Summary/Recap Dialog**
- **New Button**: "📊 Batch Recap" in main toolbar
- **Features**:
  - Select batch from dropdown
  - View batch summary (total rolls, length, avg times)
  - View detailed production logs
  - Export batch data to CSV
  - Auto-refresh capability

### 3. **Dual Storage System**
- **Primary**: Supabase (cloud database)
- **Backup**: Local JSON files
- **Benefits**: 
  - Data safety (cloud backup)
  - Works offline (local fallback)
  - Centralized data for multiple machines

## 📋 Setup Instructions

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

The `supabase` package is now included in requirements.txt.

### Step 2: Setup Supabase Database

1. **Login to Supabase Dashboard**: https://ifhwcfpakstnljkkfcfl.supabase.co

2. **Go to SQL Editor** in the dashboard

3. **Run the Schema**: Copy and paste the contents of `SUPABASE_SCHEMA.sql` and execute it

   This will create:
   - `production_logs` table
   - `batch_metadata` table
   - Indexes for performance
   - Auto-update triggers
   - Security policies

### Step 3: Configure Application

The Supabase credentials are already configured in `monitoring/config.json`:

```json
{
  "supabase_url": "https://ifhwcfpakstnljkkfcfl.supabase.co",
  "supabase_key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "enable_supabase": true
}
```

**To disable Supabase** (use only local JSON):
```json
{
  "enable_supabase": false
}
```

## 🚀 How to Use

### Auto Batch Generation

1. **Fill Product Form**:
   - Enter product code (e.g., `K-CR-1`)
   - Fill other product details
   - **Leave batch number empty** for auto-generation

2. **Click "Send to Device"**:
   - Batch number will be auto-generated (e.g., `1`, `2`, `3`)
   - Batch number field will be updated automatically
   - Batch logic:
     - Same product = same batch
     - Different product = new batch (counter increments)

3. **Manual Batch Override**:
   - You can still manually enter batch number
   - If entered, auto-generation will be skipped

### View Batch Recap

1. **Click "📊 Batch Recap"** button in toolbar

2. **Select Batch** from dropdown
   - Shows batches for today
   - Click "🔄 Refresh" to reload

3. **View Summary**:
   - Batch number
   - Product info
   - Total rolls
   - Total length
   - Average cycle/roll times
   - Start/end times

4. **View Details**:
   - Table shows all rolls in batch
   - Product code, name, length
   - Cycle time, roll time
   - Timestamps

5. **Export Data**:
   - Click "📥 Export CSV"
   - Saves to `exports/` folder
   - Filename: `batch_N_TIMESTAMP.csv` (e.g., `batch_1_20251003_143022.csv`)

## 📁 File Structure

### New Files Created:

```
monitoring-roll-machine/
├── monitoring/
│   ├── batch_manager.py          # Batch generation logic
│   ├── supabase_client.py        # Supabase integration
│   └── ui/
│       └── batch_summary_dialog.py  # Recap dialog UI
├── SUPABASE_SCHEMA.sql           # Database schema
└── BATCH_FEATURE_README.md       # This file
```

### Modified Files:

```
monitoring-roll-machine/
├── requirements.txt              # Added supabase package
├── monitoring/
│   ├── config.json              # Added Supabase credentials
│   ├── logging_table.py         # Updated to save to Supabase
│   └── ui/
│       ├── product_form.py      # Added auto-batch logic
│       └── main_window.py       # Added recap button
```

### Batch Tracking Files:

```
monitoring-roll-machine/
└── logs/
    └── batch_tracking.json      # Stores current batch state
```

## 🔧 Configuration Options

### Config.json Settings:

```json
{
  "supabase_url": "https://your-project.supabase.co",
  "supabase_key": "your-api-key",
  "enable_supabase": true  // Set to false to disable cloud storage
}
```

### Environment Variables (Optional):

You can also use environment variables:
- `SUPABASE_URL`
- `SUPABASE_KEY`

Priority: config.json > environment variables

## 📊 Database Schema

### production_logs Table

| Column | Type | Description |
|--------|------|-------------|
| id | BIGSERIAL | Auto-increment primary key |
| product_name | TEXT | Product name |
| product_code | TEXT | Product code |
| product_length | DOUBLE | Roll length in meters |
| batch | TEXT | Batch number (number only) |
| cycle_time | DOUBLE | Cycle time in seconds |
| roll_time | DOUBLE | Roll time in seconds |
| timestamp | TIMESTAMPTZ | When the log was created |
| settings_timestamp | TEXT | Last settings update time |

### batch_metadata Table

| Column | Type | Description |
|--------|------|-------------|
| id | BIGSERIAL | Auto-increment primary key |
| batch | TEXT | Batch number (unique) |
| product_code | TEXT | Product code |
| product_name | TEXT | Product name |
| start_time | TIMESTAMPTZ | Batch start time |
| end_time | TIMESTAMPTZ | Batch end time |
| total_rolls | INTEGER | Total number of rolls |
| total_length | DOUBLE | Total length produced |
| avg_cycle_time | DOUBLE | Average cycle time |
| avg_roll_time | DOUBLE | Average roll time |
| status | TEXT | active, completed, archived |

## 🔍 Useful SQL Queries

### Get today's batches:
```sql
SELECT DISTINCT batch FROM production_logs 
WHERE timestamp::date = CURRENT_DATE 
ORDER BY batch DESC;
```

### Get batch summary:
```sql
SELECT * FROM batch_summary 
WHERE batch = '1';
```

### Get production by product:
```sql
SELECT 
    product_code,
    COUNT(*) as total_rolls,
    SUM(product_length) as total_length
FROM production_logs 
WHERE timestamp::date = CURRENT_DATE
GROUP BY product_code
ORDER BY total_rolls DESC;
```

## 🐛 Troubleshooting

### Batch Not Auto-Generating

1. Check batch_number field is **empty** before clicking "Send to Device"
2. Check logs: `logs/monitor_YYYYMMDD.log`
3. Look for: `"Auto-generated batch: YYYYMMDD-N for product: XXX"`

### Supabase Connection Issues

1. Check internet connection
2. Verify credentials in `config.json`
3. Check Supabase project status
4. View logs for error messages
5. **Fallback**: Data will still save to local JSON

### Recap Dialog Not Showing Data

1. Click "🔄 Refresh" button
2. Check if batch exists in dropdown
3. Verify data in Supabase dashboard
4. Check local JSON files in `logs/production_log_YYYY-MM-DD.json`

### Cannot Export CSV

1. Check `exports/` folder exists
2. Verify write permissions
3. Check logs for export errors

## 📝 Best Practices

1. **Let the system auto-generate batches** - Only use manual batch when necessary

2. **Regular backups** - Export batch data to CSV regularly

3. **Monitor Supabase usage** - Check your Supabase project dashboard for storage/usage

4. **Archive old data** - Use the maintenance queries in `SUPABASE_SCHEMA.sql`

5. **Test offline mode** - Ensure local JSON backup works when offline

## 🔐 Security Notes

- API key is **ANON key** (safe for client-side use)
- Row Level Security (RLS) is enabled on all tables
- Data is transmitted over HTTPS
- Local JSON files are backup only

## 📞 Support

For issues or questions:
1. Check logs: `logs/monitor_YYYYMMDD.log`
2. Review error messages in the application
3. Check Supabase dashboard for database issues
4. Contact system administrator

---

**Version**: 1.0.0
**Last Updated**: 2025-10-03


-- ============================================
-- COMPLETE DATABASE SETUP FOR PIKCARZ
-- Run this in Neon SQL Editor
-- ============================================

-- Step 1: Verify users table exists
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name = 'users';

-- Step 2: Check if 'admin' role exists in enum
SELECT enum_range(NULL::userrole);

-- Step 3: Add 'admin' to enum if missing
ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'admin';

-- Step 4: Create password reset tokens table
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Step 5: Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_password_reset_token ON password_reset_tokens(token);
CREATE INDEX IF NOT EXISTS idx_password_reset_user ON password_reset_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_password_reset_expires ON password_reset_tokens(expires_at);

-- Step 6: Verify all tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Step 7: Check admin users
SELECT id, email, full_name, role 
FROM users 
WHERE role = 'admin';

-- ============================================
-- If no admin users, create them:
-- ============================================

-- IMPORTANT: Only run this if you need to create admin accounts
-- First create the accounts via API/DevTools, then upgrade with:

/*
UPDATE users 
SET role = 'admin' 
WHERE email IN (
  'gershon@pikcarz.co.za',
  'davy@pikcarz.co.za',
  'admin3@pikcarz.co.za'
);
*/

-- ============================================
-- VERIFY EVERYTHING IS SET UP
-- ============================================

-- Check users table structure
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'users'
ORDER BY ordinal_position;

-- Check password_reset_tokens structure
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'password_reset_tokens'
ORDER BY ordinal_position;

-- Count records
SELECT 
    (SELECT COUNT(*) FROM users) as total_users,
    (SELECT COUNT(*) FROM users WHERE role = 'admin') as total_admins,
    (SELECT COUNT(*) FROM vehicles) as total_vehicles,
    (SELECT COUNT(*) FROM password_reset_tokens) as total_reset_tokens;

-- ============================================
-- SUCCESS CRITERIA:
-- ============================================
-- ✅ users table exists
-- ✅ userrole enum includes 'admin'
-- ✅ password_reset_tokens table exists
-- ✅ All indexes created
-- ✅ At least 1 admin user exists
-- ============================================

-- ===============================================
-- FanTestDataに外部キー制約を満たすサンプルデータを追加
-- ===============================================

-- Step 1: 参照先テーブルから既存の値を取得して確認
SELECT 'Fan list' as table_name, COUNT(*) as count FROM "Fan list"
UNION ALL
SELECT 'Hako list', COUNT(*) FROM "Hako list"
UNION ALL
SELECT 'heat_exchanger', COUNT(*) FROM "heat_exchanger"
UNION ALL
SELECT 'Unit list', COUNT(*) FROM "Unit list";

-- Step 2: 各参照先テーブルの値をサンプル表示
SELECT 'Available fanIDs:' as info;
SELECT "fanID", series, product_type FROM "Fan list" LIMIT 10;

SELECT 'Available hakoIDs:' as info;
SELECT "hakoID", series, subseries FROM "Hako list" LIMIT 10;

SELECT 'Available 熱交_id:' as info;
SELECT "熱交_id", "フィンシリーズ" FROM "heat_exchanger" LIMIT 10;

SELECT 'Available Unit IDs:' as info;
SELECT id, product_type FROM "Unit list" LIMIT 10;

-- Step 3: CTEを使用して参照先の値を取得し、FanTestDataに挿入
WITH fan_ids AS (
  SELECT "fanID" FROM "Fan list" LIMIT 5
),
hako_ids AS (
  SELECT "hakoID" FROM "Hako list" LIMIT 4
),
hex_ids AS (
  SELECT "熱交_id" FROM "heat_exchanger" LIMIT 4
),
unit_ids AS (
  SELECT id FROM "Unit list" LIMIT 3
),
sample_data AS (
  SELECT 
    ROW_NUMBER() OVER () as rn,
    f."fanID",
    h."hakoID",
    x."熱交_id",
    u.id as unit_id
  FROM fan_ids f
  CROSS JOIN hako_ids h
  CROSS JOIN hex_ids x
  CROSS JOIN unit_ids u
  LIMIT 20
)
INSERT INTO "FanTestData" (
  "fanID",
  "FanName",
  "TestDate",
  "tested_at",
  "test_facillity",
  "comment",
  "SingleFanTest",
  "bellmouth",
  "Unit",
  "Hako",
  "Hex",
  "temp_o_[degC]",
  "temp_c_[defC]",
  "Ps_[Pa]",
  "Q_[m3min]",
  "Torque_[mNm]",
  "Power_[W]",
  "SPL_[dbA]"
)
SELECT
  "fanID",
  'TestFan-' || rn::text as "FanName",
  CURRENT_DATE - (rn || ' days')::interval as "TestDate",
  'Lab-' || (rn % 3 + 1)::text as tested_at,
  jsonb_build_object('facility', 'Lab-' || (rn % 3 + 1)::text, 'room', 'Room-' || (rn % 5 + 1)::text) as test_facillity,
  'Sample test data ' || rn::text as comment,
  (rn % 2 = 0) as "SingleFanTest",
  'Bell-' || (rn % 4 + 1)::text as bellmouth,
  unit_id as "Unit",
  "hakoID" as "Hako",
  "熱交_id" as "Hex",
  20.0 + (rn % 10) as "temp_o_[degC]",
  21.0 + (rn % 10) as "temp_c_[defC]",
  jsonb_build_array(100 + rn * 10, 150 + rn * 10, 200 + rn * 10, 250 + rn * 10, 300 + rn * 10) as "Ps_[Pa]",
  jsonb_build_array(10.0 + rn, 12.0 + rn, 14.0 + rn, 16.0 + rn, 18.0 + rn) as "Q_[m3min]",
  jsonb_build_array(80 + rn * 2, 85 + rn * 2, 90 + rn * 2, 95 + rn * 2, 100 + rn * 2) as "Torque_[mNm]",
  jsonb_build_array(40 + rn * 3, 45 + rn * 3, 50 + rn * 3, 55 + rn * 3, 60 + rn * 3) as "Power_[W]",
  jsonb_build_array(42, 44, 46, 48, 50) as "SPL_[dbA]"
FROM sample_data;

-- Step 4: 追加されたデータを確認
SELECT COUNT(*) as total_fantestdata FROM "FanTestData";
SELECT * FROM "FanTestData" ORDER BY id DESC LIMIT 10;

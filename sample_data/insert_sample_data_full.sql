-- ===============================================
-- サンプルデータ追加SQL（制約を満たす順序で実行）
-- ===============================================

-- 1. fan_type テーブル（既存データがあるのでスキップ）
-- 既存: propeller, sirocco, turbo, line_flow, mixed_flow, other

-- 2. Fan list テーブル（20件以上追加、既存のfan_typeを使用）
INSERT INTO "Fan list" (series, product_type, innerouter, diameter, year, fan_type)
VALUES
    ('Series-A', 'Axial', 'Inner', 100, 2020, 'propeller'),
    ('Series-A', 'Axial', 'Outer', 120, 2021, 'propeller'),
    ('Series-B', 'Centrifugal', 'Inner', 150, 2020, 'sirocco'),
    ('Series-B', 'Centrifugal', 'Outer', 200, 2021, 'sirocco'),
    ('Series-C', 'Mixed Flow', 'Inner', 100, 2022, 'mixed_flow'),
    ('Series-C', 'Axial', 'Outer', 120, 2022, 'propeller'),
    ('Series-D', 'Centrifugal', 'Inner', 150, 2023, 'turbo'),
    ('Series-D', 'Axial', 'Outer', 200, 2023, 'propeller'),
    ('Series-A', 'Centrifugal', 'Inner', 250, 2024, 'sirocco'),
    ('Series-B', 'Axial', 'Outer', 100, 2024, 'propeller'),
    ('Series-C', 'Centrifugal', 'Inner', 120, 2020, 'turbo'),
    ('Series-D', 'Mixed Flow', 'Outer', 150, 2021, 'mixed_flow'),
    ('Series-A', 'Axial', 'Inner', 200, 2022, 'propeller'),
    ('Series-B', 'Centrifugal', 'Outer', 250, 2023, 'sirocco'),
    ('Series-C', 'Axial', 'Inner', 100, 2024, 'line_flow'),
    ('Series-D', 'Centrifugal', 'Outer', 120, 2020, 'turbo'),
    ('Series-A', 'Mixed Flow', 'Inner', 150, 2021, 'mixed_flow'),
    ('Series-B', 'Axial', 'Outer', 200, 2022, 'propeller'),
    ('Series-C', 'Centrifugal', 'Inner', 250, 2023, 'sirocco'),
    ('Series-D', 'Axial', 'Outer', 100, 2024, 'line_flow'),
    ('Series-A', 'Centrifugal', 'Inner', 120, 2020, 'turbo'),
    ('Series-B', 'Axial', 'Outer', 150, 2021, 'propeller'),
    ('Series-C', 'Mixed Flow', 'Inner', 200, 2022, 'mixed_flow'),
    ('Series-D', 'Centrifugal', 'Outer', 250, 2023, 'sirocco'),
    ('Series-A', 'Axial', 'Inner', 100, 2024, 'other');

-- 3. Hako list テーブル（20件追加）
INSERT INTO "Hako list" (series, subseries)
VALUES
    ('Hako-A', 'Sub-1'),
    ('Hako-A', 'Sub-2'),
    ('Hako-B', 'Sub-1'),
    ('Hako-B', 'Sub-2'),
    ('Hako-C', 'Sub-1'),
    ('Hako-C', 'Sub-2'),
    ('Hako-D', 'Sub-1'),
    ('Hako-D', 'Sub-2'),
    ('Hako-A', 'Sub-3'),
    ('Hako-B', 'Sub-3'),
    ('Hako-C', 'Sub-3'),
    ('Hako-D', 'Sub-3'),
    ('Hako-A', 'Sub-4'),
    ('Hako-B', 'Sub-4'),
    ('Hako-C', 'Sub-4'),
    ('Hako-D', 'Sub-4'),
    ('Hako-A', 'Sub-5'),
    ('Hako-B', 'Sub-5'),
    ('Hako-C', 'Sub-5'),
    ('Hako-D', 'Sub-5');

-- 4. heat_exchanger テーブル（20件追加）
INSERT INTO "heat_exchanger" (熱交_id, フィンシリーズ, 列数, 段数, 伝熱面積, フィンピッチ, チューブ外径, 備考)
VALUES
    ('HEX-001', 'Fin-A', 2, 3, 1.5, 2.0, 7.0, 'Standard'),
    ('HEX-002', 'Fin-B', 3, 4, 2.0, 2.5, 8.0, 'High efficiency'),
    ('HEX-003', 'Fin-A', 2, 4, 1.8, 2.0, 7.0, 'Compact'),
    ('HEX-004', 'Fin-C', 4, 5, 2.5, 3.0, 9.0, 'Heavy duty'),
    ('HEX-005', 'Fin-B', 3, 3, 1.7, 2.5, 8.0, 'Standard'),
    ('HEX-006', 'Fin-A', 2, 5, 2.2, 2.0, 7.0, 'Extended'),
    ('HEX-007', 'Fin-C', 4, 4, 2.3, 3.0, 9.0, 'Premium'),
    ('HEX-008', 'Fin-B', 3, 4, 2.0, 2.5, 8.0, 'Standard'),
    ('HEX-009', 'Fin-A', 2, 3, 1.6, 2.0, 7.0, 'Compact'),
    ('HEX-010', 'Fin-C', 4, 5, 2.6, 3.0, 9.0, 'High capacity'),
    ('HEX-011', 'Fin-B', 3, 3, 1.8, 2.5, 8.0, 'Standard'),
    ('HEX-012', 'Fin-A', 2, 4, 1.9, 2.0, 7.0, 'Medium'),
    ('HEX-013', 'Fin-C', 4, 4, 2.4, 3.0, 9.0, 'Premium'),
    ('HEX-014', 'Fin-B', 3, 5, 2.1, 2.5, 8.0, 'Extended'),
    ('HEX-015', 'Fin-A', 2, 3, 1.5, 2.0, 7.0, 'Basic'),
    ('HEX-016', 'Fin-C', 4, 5, 2.7, 3.0, 9.0, 'Super duty'),
    ('HEX-017', 'Fin-B', 3, 4, 2.0, 2.5, 8.0, 'Standard'),
    ('HEX-018', 'Fin-A', 2, 4, 1.8, 2.0, 7.0, 'Compact'),
    ('HEX-019', 'Fin-C', 4, 3, 2.2, 3.0, 9.0, 'Wide'),
    ('HEX-020', 'Fin-B', 3, 5, 2.3, 2.5, 8.0, 'Long');

-- 確認用クエリ
SELECT 'fan_type' as table_name, COUNT(*) as record_count FROM "fan_type"
UNION ALL
SELECT 'Fan list', COUNT(*) FROM "Fan list"
UNION ALL
SELECT 'Hako list', COUNT(*) FROM "Hako list"
UNION ALL
SELECT 'heat_exchanger', COUNT(*) FROM "heat_exchanger";

-- Fan listの最新レコードを確認
SELECT * FROM "Fan list" ORDER BY id DESC LIMIT 10;

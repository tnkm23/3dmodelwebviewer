-- Fan listテーブルに20件のサンプルデータを追加するSQL

INSERT INTO "Fan list" (series, product_type, innerouter, diameter, year, fan_type)
VALUES
('Series-A', 'Axial', 'Inner', 100, 2020, 'axial'),
('Series-B', 'Centrifugal', 'Outer', 120, 2021, 'centrifugal'),
('Series-C', 'Mixed Flow', 'Inner', 150, 2022, 'axial'),
('Series-D', 'Axial', 'Outer', 200, 2023, 'centrifugal'),
('Series-A', 'Centrifugal', 'Inner', 250, 2024, 'axial'),
('Series-B', 'Axial', 'Outer', 100, 2020, 'centrifugal'),
('Series-C', 'Centrifugal', 'Inner', 120, 2021, 'axial'),
('Series-D', 'Mixed Flow', 'Outer', 150, 2022, 'centrifugal'),
('Series-A', 'Axial', 'Inner', 200, 2023, 'axial'),
('Series-B', 'Centrifugal', 'Outer', 250, 2024, 'centrifugal'),
('Series-C', 'Axial', 'Inner', 100, 2020, 'axial'),
('Series-D', 'Centrifugal', 'Outer', 120, 2021, 'centrifugal'),
('Series-A', 'Mixed Flow', 'Inner', 150, 2022, 'axial'),
('Series-B', 'Axial', 'Outer', 200, 2023, 'centrifugal'),
('Series-C', 'Centrifugal', 'Inner', 250, 2024, 'axial'),
('Series-D', 'Axial', 'Outer', 100, 2020, 'centrifugal'),
('Series-A', 'Centrifugal', 'Inner', 120, 2021, 'axial'),
('Series-B', 'Mixed Flow', 'Outer', 150, 2022, 'centrifugal'),
('Series-C', 'Axial', 'Inner', 200, 2023, 'axial'),
('Series-D', 'Centrifugal', 'Outer', 250, 2024, 'centrifugal');

-- 追加されたレコード数を確認
SELECT COUNT(*) as total_records FROM "Fan list";

-- 最近追加されたレコードを確認
SELECT * FROM "Fan list" ORDER BY id DESC LIMIT 20;

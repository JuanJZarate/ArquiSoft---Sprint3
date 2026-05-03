INSERT INTO reportes_proyecto (id, nombre, descripcion) VALUES
(1, 'Riot Games', 'Manejo de costos en la nube para Riot Games en el contexto de los mundiales de League of Legends.'),
(2, 'Netflix', 'Manejo de costos en la nube para Netflix en el contexto de los lanzamientos de contenido.'),
(3, 'NASA', 'Manejo de costos en la nube para NASA, porque aparentemente llegar a la Luna sale más barato que mantener los servidores.');

INSERT INTO reportes_usuario (id, nombre, email, proyecto_id) VALUES
(1, 'Faker', 'faker@example.com', 1),
(2, 'Doublelift', 'doublelift@example.com', 2),
(3, 'Miss Fortune', 'miss.fortune@example.com', 1),
(4, 'Teemo', 'teemo.terrordelabosque@riotgames.com', 1),
(5, 'Walter White', 'w.white.notaspaceship@nasa.gov', 3),
(6, 'Elon Musk', 'jefe.delosjefes@nasa.gov', 3),
(7, 'Charlie Kirk', 'charlie.kirk@example.com', 1);

INSERT INTO reportes_consumomensual (id, proyecto_id, mes, anio, costo_total) VALUES
-- Riot Games (proyecto 1): costos disparados en octubre/noviembre por los Worlds
(1,  1, 1,  2023, 1200.00),
(2,  1, 2,  2023, 1150.50),
(3,  1, 3,  2023, 1300.75),
(4,  1, 4,  2023, 1100.00),
(5,  1, 5,  2023, 1250.25),
(6,  1, 6,  2023, 1180.00),
(7,  1, 7,  2023, 1320.00),
(8,  1, 8,  2023, 1400.00),
(9,  1, 9,  2023, 1600.00),
(10, 1, 10, 2023, 9800.00),  -- Worlds empieza, servidores en llamas
(11, 1, 11, 2023, 12500.99), -- Final de Worlds, Faker gana otra vez
(12, 1, 12, 2023, 1350.00),
(13, 1, 1,  2024, 1280.00),
(14, 1, 2,  2024, 1190.00),
-- Netflix (proyecto 2): picos cuando lanzan temporadas nuevas
(15, 2, 1,  2023, 3100.00),
(16, 2, 2,  2023, 2900.50),
(17, 2, 3,  2023, 3400.00),  -- lanzamiento temporada nueva, todo el mundo ve lo mismo
(18, 2, 4,  2023, 2750.00),
(19, 2, 5,  2023, 2800.75),
(20, 2, 6,  2023, 3050.00),
(21, 2, 7,  2023, 3200.00),
(22, 2, 8,  2023, 2950.00),
(23, 2, 9,  2023, 3600.00),  -- el show del que todos hablan pero nadie termina
(24, 2, 10, 2023, 2700.00),
(25, 2, 11, 2023, 2850.00),
(26, 2, 12, 2023, 4100.00),  -- todos en vacaciones pegados al sofá
(27, 2, 1,  2024, 3300.00),
-- NASA (proyecto 3): siempre caro, a veces inexplicablemente más caro
(28, 3, 1,  2023, 15000.00),
(29, 3, 2,  2023, 14800.50),
(30, 3, 3,  2023, 16200.00),
(31, 3, 4,  2023, 14500.00),
(32, 3, 5,  2023, 15800.75),
(33, 3, 6,  2023, 99999.99), -- alguien dejó un for loop infinito en producción
(34, 3, 7,  2023, 15100.00),
(35, 3, 8,  2023, 16500.00),
(36, 3, 9,  2023, 14900.00),
(37, 3, 10, 2023, 17200.00),
(38, 3, 11, 2023, 15600.00),
(39, 3, 12, 2023, 18000.00), -- regalo de navidad a AWS
(40, 3, 1,  2024, 16100.00);

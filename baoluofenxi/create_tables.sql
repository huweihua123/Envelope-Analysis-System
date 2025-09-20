-- 包络分析系统数据库表结构 (无外键版本)
-- 设置字符集
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for experiment_types
-- ----------------------------
DROP TABLE IF EXISTS `experiment_types`;
CREATE TABLE `experiment_types` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `time_column` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `data_columns` json NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `name`(`name` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for experiment_data
-- ----------------------------
DROP TABLE IF EXISTS `experiment_data`;
CREATE TABLE `experiment_data` (
  `id` int NOT NULL AUTO_INCREMENT,
  `experiment_type_id` int NULL DEFAULT NULL,
  `data_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `file_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `clickhouse_table_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `row_count` int NULL DEFAULT NULL,
  `upload_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `is_historical` tinyint(1) NULL DEFAULT 0,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT 'active',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `clickhouse_table_name`(`clickhouse_table_name` ASC) USING BTREE,
  INDEX `experiment_type_id`(`experiment_type_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for envelope_settings
-- ----------------------------
DROP TABLE IF EXISTS `envelope_settings`;
CREATE TABLE `envelope_settings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `experiment_type_id` int NULL DEFAULT NULL,
  `selected_columns` json NULL,
  `time_range_start` decimal(10, 2) NULL DEFAULT NULL,
  `time_range_end` decimal(10, 2) NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `experiment_type_id`(`experiment_type_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for envelope_cache
-- ----------------------------
DROP TABLE IF EXISTS `envelope_cache`;
CREATE TABLE `envelope_cache` (
  `id` int NOT NULL AUTO_INCREMENT,
  `experiment_type_id` int NOT NULL,
  `selected_columns_hash` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `historical_data_ids` json NOT NULL,
  `envelope_data` json NOT NULL,
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `expires_at` datetime NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `experiment_type_id`(`experiment_type_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- 插入一些测试数据
-- ----------------------------
INSERT INTO `experiment_types` (`name`, `description`, `time_column`, `data_columns`) VALUES
('温度测试', '温度传感器数据测试', 't', '["C1", "C2", "C3"]'),
('压力测试', '压力传感器数据测试', 'time', '["P1", "P2", "P3", "P4"]'),
('振动测试', '振动传感器数据测试', 't', '["V1", "V2", "V3", "V4", "V5"]');

SET FOREIGN_KEY_CHECKS = 1;

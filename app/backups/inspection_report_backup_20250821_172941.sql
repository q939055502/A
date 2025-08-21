-- MySQL dump 10.13  Distrib 5.7.41, for Win64 (x86_64)
--
-- Host: localhost    Database: inspection_report
-- ------------------------------------------------------
-- Server version	5.7.41-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
INSERT INTO `alembic_version` VALUES ('4fa8b40efa28');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `announcements`
--

DROP TABLE IF EXISTS `announcements`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `announcements` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `icon` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `priority` int(11) DEFAULT NULL,
  `start_date` datetime DEFAULT NULL,
  `end_date` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  `is_deleted` tinyint(1) DEFAULT NULL,
  `created_by_nickname` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `created_by` (`created_by`),
  KEY `ix_announcements_id` (`id`),
  KEY `ix_announcements_title` (`title`),
  CONSTRAINT `announcements_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `announcements`
--

LOCK TABLES `announcements` WRITE;
/*!40000 ALTER TABLE `announcements` DISABLE KEYS */;
/*!40000 ALTER TABLE `announcements` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `certificates`
--

DROP TABLE IF EXISTS `certificates`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `certificates` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `certificate_name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `issuing_authority` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `issue_date` datetime NOT NULL,
  `expiry_date` datetime DEFAULT NULL,
  `certificate_number` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_certificates_id` (`id`),
  KEY `ix_certificates_user_id` (`user_id`),
  CONSTRAINT `certificates_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `certificates`
--

LOCK TABLES `certificates` WRITE;
/*!40000 ALTER TABLE `certificates` DISABLE KEYS */;
/*!40000 ALTER TABLE `certificates` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `educations`
--

DROP TABLE IF EXISTS `educations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `educations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `education_level` int(11) NOT NULL,
  `school_name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `major` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `graduation_date` datetime NOT NULL,
  `degree_certificate_number` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_educations_id` (`id`),
  KEY `ix_educations_user_id` (`user_id`),
  CONSTRAINT `educations_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `educations`
--

LOCK TABLES `educations` WRITE;
/*!40000 ALTER TABLE `educations` DISABLE KEYS */;
/*!40000 ALTER TABLE `educations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inspection_reports`
--

DROP TABLE IF EXISTS `inspection_reports`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inspection_reports` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `project_name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '工程名称',
  `project_location` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '工程地址',
  `project_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '工程类型',
  `project_stage` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '工程阶段',
  `construction_unit` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '建设单位',
  `contractor` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '施工单位',
  `supervisor` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '监理单位',
  `witness_unit` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '见证单位',
  `remarks` text COLLATE utf8mb4_unicode_ci COMMENT '备注',
  `client_unit` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '委托单位',
  `client_contact` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '委托人',
  `acceptance_date` date DEFAULT NULL COMMENT '受理日期',
  `commission_date` date DEFAULT NULL COMMENT '委托日期',
  `commission_code` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '委托编号',
  `salesperson` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '业务员',
  `inspection_unit` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '检测单位',
  `certificate_no` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '资质证书编号',
  `contact_address` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '联系地址',
  `contact_phone` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '联系电话',
  `registrant` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '登记人',
  `inspection_object` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '检测对象',
  `object_part` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '检测部位',
  `object_spec` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '对象规格',
  `design_spec` text COLLATE utf8mb4_unicode_ci COMMENT '设计要求',
  `inspection_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '检验类型',
  `inspection_items` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '检测项目',
  `test_items` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '检测项详情',
  `inspection_quantity` int(11) DEFAULT NULL COMMENT '检测数量',
  `measurement_unit` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '计量单位',
  `inspection_conclusion` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '检测结论',
  `conclusion_description` text COLLATE utf8mb4_unicode_ci COMMENT '结论描述',
  `is_recheck` tinyint(1) DEFAULT NULL COMMENT '是否复检',
  `sampling_method` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '抽样方式',
  `sampling_date` date DEFAULT NULL COMMENT '抽样日期',
  `sampler` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '抽样人员',
  `start_date` date DEFAULT NULL COMMENT '开始日期',
  `end_date` date DEFAULT NULL COMMENT '结束日期',
  `inspection_code` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '检测编号',
  `inspector` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '检测员',
  `tester_date` date DEFAULT NULL COMMENT '检测完成日期',
  `reviewer` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '审核人',
  `review_date` date DEFAULT NULL COMMENT '审核日期',
  `approver` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '批准人',
  `approve_date` date DEFAULT NULL COMMENT '批准日期',
  `report_date` date NOT NULL COMMENT '报告日期',
  `issue_date` date DEFAULT NULL COMMENT '签发日期',
  `report_code` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '报告编号',
  `report_status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '报告状态',
  `qrcode_content` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '二维码内容',
  `attachment_paths` json DEFAULT NULL COMMENT '附件路径',
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `is_deleted` tinyint(1) DEFAULT NULL,
  `last_modified_by` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '最后修改人',
  `registrant_id` int(11) DEFAULT NULL COMMENT '登记人ID',
  `last_modified_by_id` int(11) DEFAULT NULL COMMENT '最后修改人ID',
  PRIMARY KEY (`id`),
  UNIQUE KEY `report_code` (`report_code`),
  KEY `fk_inspection_reports_registrant_id` (`registrant_id`),
  KEY `fk_inspection_reports_last_modified_by_id` (`last_modified_by_id`),
  CONSTRAINT `fk_inspection_reports_last_modified_by_id` FOREIGN KEY (`last_modified_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `fk_inspection_reports_registrant_id` FOREIGN KEY (`registrant_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inspection_reports`
--

LOCK TABLES `inspection_reports` WRITE;
/*!40000 ALTER TABLE `inspection_reports` DISABLE KEYS */;
/*!40000 ALTER TABLE `inspection_reports` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `permissions`
--

DROP TABLE IF EXISTS `permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `resource` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `action` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `scope` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_permissions_code` (`code`),
  KEY `created_by` (`created_by`),
  KEY `ix_permissions_id` (`id`),
  CONSTRAINT `permissions_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=146 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permissions`
--

LOCK TABLES `permissions` WRITE;
/*!40000 ALTER TABLE `permissions` DISABLE KEYS */;
INSERT INTO `permissions` VALUES (117,'user:view:own','user','view','own','查看自己的用户信息',1,'2025-08-21 09:24:52','2025-08-21 09:24:52',NULL),(118,'user:view:all','user','view','all','查看所有用户信息',1,'2025-08-21 09:24:52','2025-08-21 09:24:52',NULL),(119,'user:create','user','create','all','创建新用户',1,'2025-08-21 09:24:52','2025-08-21 09:24:52',NULL),(120,'user:edit:own','user','edit','own','编辑自己的用户信息',1,'2025-08-21 09:24:52','2025-08-21 09:24:52',NULL),(121,'user:edit:all','user','edit','all','编辑所有用户信息',1,'2025-08-21 09:24:52','2025-08-21 09:24:52',NULL),(122,'user:delete','user','delete','all','删除用户',1,'2025-08-21 09:24:52','2025-08-21 09:24:52',NULL),(123,'user:export','user','export','all','导出用户数据',1,'2025-08-21 09:24:52','2025-08-21 09:24:52',NULL),(124,'user:role:manage','user','role:manage','all','管理用户角色',1,'2025-08-21 09:24:52','2025-08-21 09:24:52',NULL),(125,'user:permission:manage','user','permission:manage','all','管理用户权限',1,'2025-08-21 09:24:52','2025-08-21 09:24:52',NULL),(126,'inspection_report:view:own','inspection_report','view','own','查看自己的检测报告',1,'2025-08-21 09:24:52','2025-08-21 09:24:52',NULL),(127,'inspection_report:view:all','inspection_report','view','all','查看所有检测报告',1,'2025-08-21 09:24:52','2025-08-21 09:24:52',NULL),(128,'inspection_report:create','inspection_report','create','all','创建检测报告',1,'2025-08-21 09:24:52','2025-08-21 09:24:52',NULL),(129,'inspection_report:edit:own','inspection_report','edit','own','编辑自己的检测报告',1,'2025-08-21 09:24:52','2025-08-21 09:24:52',NULL),(130,'inspection_report:edit:all','inspection_report','edit','all','编辑所有检测报告',1,'2025-08-21 09:24:52','2025-08-21 09:24:52',NULL),(131,'inspection_report:delete:own','inspection_report','delete','own','删除自己的检测报告',1,'2025-08-21 09:24:52','2025-08-21 09:24:52',NULL),(132,'inspection_report:delete:all','inspection_report','delete','all','删除所有检测报告',1,'2025-08-21 09:24:52','2025-08-21 09:24:52',NULL),(133,'inspection_report:approve:all','inspection_report','approve','all','审批检测报告',1,'2025-08-21 09:24:52','2025-08-21 09:24:52',NULL),(134,'inspection_report:export','inspection_report','export','all','导出检测报告',1,'2025-08-21 09:24:52','2025-08-21 09:24:52',NULL),(135,'inspection_report:print','inspection_report','print','all','打印检测报告',1,'2025-08-21 09:24:52','2025-08-21 09:24:52',NULL),(136,'announcement:view:all','announcement','view','all','查看所有公告',1,'2025-08-21 09:24:52','2025-08-21 09:24:52',NULL),(137,'announcement:create','announcement','create','all','创建公告',1,'2025-08-21 09:24:52','2025-08-21 09:24:52',NULL),(138,'announcement:edit:all','announcement','edit','all','编辑所有公告',1,'2025-08-21 09:24:52','2025-08-21 09:24:52',NULL),(139,'announcement:delete:all','announcement','delete','all','删除所有公告',1,'2025-08-21 09:24:52','2025-08-21 09:24:52',NULL),(140,'announcement:pin:manage','announcement','pin:manage','all','管理公告置顶状态',1,'2025-08-21 09:24:52','2025-08-21 09:24:52',NULL),(141,'announcement:active:manage','announcement','active:manage','all','管理公告激活状态',1,'2025-08-21 09:24:52','2025-08-21 09:24:52',NULL),(142,'system:role:manage','system','role:manage','all','管理角色',1,'2025-08-21 09:24:52','2025-08-21 09:24:52',NULL),(143,'system:permission:manage','system','permission:manage','all','管理权限',1,'2025-08-21 09:24:52','2025-08-21 09:24:52',NULL),(144,'system:config:edit','system','config:edit','all','编辑系统参数',1,'2025-08-21 09:24:52','2025-08-21 09:24:52',NULL),(145,'system:log:view','system','log:view','all','查看系统日志',1,'2025-08-21 09:24:52','2025-08-21 09:24:52',NULL);
/*!40000 ALTER TABLE `permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `role_permissions`
--

DROP TABLE IF EXISTS `role_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `role_permissions` (
  `role_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`role_id`,`permission_id`),
  KEY `created_by` (`created_by`),
  KEY `permission_id` (`permission_id`),
  CONSTRAINT `role_permissions_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`),
  CONSTRAINT `role_permissions_ibfk_2` FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`id`),
  CONSTRAINT `role_permissions_ibfk_3` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `role_permissions`
--

LOCK TABLES `role_permissions` WRITE;
/*!40000 ALTER TABLE `role_permissions` DISABLE KEYS */;
INSERT INTO `role_permissions` VALUES (21,117,'2025-08-21 09:24:52',NULL,1),(21,118,'2025-08-21 09:24:52',NULL,1),(21,119,'2025-08-21 09:24:52',NULL,1),(21,120,'2025-08-21 09:24:52',NULL,1),(21,121,'2025-08-21 09:24:52',NULL,1),(21,122,'2025-08-21 09:24:52',NULL,1),(21,123,'2025-08-21 09:24:52',NULL,1),(21,124,'2025-08-21 09:24:52',NULL,1),(21,125,'2025-08-21 09:24:52',NULL,1),(21,126,'2025-08-21 09:24:52',NULL,1),(21,127,'2025-08-21 09:24:52',NULL,1),(21,128,'2025-08-21 09:24:52',NULL,1),(21,129,'2025-08-21 09:24:52',NULL,1),(21,130,'2025-08-21 09:24:52',NULL,1),(21,131,'2025-08-21 09:24:52',NULL,1),(21,132,'2025-08-21 09:24:52',NULL,1),(21,133,'2025-08-21 09:24:52',NULL,1),(21,134,'2025-08-21 09:24:52',NULL,1),(21,135,'2025-08-21 09:24:52',NULL,1),(21,136,'2025-08-21 09:24:52',NULL,1),(21,137,'2025-08-21 09:24:52',NULL,1),(21,138,'2025-08-21 09:24:52',NULL,1),(21,139,'2025-08-21 09:24:52',NULL,1),(21,140,'2025-08-21 09:24:52',NULL,1),(21,141,'2025-08-21 09:24:52',NULL,1),(21,142,'2025-08-21 09:24:52',NULL,1),(21,143,'2025-08-21 09:24:52',NULL,1),(21,144,'2025-08-21 09:24:52',NULL,1),(21,145,'2025-08-21 09:24:52',NULL,1),(22,118,'2025-08-21 09:24:52',NULL,1),(22,127,'2025-08-21 09:24:52',NULL,1),(22,133,'2025-08-21 09:24:52',NULL,1),(23,118,'2025-08-21 09:24:52',NULL,1),(23,121,'2025-08-21 09:24:52',NULL,1),(23,127,'2025-08-21 09:24:52',NULL,1),(23,128,'2025-08-21 09:24:52',NULL,1),(23,130,'2025-08-21 09:24:52',NULL,1),(23,132,'2025-08-21 09:24:52',NULL,1),(23,136,'2025-08-21 09:24:52',NULL,1),(23,137,'2025-08-21 09:24:52',NULL,1),(23,138,'2025-08-21 09:24:52',NULL,1),(23,139,'2025-08-21 09:24:52',NULL,1),(24,117,'2025-08-21 09:24:52',NULL,1),(24,120,'2025-08-21 09:24:52',NULL,1),(24,127,'2025-08-21 09:24:52',NULL,1),(24,128,'2025-08-21 09:24:52',NULL,1),(24,129,'2025-08-21 09:24:52',NULL,1),(24,131,'2025-08-21 09:24:52',NULL,1),(25,117,'2025-08-21 09:24:52',NULL,1),(25,127,'2025-08-21 09:24:52',NULL,1),(25,136,'2025-08-21 09:24:52',NULL,1);
/*!40000 ALTER TABLE `role_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `roles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `parent_id` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_roles_name` (`name`),
  KEY `parent_id` (`parent_id`),
  KEY `ix_roles_id` (`id`),
  CONSTRAINT `roles_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `roles` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (21,'admin','系统管理员角色，拥有最高权限',NULL,'2025-08-21 09:24:52','2025-08-21 09:24:52',1),(22,'auditor','审核者角色，负责审批检测报告',NULL,'2025-08-21 09:24:52','2025-08-21 09:24:52',1),(23,'editor','编辑者角色，负责创建和编辑内容',NULL,'2025-08-21 09:24:52','2025-08-21 09:24:52',1),(24,'user','普通用户角色，拥有个人信息管理权限',NULL,'2025-08-21 09:24:52','2025-08-21 09:24:52',1),(25,'viewer','访客角色，拥有只读权限',NULL,'2025-08-21 09:24:52','2025-08-21 09:24:52',1);
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `token_blocklist`
--

DROP TABLE IF EXISTS `token_blocklist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `token_blocklist` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `jti` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_token_blocklist_jti` (`jti`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `token_blocklist`
--

LOCK TABLES `token_blocklist` WRITE;
/*!40000 ALTER TABLE `token_blocklist` DISABLE KEYS */;
INSERT INTO `token_blocklist` VALUES (1,'4d0e8416-0b5f-42a4-b805-cc9ec8e9dfff','2025-08-21 07:36:26'),(2,'b807c800-be6d-4b97-b931-dd3623812b72','2025-08-21 09:25:19');
/*!40000 ALTER TABLE `token_blocklist` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_permissions`
--

DROP TABLE IF EXISTS `user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_permissions` (
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `expires_at` datetime DEFAULT NULL,
  PRIMARY KEY (`user_id`,`permission_id`),
  KEY `permission_id` (`permission_id`),
  CONSTRAINT `user_permissions_ibfk_1` FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`id`),
  CONSTRAINT `user_permissions_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_permissions`
--

LOCK TABLES `user_permissions` WRITE;
/*!40000 ALTER TABLE `user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_roles`
--

DROP TABLE IF EXISTS `user_roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_roles` (
  `user_id` int(11) NOT NULL,
  `role_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`user_id`,`role_id`),
  KEY `created_by` (`created_by`),
  KEY `role_id` (`role_id`),
  CONSTRAINT `user_roles_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`),
  CONSTRAINT `user_roles_ibfk_2` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`),
  CONSTRAINT `user_roles_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_roles`
--

LOCK TABLES `user_roles` WRITE;
/*!40000 ALTER TABLE `user_roles` DISABLE KEYS */;
INSERT INTO `user_roles` VALUES (2,21,'2025-08-21 09:24:52',NULL,1);
/*!40000 ALTER TABLE `user_roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone_number` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nickname` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `avatar` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `gender` int(11) DEFAULT NULL,
  `birthday` date DEFAULT NULL,
  `address` text COLLATE utf8mb4_unicode_ci,
  `bio` text COLLATE utf8mb4_unicode_ci,
  `status` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `last_login_at` datetime DEFAULT NULL,
  `last_logout_at` datetime DEFAULT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `openid` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `unionid` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `member_level` int(11) DEFAULT NULL,
  `ext_info` json DEFAULT NULL,
  `position_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `employment_type` int(11) DEFAULT NULL,
  `hire_date` datetime DEFAULT NULL,
  `department_id` int(11) DEFAULT NULL,
  `id_card_number` varchar(128) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `reset_token` varchar(128) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `reset_token_expires` datetime DEFAULT NULL,
  `verification_code` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `verification_code_expires` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_email` (`email`),
  UNIQUE KEY `ix_users_username` (`username`),
  UNIQUE KEY `ix_users_phone_number` (`phone_number`),
  KEY `ix_users_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (2,'admin','admin@example.com','13800138000','scrypt:32768:8:1$C1dNbHimb4KHCkr2$33628e710554e10c4b4eb5ff417adc17ace6c0b50806a1b45b3427e1ddd4fec3f3b406a4a3eb3f3443558b256b9d1030927c4eb1aa42b22b32b580b587c9ec15','管理员',NULL,NULL,NULL,NULL,NULL,1,'2025-08-21 09:22:22','2025-08-21 09:24:52',NULL,NULL,NULL,NULL,NULL,1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-08-21 17:29:41

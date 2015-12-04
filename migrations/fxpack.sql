/*
Navicat MySQL Data Transfer

Source Server         : fxpack
Source Server Version : 50546
Source Host           : localhost:3306
Source Database       : fxpack_real

Target Server Type    : MYSQL
Target Server Version : 50546
File Encoding         : 65001

Date: 2015-12-04 15:45:26
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for roles
-- ----------------------------
DROP TABLE IF EXISTS `roles`;
CREATE TABLE `roles` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(16) NOT NULL,
  `default` bit(1) DEFAULT b'0',
  `permissions` int(4) DEFAULT NULL COMMENT '权限',
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_name` (`name`) USING HASH,
  KEY `index_default` (`default`) USING HASH
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='角色权限列表';


-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `username` varchar(32) NOT NULL,
  `password_hash` varchar(128) NOT NULL,
  `name` varchar(32) DEFAULT NULL,
  `confirmed` bit(1) DEFAULT b'0',
  `last_seen` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `store_cookie_hash` varchar(128) DEFAULT NULL,
  `role_id` int(11) unsigned DEFAULT NULL,
  `member_since` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_uname` (`username`) USING HASH,
  KEY `foreign_roleid` (`role_id`),
  KEY `index_uname` (`username`) USING BTREE,
  CONSTRAINT `foreign_roleid` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='用户信息表';


-- ----------------------------
-- Table structure for sdks
-- ----------------------------
DROP TABLE IF EXISTS `sdks`;
CREATE TABLE `sdks` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `sdk_id` int(8) NOT NULL,
  `sdk_name` varchar(16) NOT NULL,
  `channel_id` int(8) DEFAULT NULL,
  `sub_channel_id` int(8) DEFAULT NULL,
  `note` text,
  `has_config` bit(1) DEFAULT b'1',
  `config_key` text,
  `has_script` bit(1) DEFAULT b'0',
  `script_key` text,
  `has_parser` bit(1) DEFAULT b'0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_sdkid` (`sdk_id`) USING HASH,
  UNIQUE KEY `unique_sdkname` (`sdk_name`) USING HASH,
  KEY `index_sdkid` (`sdk_id`) USING BTREE,
  KEY `index_sdkname` (`sdk_name`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='已接入SDK表';


-- ----------------------------
-- Table structure for games
-- ----------------------------
DROP TABLE IF EXISTS `games`;
CREATE TABLE `games` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(16) NOT NULL,
  `cn_name` varchar(32) NOT NULL,
  `note` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_name` (`name`) USING HASH,
  KEY `index_name` (`name`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='可打包游戏表';


-- ----------------------------
-- Table structure for link_infos
-- ----------------------------
DROP TABLE IF EXISTS `link_infos`;
CREATE TABLE `link_infos` (
  `sid` int(11) unsigned NOT NULL,
  `gid` int(11) unsigned NOT NULL,
  `package_name` varchar(64) NOT NULL,
  `config` text,
  `script` text,
  `parser` text,
  PRIMARY KEY (`sid`,`gid`),
  KEY `foreign_gid` (`gid`),
  CONSTRAINT `foreign_gid` FOREIGN KEY (`gid`) REFERENCES `games` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `foreign_sid` FOREIGN KEY (`sid`) REFERENCES `sdks` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='游戏接入渠道SDK信息配置表';

CREATE DATABASE  IF NOT EXISTS `zebra` /*!40100 DEFAULT CHARACTER SET utf8 */;
USE `zebra`;
-- MySQL dump 10.13  Distrib 5.7.17, for macos10.12 (x86_64)
--
-- Host: localhost    Database: zebra
-- ------------------------------------------------------
-- Server version 5.7.17

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
-- Table structure for table `article`
--

DROP TABLE IF EXISTS `article`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `article` (
  `id` int(32) unsigned NOT NULL AUTO_INCREMENT,
  `link_id` int(32) unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `link_id` (`link_id`),
  CONSTRAINT `article_ibfk_1` FOREIGN KEY (`link_id`) REFERENCES `link` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=101 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `article_word`
--

DROP TABLE IF EXISTS `article_word`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `article_word` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `article_id` int(32) unsigned NOT NULL,
  `word_id` int(32) unsigned NOT NULL,
  `count` int(32) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `id_idx` (`word_id`),
  KEY `article_id` (`article_id`),
  CONSTRAINT `article_word_ibfk_1` FOREIGN KEY (`article_id`) REFERENCES `article` (`id`),
  CONSTRAINT `article_word_ibfk_2` FOREIGN KEY (`word_id`) REFERENCES `word` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1190019 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `domain`
--

DROP TABLE IF EXISTS `domain`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `domain` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `domain_name` varchar(256) NOT NULL DEFAULT '',
  `domain_extension_id` int(32) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `domain_extension_id` (`domain_extension_id`),
  CONSTRAINT `domain_ibfk_1` FOREIGN KEY (`domain_extension_id`) REFERENCES `domain_extension` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4342 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `domain_extension`
--

DROP TABLE IF EXISTS `domain_extension`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `domain_extension` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `extension` varchar(32) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  KEY `extension` (`extension`)
) ENGINE=InnoDB AUTO_INCREMENT=2786 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `domain_relation`
--

DROP TABLE IF EXISTS `domain_relation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `domain_relation` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `base_domain_id` int(32) unsigned NOT NULL,
  `related_domain_id` int(32) unsigned NOT NULL,
  `count` int(32) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `base_domain_id` (`base_domain_id`),
  KEY `related_domain_id` (`related_domain_id`),
  CONSTRAINT `domain_relation_ibfk_1` FOREIGN KEY (`base_domain_id`) REFERENCES `domain` (`id`),
  CONSTRAINT `domain_relation_ibfk_2` FOREIGN KEY (`related_domain_id`) REFERENCES `domain` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=405 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `link`
--

DROP TABLE IF EXISTS `link`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `link` (
  `id` int(32) unsigned NOT NULL AUTO_INCREMENT,
  `created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `link_str` varchar(512) DEFAULT '',
  `domain_id` int(32) unsigned NOT NULL,
  `crawled` tinyint(4) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `domain_id` (`domain_id`),
  CONSTRAINT `link_ibfk_1` FOREIGN KEY (`domain_id`) REFERENCES `domain` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=33459 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tweet_link`
--

DROP TABLE IF EXISTS `tweet_link`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tweet_link` (
  `tweet_id` int(32) unsigned NOT NULL,
  `link_id` int(32) unsigned NOT NULL,
  KEY `tweet_id` (`tweet_id`),
  KEY `link_id` (`link_id`),
  CONSTRAINT `tweet_link_ibfk_1` FOREIGN KEY (`tweet_id`) REFERENCES `tweets` (`id`),
  CONSTRAINT `tweet_link_ibfk_2` FOREIGN KEY (`link_id`) REFERENCES `link` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tweets`
--

DROP TABLE IF EXISTS `tweets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tweets` (
  `id` int(32) unsigned NOT NULL AUTO_INCREMENT,
  `created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `user_id` int(32) unsigned NOT NULL,
  `id_str` varchar(64) DEFAULT NULL,
  `text` varchar(200) DEFAULT NULL,
  `lang` varchar(16) DEFAULT NULL,
  `in_reply_to_user_id` int(32) unsigned DEFAULT NULL,
  `retweet_user` int(32) unsigned DEFAULT NULL,
  `created_at` varchar(64) DEFAULT NULL,
  `retweet_count` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `retweet_user` (`retweet_user`),
  KEY `in_reply_to_user_id` (`in_reply_to_user_id`),
  CONSTRAINT `tweets_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`),
  CONSTRAINT `tweets_ibfk_2` FOREIGN KEY (`retweet_user`) REFERENCES `user` (`id`),
  CONSTRAINT `tweets_ibfk_3` FOREIGN KEY (`in_reply_to_user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12088 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user` (
  `id` int(32) unsigned NOT NULL AUTO_INCREMENT,
  `created_at` varchar(128) NOT NULL DEFAULT '',
  `id_str` varchar(64) NOT NULL DEFAULT '',
  `favourites_count` int(10) unsigned DEFAULT NULL,
  `verified` tinyint(1) DEFAULT NULL,
  `followers_count` int(10) unsigned DEFAULT NULL,
  `friends_count` int(11) unsigned DEFAULT NULL,
  `statuses_count` int(11) unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `twitter_id_str` (`id_str`)
) ENGINE=InnoDB AUTO_INCREMENT=76716 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `word`
--

DROP TABLE IF EXISTS `word`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `word` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `word` varchar(128) NOT NULL DEFAULT '',
  `word_count` double unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `word_UNIQUE` (`word`),
  KEY `word` (`word`)
) ENGINE=InnoDB AUTO_INCREMENT=429881 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2017-05-30 16:00:18

CREATE TABLE `services` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `service_date` date NOT NULL,
  `service_number` varchar(12) NOT NULL,
  `company` varchar(10) NOT NULL,
  `transport_mode` varchar(4) NOT NULL,
  `cancelled` tinyint(1) NOT NULL,
  `partly_cancelled` tinyint(1) NOT NULL,
  `max_delay` smallint(5) unsigned NOT NULL,
  `from` varchar(6) NOT NULL,
  `to` varchar(6) NOT NULL,
  `source` enum('actual','scheduled') NOT NULL,
  PRIMARY KEY (`id`),
  KEY `service_number` (`service_number`),
  KEY `service_date_service_number` (`service_date`,`service_number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `stops` (
  `service_id` int(10) unsigned NOT NULL,
  `stop_nr` tinyint(3) unsigned NOT NULL,
  `stop` varchar(6) NOT NULL,
  `servicenumber` varchar(12) NOT NULL,
  `arrival` datetime DEFAULT NULL,
  `departure` datetime DEFAULT NULL,
  `arrival_delay` smallint(6) NOT NULL,
  `arrival_cancelled` tinyint(1) NOT NULL,
  `arrival_platform` varchar(6) DEFAULT NULL,
  `arrival_platform_scheduled` varchar(6) DEFAULT NULL,
  `departure_delay` smallint(6) NOT NULL,
  `departure_cancelled` tinyint(1) NOT NULL,
  `departure_platform` varchar(6) DEFAULT NULL,
  `departure_platform_scheduled` varchar(6) DEFAULT NULL,
  PRIMARY KEY (`service_id`,`stop_nr`),
  KEY `stop` (`stop`),
  CONSTRAINT `stops_ibfk_1` FOREIGN KEY (`service_id`) REFERENCES `services` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
-- Create syntax for TABLE 'changes'
CREATE TABLE `changes` (
  `station` varchar(6) CHARACTER SET utf8 DEFAULT NULL,
  `fromservice` int(11) NOT NULL,
  `toservice` int(11) NOT NULL,
  `possiblechange` smallint(6) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Create syntax for TABLE 'company'
CREATE TABLE `company` (
  `company` int(11) NOT NULL,
  `code` varchar(9) CHARACTER SET utf8 NOT NULL,
  `name` varchar(29) CHARACTER SET utf8 NOT NULL,
  `timeturn` time DEFAULT NULL,
  PRIMARY KEY (`company`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Create syntax for TABLE 'connmode'
CREATE TABLE `connmode` (
  `code` varchar(4) CHARACTER SET utf8 NOT NULL,
  `connectiontype` smallint(6) NOT NULL,
  `description` varchar(29) CHARACTER SET utf8 DEFAULT NULL,
  PRIMARY KEY (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Create syntax for TABLE 'contconn'
CREATE TABLE `contconn` (
  `fromstation` varchar(6) CHARACTER SET utf8 NOT NULL DEFAULT '',
  `tostation` varchar(6) CHARACTER SET utf8 NOT NULL DEFAULT '',
  `connectiontime` int(11) NOT NULL,
  `connectionmode` varchar(4) CHARACTER SET utf8 NOT NULL DEFAULT '',
  PRIMARY KEY (`fromstation`,`tostation`,`connectionmode`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Create syntax for TABLE 'country'
CREATE TABLE `country` (
  `code` varchar(4) CHARACTER SET utf8 NOT NULL,
  `inland` tinyint(1) NOT NULL,
  `name` varchar(29) CHARACTER SET utf8 NOT NULL,
  PRIMARY KEY (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Create syntax for TABLE 'delivery'
CREATE TABLE `delivery` (
  `company` int(11) DEFAULT NULL,
  `firstday` date DEFAULT NULL,
  `lastday` date DEFAULT NULL,
  `versionnumber` int(11) DEFAULT NULL,
  `description` varchar(29) CHARACTER SET utf8 DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Create syntax for TABLE 'footnote'
CREATE TABLE `footnote` (
  `footnote` int(11) NOT NULL DEFAULT '0',
  `servicedate` date NOT NULL DEFAULT '0000-00-00',
  PRIMARY KEY (`footnote`,`servicedate`),
  KEY `servicedate` (`servicedate`),
  KEY `footnote` (`footnote`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Create syntax for TABLE 'station'
CREATE TABLE `station` (
  `shortname` varchar(6) NOT NULL,
  `trainchanges` smallint(6) DEFAULT NULL,
  `layovertime` int(11) DEFAULT NULL,
  `country` varchar(4) DEFAULT NULL,
  `timezone` int(11) DEFAULT NULL,
  `x` int(11) DEFAULT NULL,
  `y` int(11) DEFAULT NULL,
  `name` varchar(29) DEFAULT NULL,
  PRIMARY KEY (`shortname`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Create syntax for TABLE 'timetable_attribute'
CREATE TABLE `timetable_attribute` (
  `serviceid` int(11) NOT NULL,
  `code` varchar(4) CHARACTER SET utf8 DEFAULT NULL,
  `firststop` int(1) DEFAULT NULL,
  `laststop` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Create syntax for TABLE 'timetable_platform'
CREATE TABLE `timetable_platform` (
  `serviceid` int(11) NOT NULL DEFAULT '0',
  `idx` int(11) NOT NULL DEFAULT '0',
  `station` varchar(6) CHARACTER SET utf8 DEFAULT NULL,
  `arrival` varchar(4) CHARACTER SET utf8 DEFAULT NULL,
  `departure` varchar(4) CHARACTER SET utf8 DEFAULT NULL,
  `footnote` int(11) DEFAULT NULL,
  PRIMARY KEY (`serviceid`,`idx`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Create syntax for TABLE 'timetable_service'
CREATE TABLE `timetable_service` (
  `serviceid` int(11) NOT NULL,
  `companynumber` int(11) DEFAULT NULL,
  `servicenumber` int(11) DEFAULT NULL,
  `variant` varchar(6) CHARACTER SET utf8 DEFAULT NULL,
  `firststop` int(11) DEFAULT NULL,
  `laststop` int(11) DEFAULT NULL,
  `servicename` varchar(29) CHARACTER SET utf8 DEFAULT NULL,
  KEY `serviceid` (`serviceid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Create syntax for TABLE 'timetable_stop'
CREATE TABLE `timetable_stop` (
  `serviceid` int(11) NOT NULL DEFAULT '0',
  `idx` int(11) NOT NULL DEFAULT '0',
  `station` varchar(6) CHARACTER SET utf8 DEFAULT NULL,
  `arrivaltime` time DEFAULT NULL,
  `departuretime` time DEFAULT NULL,
  PRIMARY KEY (`serviceid`,`idx`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Create syntax for TABLE 'timetable_transport'
CREATE TABLE `timetable_transport` (
  `serviceid` int(11) NOT NULL,
  `transmode` varchar(4) CHARACTER SET utf8 DEFAULT NULL,
  `firststop` int(11) DEFAULT NULL,
  `laststop` int(11) DEFAULT NULL,
  KEY `serviceid` (`serviceid`),
  KEY `transmode` (`transmode`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Create syntax for TABLE 'timetable_validity'
CREATE TABLE `timetable_validity` (
  `serviceid` int(11) NOT NULL,
  `footnote` int(11) DEFAULT NULL,
  `firststop` int(11) DEFAULT NULL,
  `laststop` int(11) DEFAULT NULL,
  UNIQUE KEY `serviceid_2` (`serviceid`,`footnote`),
  KEY `serviceid` (`serviceid`),
  KEY `footnote` (`footnote`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Create syntax for TABLE 'timezone'
CREATE TABLE `timezone` (
  `tznumber` int(11) NOT NULL,
  `difference` int(11) DEFAULT NULL,
  `firstday` date NOT NULL,
  `lastday` date NOT NULL,
  PRIMARY KEY (`tznumber`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Create syntax for TABLE 'trnsaqst'
CREATE TABLE `trnsaqst` (
  `code` varchar(3) CHARACTER SET utf8 NOT NULL DEFAULT '',
  `inclusive` tinyint(1) DEFAULT NULL,
  `question` varchar(29) CHARACTER SET utf8 NOT NULL,
  `transattr` varchar(4) CHARACTER SET utf8 NOT NULL DEFAULT '',
  PRIMARY KEY (`code`,`transattr`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Create syntax for TABLE 'trnsattr'
CREATE TABLE `trnsattr` (
  `code` varchar(4) CHARACTER SET utf8 NOT NULL,
  `processingcode` smallint(6) NOT NULL,
  `description` varchar(30) CHARACTER SET utf8 DEFAULT NULL,
  PRIMARY KEY (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Create syntax for TABLE 'trnsmode'
CREATE TABLE `trnsmode` (
  `code` varchar(4) CHARACTER SET utf8 NOT NULL,
  `description` varchar(29) CHARACTER SET utf8 DEFAULT NULL,
  PRIMARY KEY (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

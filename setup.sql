CREATE TABLE `rovaimt_auth` (
  `id` int NOT NULL AUTO_INCREMENT,
  `token` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
);

INSERT INTO `rovaimt_auth` (`token`) VALUES ('123');

CREATE TABLE `rovaimt_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `endpoint` varchar(100) NOT NULL,
  `token` varchar(100),
  `code` int,
  `msg` varchar(255),
  `sqltime` double,
  `dt` datetime NOT NULL,
  PRIMARY KEY (`id`)
);
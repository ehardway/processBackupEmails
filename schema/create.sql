CREATE TABLE IF NOT EXISTS backup_log (
  id INT(10) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  client VARCHAR(100) NOT NULL,
  server VARCHAR(100) NOT NULL,
  company VARCHAR(100) NOT NULL,
  code VARCHAR(255),
  backupdate DATETIME,
  date_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY client_server_company (client,server,company)
) ENGINE=InnoDB DEFAULT CHARSET latin1;

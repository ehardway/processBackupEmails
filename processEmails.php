#!/usr/bin/php
<?php

chdir(getcwd());

require_once "processEmailsClass.php";
require_once "checkThresholdsClass.php";

$options = parse_ini_file("process_backup_emails.ini");

$processEmails = new processEmails($options);

if ($processEmails->setEmailFileNames()) {
  $processEmails->readEmails();
  $processEmails->parseEmails();
  $processEmails->updateDatabase();
}


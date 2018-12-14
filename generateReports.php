#!/usr/bin/php
<?php

chdir(getcwd());
$options = parse_ini_file("process_backup_emails.ini");
require_once "processEmailsClass.php";
require_once "checkThresholdsClass.php";

$checkThresholds = new checkThresholds($options);
$checkThresholds->determineStatus();
#$checkThresholds->generateCLIreport();
$checkThresholds->generateWebPage();


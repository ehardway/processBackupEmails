<?php

class checkThresholds
{

  private $dbCredentialsIni;
  private $thresholds = [];
  private $thresholdsCleanedUp = [];
  private $dbHandle;
  private $database;
  private $table;
  private $dbData = [];
  private $mergedThresholds = [];
  private $reportData = [];
  private $cliReport;
  private $webPageFile; 
  private $stateCount = [ 'OK' => 0 , 'UNKNOWN' => 0, 'CRITICAL' => 0, 'TOTAL' => 0];
  private $newEntriesForIni = [];
  private $defaultThreshold; 

  public function __construct($iniArray) 
  {
    $this->processOptions($iniArray);
    return true;
  }

  private function processOptions($iniArray)
  {
    $this->dbCredentialsIni = $iniArray['db_ini'];
    $this->thresholds = $iniArray['threshold'];
    $this->database = $iniArray['database'];
    $this->table = $iniArray['table'];
    $this->webPageFile = $iniArray['webPageFile'];
    $this->defaultThreshold = $iniArray['defaultThreshold'];
    return true;
  }

  public function determineStatus()
  {
    $this->dbData = $this->readDB();
    $this->thresholdsCleanedUp = $this->cleanupThresholdArray();
    $this->mergedThresholds = $this->mergeThresholdsWithDbData();
    $this->reportData = $this->generateStatusReportData();
    return true;
  }

  public function generateCLIreport()
  {
    $cliReport = '';
    foreach($this->reportData as $uniqKey => $rData)
    {
      if ($rData['emailReceived'] === TRUE) {
	if ($rData['overdue'] === TRUE) {
	  $cliReport .= "UNKOWN: Backup Email Overdue: Company: {$rData['data']['company']} Client: {$rData['data']['client']} Last Email: {$rData['data']['dbResults']['backupdate']}";
	} else {
	  if ($rData['data']['dbResults']['code'] == 1121) {
	    $cliReport .= "CRITCAL: Backup Failed: Company: {$rData['data']['company']} Client: {$rData['data']['client']} Code:{$rData['data']['dbResults']['code']} Last Email: {$rData['data']['dbResults']['backupdate']}";
	  } else {
	    $cliReport .= "OK: Backup Successful: Company: {$rData['data']['company']} Client: {$rData['data']['client']} Code:{$rData['data']['dbResults']['code']} Last Email: {$rData['data']['dbResults']['backupdate']}";
	  }
	}
      } else {
	$cliReport .= "UNKOWN: Email Never Received: Company: {$rData['data']['company']} Client: {$rData['data']['client']} ";
      }

      $cliReport .= "\n";
    }
    echo "$cliReport";
  }

  public function generateWebPage()
  {
    $webPageData = $this->generateWebPageData();
    $this->generateWebPageTable($webPageData); 
    return true;
  }

  private function generateWebPageTable($webPageData)
  {
    $table = "<table border=1>\n";
    $table .= "<tr><th> id </th> <th> Status </th> <th> Cause </th> <th> Company </th> <th> Backup Client </th> <th> Backup Code </th> <th> Last Email </th> <th> Threshold-Hours </th><th> Connect </th> </tr>\n";
    $rowArray = []; 
    foreach($webPageData as $state => $cause)
    {
      $bgcolor = $this->getRowColor($state);
      foreach ($cause as $causeName => $data)
      {
	foreach ($data as $dataProperties => $dp) 
	{
	  $rows = '';
	  $rows  .= "<tr bgcolor=$bgcolor>";
	  $rows  .= "<td>idreplace</td> ";
	  $rows  .= "<td align=center>$state</td> ";
	  $rows  .= "<td align=center>$causeName</td> ";
	  $rows  .= "<td align=center>{$dp['data']['company']}</td> ";
	  if (isset($dp['data']['notInIni']) && $dp['data']['notInIni'] == TRUE) {
	    $rows  .= "<td align=center>{$dp['data']['client']} (not in ini)</td> ";
	  } else {
	    $rows  .= "<td align=center>{$dp['data']['client']}</td> ";
	  }
	  if (isset($dp['data']['dbResults']['code'])) {
		  $rows  .= "<td align=center>{$dp['data']['dbResults']['code']}</td> ";
	  } else {
		  $rows  .= '<td>unknown </td>';
	  }
	  if (isset($dp['data']['dbResults']['backupdate'])) {
		  $rows  .= "<td>{$dp['data']['dbResults']['backupdate']}</td> ";
	  } else {
		  $rows  .= '<td> unknown </td>';
	  }
	  $rows  .= "<td align=center>{$dp['data']['hour']}</td> ";
	  if (!empty($dp['data']['url']))
	  {
		    $rows  .= "<td align=center><a href='{$dp['data']['url']}' target='_blank'> Connect </a></td> ";
	  } else {
		    $rows  .= "<td align=center></td> ";
	  }
	  $rows .= "</tr>\n";
	  $sortOrder = $this->sortOrder($state);
	  $this->incrementStateCount($state);
	  $rowsArray[$sortOrder][] = $rows;
	}
      }
    }
    sort($rowsArray);
    $id = 1;
    foreach ($rowsArray as $order => $orderNumber) {
      foreach ($orderNumber as $tableRow) {
	$table .= str_replace('idreplace',$id,$tableRow);
	$id++;
      }
    }
    $table .= "</table>";
    $webPage = '';
    $webPage .= "<html> <head> <title> NLS Backups </title> </head><body>\n";
    $currentTimestamp = new DateTime();
    $currentTimestamp->setTimezone(new DateTimeZone('US/Eastern'));
    $webPage .= "This page was last updated at " . $currentTimestamp->format("Y-m-d H:i:s") . " Eastern Time <br>";
    $dashboard = $this->generateDashBoardStateCounts();
    $webPage .= $dashboard;
    $webPage .= $table;
    $webPage .= "</body></html>\n";
    file_put_contents($this->webPageFile, $webPage);
    return true; 
  }

  private function getRowColor($state) {
    $colors = [
      'UNKNOWN' => 'ORANGE',
      'CRITICAL' => 'E64A34',
      'OK' => 'WHITE',
      'TOTAL' => 'WHITE'
      ];
      return $colors[$state];
  }

  private function sortOrder($state) {
    $order = [
      'UNKNOWN' => 1,
      'CRITICAL' => 2,
      'OK' => 3
      ];
      return $order[$state];
  }

  private function incrementStateCount($state) {
    $this->stateCount['TOTAL'] = $this->stateCount['TOTAL'] + 1;
    $this->stateCount[$state] = $this->stateCount[$state] + 1;
    return true;
  }

  private function generateDashBoardStateCounts()
  {
    $table = "<table border=1>";
    $row = "<tr>";
    foreach ($this->stateCount as $state => $count) {
      $bgcolor = $this->getRowColor($state);
      $row .= "<td bgcolor=$bgcolor> $state </td>";
    }
      $row .= "</tr>";
    foreach ($this->stateCount as $state => $count) {
      $bgcolor = $this->getRowColor($state);
      $row .= "<td bgcolor=$bgcolor align=center> $count </td>";
    }
      $row .= "</tr>";
      $table .= $row;
      $table .= "</table>";
      return $table; 
  }

  private function generateWebPageData()
  {
    $webPageData = [];
    foreach($this->reportData as $uniqKey => $rData)
    {
      if ($rData['emailReceived'] === TRUE) {
	if ($rData['overdue'] === TRUE) {
	  $webPageData['UNKNOWN']['overdue'][] = $rData;
	} else {
	  if ($rData['data']['dbResults']['code'] == 1121) {
	    $webPageData['CRITICAL']['failed'][] = $rData;
	  } else {
	    $webPageData['OK']['successful'][] = $rData;
	  }
	}
      } else {
	$webPageData['UNKNOWN']['missing'][] = $rData;
      }
    }
    return $webPageData;
  }



  private function generateStatusReportData()
  {
    $report = [];
    foreach ($this->mergedThresholds as $backupJob => $thresh) 
    {
      $key = base64_encode($thresh['client'] . '-' . $thresh['server'] . '-' . $thresh['company']);
      $report[$key]['data'] = $thresh;
      $thresholdTimestamp = $this->calculateThresholdDate($thresh['hour']);
      if (!isset($thresh['dbResults'])){
	$report[$key]['emailReceived'] = FALSE;
      } else {
	$report[$key]['emailReceived'] = TRUE;
      }

      if (isset($thresh['dbResults']))
      {
	if ($thresh['dbResults']['backupdate'] < $thresholdTimestamp->format("Y-m-d H:i:s")) {
	  $report[$key]['overdue'] = TRUE;
	} else {
	  $report[$key]['overdue'] = FALSE;
	}
      }
    }
    
    return $report;
  }

  private function calculateThresholdDate($hours) {
    $currentTimestamp = new DateTime();
    $currentTimestamp->setTimezone(new DateTimeZone('US/Eastern'));
    $currentTimestamp->sub(new DateInterval("PT{$hours}H"));
    return $currentTimestamp;
  }

  private function mergeThresholdsWithDbData()
  {
    $dataFromDB = $this->dbData;
    foreach ($this->thresholdsCleanedUp as $key => $thresholds)
    {
      foreach ($dataFromDB as $row => $dbData) 
      {
	if ($thresholds['client'] == $dbData['client'] && $thresholds['server'] == $dbData['server'] && $thresholds['company'] == $dbData['company']) {
	  $this->thresholdsCleanedUp[$key]['dbResults'] = $dbData;
	  unset($dataFromDB[$row]);
	}
      }
    }
    $this->newEntriesForIni = $dataFromDB;
    $mergedThresholds  =  $this->processNewBackupJobs($this->thresholdsCleanedUp,$this->newEntriesForIni,$this->defaultThreshold);
    return $mergedThresholds;
  }

  private function processNewBackupJobs($thresholdCleanUp,$newEntries,$threshold)
  {
  foreach ($newEntries as $row => $dbData)
    {
      $newEntry = [];
      $newEntry['client'] = $dbData['client'];
      $newEntry['server'] = $dbData['server'];
      $newEntry['company'] = $dbData['company'];
      $newEntry['hour'] = $threshold;
      $newEntry['notInIni'] = TRUE;
      $newEntry['dbResults'] = $dbData;
      $thresholdCleanUp[] = $newEntry;
    }
    return $thresholdCleanUp;
  }

  private function readDB()
  {
    $dbData = [];
    $this->connectToDB();
    $query = "SELECT * from {$this->database}.{$this->table} where code <> ''";
    $results = $this->dbHandle->query($query,PDO::FETCH_ASSOC);
    foreach ($results as $row => $values) {
      $dbData[] = $values;
    }
    return $dbData;
  }

  private function cleanupThresholdArray()
  {
    $thresholdsCleaned = [];
    foreach ($this->thresholds as $threshold) {
      LIST($client,$server,$company,$hour,$url) = explode("|",$threshold);
	$thresholdsCleaned[] = [ 
	  'client' => trim($client),
	  'server' => trim($server),
	  'company' => trim($company),
	  'hour' => trim($hour),
	  'url' => trim($url)
	  ];
    }
    return $thresholdsCleaned;
  }

  private function connectToDB()
  {
    // Open connection
    $dbCredentials = parse_ini_file($this->dbCredentialsIni);
    try 
    {
	    $pdo = new PDO('mysql:host=localhost;dbname=backups', $dbCredentials['user'], $dbCredentials['password']);

    }
    catch (PDOException $e) 
    {
	echo 'Error: ' . $e->getMessage();
	exit();
    }
    $this->dbHandle = $pdo;
    return true;
  }


}

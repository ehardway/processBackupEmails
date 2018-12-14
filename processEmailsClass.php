<?php

class processEmails
{

  private $emailDirectory = '/tmp/email_messages';
  private $dbCredentialsIni;
  private $emailFileNames = [];
  private $emailContents = [];
  private $emailParsedData = [];
  private $dbHandle;
  private $database;
  private $table;

  public function __construct($iniArray) 
  {
    $this->processOptions($iniArray);
    return true;
  }

  private function processOptions($iniArray)
  {
    $this->dbCredentialsIni = $iniArray['db_ini'];
    $this->database = $iniArray['database'];
    $this->table = $iniArray['table'];
    return true;
  }

  public function setEmailFileNames() 
  {
    $cmd = "ls -1d {$this->emailDirectory}/*";
    system($cmd,$retval);
    if ($retval == 2) {
      return false;
    }
    $emails =  explode("\n",`$cmd`);
    array_pop($emails);
    $this->emailFileNames = $emails;
    return true;
  }

  public function readEmails() {
  $emailContents = [];
  foreach ($this->emailFileNames as $fileName) {
    $emailContents[$fileName] =  file_get_contents($fileName);
    $this->deleteEmailFiles($fileName);
  }
  $this->emailContents = $emailContents;
  return true;
  }

  private function deleteEmailFiles($file)
  {
    system("rm -vf $file");
    return true;
  }

  public function parseEmails() {
    foreach ($this->emailContents as $fileName => $emailData)
    {
      $this->parseEmailData($emailData);
    }
    return true;
  }

  private function parseEmailData($emailData) {
    $emailDataExploded = [];
    $emailDataExploded = explode("\n",$emailData);
    $emailParsedData = []; 
    foreach($emailDataExploded as $lineNumber => $lineData) 
    {
	if (preg_match("/^Subject:/",$lineData)) {
	  $nextLine = $lineNumber + 1;
	  $emailParsedData['subject'] =  $emailDataExploded[$lineNumber] . $emailDataExploded[$nextLine];
	}
	if (preg_match("/^Date:/",$lineData)) {
	  $nextLine = $lineNumber + 1;
	  $emailParsedData['date'] =  $emailDataExploded[$lineNumber] . $emailDataExploded[$nextLine];
	}
    }
    $this->emailParsedData[] = $emailParsedData;
    return true;
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

  public function updateDatabase()
  {
    $this->connectToDB();
    foreach ($this->emailParsedData as $arrayNumber => $parsedArray) 
    {
      $parsedSubject = $this->parseSubject($parsedArray['subject']);
      $parsedDate = $this->parseDate($parsedArray['date']);
      $stmt = $this->generateReplaceStatements($parsedSubject,$parsedDate);
      try 
      {
	$this->dbHandle->exec($stmt);
      }
      catch (PDOException $e) 
      {
	  echo 'Error: ' . $e->getMessage();
      }
    }
    return true;
  }

  private function generateReplaceStatements($parsedSubject,$parsedDate) {

    $date = $parsedDate->format('Y-m-d H:i:s');
    $replaceStatement = "REPLACE INTO {$this->database}.{$this->table} ";
    $replaceStatement .= "(client,server,company,code,backupdate,date_modified) VALUES ";
    $replaceStatement .= "(" . $this->dbHandle->quote($parsedSubject['client']) . "," ;
    $replaceStatement .= $this->dbHandle->quote($parsedSubject['server']) . "," ;
    $replaceStatement .= $this->dbHandle->quote($parsedSubject['company']) . "," ;
    $replaceStatement .= $this->dbHandle->quote($parsedSubject['code']) . "," ;
    $replaceStatement .= "'$date',NOW())";
    return $replaceStatement;
  }

  private function parseSubject($subject)
  {
    $subject = preg_replace("/^Subject:/",'',$subject);
    LIST($client,$server,$company,$skip1,$skip2,$code) = explode("|",$subject);
    $code = preg_replace("/[^0-9]/",'',$code);
    $parsedSubject = ['client' => trim($client), 'server' => trim($server), 'company' => trim($company), 'code' => trim($code)];
    return $parsedSubject;
  }

  private function parseDate($date) 
  {
    preg_match('/\s\d+\s[A-Z,a-z]{3,3}\s[0-9]{4,4}\s[0-9]{2,2}:[0-9]{2,2}:[0-9]{2,2}/', $date, $matches, PREG_OFFSET_CAPTURE);
    LIST($day,$month,$year,$time) = explode(' ',trim($matches[0][0]));
    $month = $this->convertMonthToNumber($month);
    $dateProcessed = "$year-$month-$day $time";
    $dt = new DateTime($dateProcessed);
    $dt->setTimezone(new DateTimeZone('US/Eastern'));
    return $dt;
  }

  private function convertMonthToNumber($month)
  {
    $months = [
    'Dec' => 12,
    'Nov' => 11,
    'Oct' => 10,
    'Sep' => 9,
    'Aug' => 8,
    'Jul' => 7,
    'Jun' => 6,
    'May' => 5,
    'Apr' => 4,
    'Mar' => 3,
    'Feb' => 2,
    'Jan' => 1
    ];

    return $months[$month];
  }

}

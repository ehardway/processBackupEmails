#!/usr/bin/php
<?php

$currentDate = new DateTime();

$time_start = $currentDate->format('Y-m-d-H.i.s') . '.' .  microtime_float();

$file = fopen("/tmp/email_messages/email_{$time_start}.txt", "a");
fwrite($file, "Script successfully ran at ".date("Y-m-d H:i:s")."\n");

$fd = fopen("php://stdin", "r");
$email = "";
while (!feof($fd)) {
  $line = fread($fd, 1024);
  $email .= $line;
  }
fclose($fd);

fwrite($file, $email);
fclose($file);

function microtime_float()
{
  list($usec, $sec) = explode(" ", microtime());
  return ((float)$usec + (float)$sec);
}

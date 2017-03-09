<?php
  // proksi arg curl: --proxy http://167.205.22.102:8080


  $ret = shell_exec("curl --proxy http://167.205.22.102:8080 http://www.snopes.com/category/facts/");
  $url_pattern = '/^(http|https|ftp):\/\/([A-Z0-9][A-Z0-9_-]*(?:\.[A-Z0-9][A-Z0-9_-]*)+):?(\d+)?\/?/i';
  $matches = [];

  preg_match_all('/<a href="(.*)">/',$ret,$a);

  $count = count($a[1]);
  echo "Number of Urls = " .$count."\n";
  $links = [];
  for ($row = 0; $row < $count ; $row++) {
    $str = $a[1]["$row"];
    $pos = strpos($str, "\"");
    if ($pos) {
      $str = substr($str, 0, $pos);
    }

    $ok = false;
    for ($i = 0; $i < strlen($str); $i++) {
      if ($str[$i] == '-') {
        $ok = true;
      }
    }
    if (strpos($str, "itemprop")
    || strpos($str, "target=\"_blank\"")
    || strpos($str, "www.snopes.com/contact/")
    || strpos($str, "www.snopes.com/category/facts/")) {
      $ok = false;
    }

    $pos = strpos($str, "http");
    //echo "lala ".$pos."\n";
    if (strpos($str, "http") !== 0) {
      $ok = false;
    }

    if ($ok) {
      array_push($links, $str);
    }
  }
  $links = array_values(array_unique($links));
  echo "Valid url = ".sizeof($links)."\n";
  for ($i = 0; $i < sizeof($links); $i++) {
    echo $links[$i]."\n";
  }
?>

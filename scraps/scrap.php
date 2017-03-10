<?php
  // proksi arg curl: --proxy http://167.205.22.102:8080

function extractString($string, $start, $end) {
    $string = " ".$string;
    $ini = strpos($string, $start);
    if ($ini == 0) return "";
    $ini += strlen($start);
    $len = strpos($string, $end, $ini) - $ini;
    return substr($string, $ini, $len);
}

function strip_tags_content($text) {

    return preg_replace('@<(\w+)\b.*?>.*?</\1>@si', '', $text);

 }

  for ($page = 1; $page <= 3; $page++) {
    $url = "curl http://www.snopes.com/category/facts";
    if ($page != 1) {
      $url = $url."/page/".$page;
    }
    //echo $url."\n";

    $ret = shell_exec($url);
    $url_pattern = '/^(http|https|ftp):\/\/([A-Z0-9][A-Z0-9_-]*(?:\.[A-Z0-9][A-Z0-9_-]*)+):?(\d+)?\/?/i';
    $matches = [];

    preg_match_all('/<a href="(.*)">/',$ret,$a);

    $count = count($a[1]);
    //echo "Number of Urls = " .$count."\n";
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
      || strpos($str, "www.snopes.com/category/facts/")
      || strpos($str, "www.snopes.com/whats-new/")
      || strpos($str, "www.snopes.com/50-hottest-urban-legends/")
      || strpos($str, "www.snopes.com/about-snopes/")
      || strpos($str, "www.snopes.com/frequently-asked-questions/")) {
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
    //echo "Valid url = ".sizeof($links)."\n";
    for ($i = 0; $i < sizeof($links); $i++) {
      //echo $links[$i]."\n";
      $buffer = shell_exec("curl ".$links[$i]);
      $claim = extractString($buffer, "<p itemprop=\"claimReviewed\">", "</p>");
      $rating = trim(extractString($buffer, "<span itemProp=\"alternateName\">", "</span>"));

      $claim = trim(strip_tags_content($claim));
      $claim = str_replace("\"", "\"\"", $claim);
      echo "\"".$claim."\";".$rating."\n";
    }

  }
?>

<?php
include("wordfilter.php");

//support text with html tags
$text = "duh-p3n1s <i>b</i>abi kebab i k4mpr3t halo&nbsp;the Pen is mightier penisilin <b>p e ni&nbsp;s</b> dan <a href='/kampret'>lainnya</a> a.s.s-h-o-l-e kampret ass classic kucing andhjieng si b r e n g s e k d a n v i r g i n";

$result = wordFilter($text);

echo $text . "\n\n";
echo $result;

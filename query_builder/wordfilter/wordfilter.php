<?php
/*
Filter bad words in Indonesian text
elfan@live.com
*/

function wordFilter($text, $lang="id") {
	//ignore and preserve html tags
	//aware of white space and invisible markups (e.g. "&nbsp;", "&shy;")
	//aware of "p e n i s", "<b>p</b>enis", and "penisilin"
	//aware of "45sh0le" as "asshole"


	//$text = preg_replace("/&#(?:[0-9]+|[a-z][a-f0-9]+);?/i", "", $text);  //strip out any code similar to "&#378;" or "&#x8fc2;"

	$pattern = array(
			"<\/?\w+(?:\s*\w+\s*=\s*(?:'[^']*'|\"[^\"]*\"|[^>]*)|[^>]+?)*\s*>" => "",
			"&shy;?" => "",
			"&nbsp;?" => " ",
	);
	$regex = "";
	foreach ($pattern as $pat=>$rep) {
		if ($regex) $regex .= "|";
		$regex .= ($rep==="" ? "(?:".$pat.")+" : $pat);
	}
	$regex = "/(?:".$regex.")/is";
	preg_match_all($regex, $text, $match, PREG_OFFSET_CAPTURE);
	
	$cleantext = "";

	$captures = $match[0];
	if ($captures) {
		//normalize
		$shorttext = "";
		for ($i=0; $i<count($captures); $i++) {
			$capture = $captures[$i];
			if ($i==0) {
				$shorttext .= substr($text, 0, $capture[1]);
			}

			foreach ($pattern as $pat=>$rep) {
				if ($rep!="") {
					if (preg_match("/^".$pat."$/is", $capture[0])) {
						$shorttext .= $rep;
						$captures[$i][2] = strlen($rep);
						$captures[$i][3] = $rep;
						break;
					}
				}
			}

			$offset = $capture[1] + strlen($capture[0]);
			$length = (($i < count($captures)-1) ? $captures[$i+1][1] : strlen($text)) - $offset;
			$shorttext .= substr($text, $offset, $length);
		}

		//clean
		$cleantext = replaceBadWords($shorttext, $lang);

		//restore
		$longtext = "";
		$offset = 0;
		for ($i=0; $i<count($captures); $i++) {
			$capture = $captures[$i];
			if ($i==0) {
				$longtext .= substr($cleantext, 0, $capture[1]);
				$offset += $capture[1];
			}

			if (@$capture[2]) {	//visible markup
				$reptext = substr($cleantext, $offset, $capture[2]);
				if ($reptext == $capture[3]) {	//unchanged
					$longtext .= $capture[0];
				}
				else {
					$longtext .= $reptext;	//changed
				}
				$offset += $capture[2];
			}
			else {	//invisible markup
				$longtext .= $capture[0];
			}


			$length = (($i < count($captures)-1) ? ($captures[$i+1][1] - $capture[1] - strlen($capture[0])) : (strlen($cleantext) - $offset + 1));

			$longtext .= substr($cleantext, $offset, $length);
			$offset += $length;
		}
		$cleantext = $longtext;
	}
	else {
		$cleantext = replaceBadWords($text, $lang);
	}
	$cleantext = preg_replace("/\*{8,}/s", "*********", $cleantext);
	return $cleantext;
}


function replaceBadWords($text, $lang="id") {
	$file = dirname(__FILE__)."/".$lang.".txt";
	$filere = dirname(__FILE__)."/".$lang.".re.txt";
	$result = "";
	$badlist = array();
	if (file_exists($filere) && (filemtime($filere) > @filemtime($file)) && (filemtime($filere) > filemtime(__FILE__))) { //already have cached regex pattern
		$regex = file_get_contents($filere);
	}
	else if (file_exists($file)) {  //regex cache file is outdated, rebuild a new one
		if ($f = fopen($file, "r")) {
			while (!feof($f)) {
				$line = trim(fgets($f, 1000000));
				if ($line) array_splice($badlist, count($badlist), 0, explode(",", $line));
			}
			fclose($f);

			$regex = "";
			foreach ($badlist as $bad) {
				if ($regex!="") $regex .= "|";
				if (strpos($bad, "/") === 0) {
					$pat = substr($bad, 1, strlen($bad)-2);
        }
        else {
          $pat = implode("", array_map(function($c) {
            $map = ['a'=>'[a4]', 'i'=>'[i1]', 'e'=>'[e3]', 'o'=>'[o0]', 'k'=>'[kq]', 's'=>'[s5z]'];
            return str_replace(array_keys($map), array_values($map), $c) . '+';
          }, str_split($bad)));
        }
	  		$spat = preg_replace("/([\+\*])/s", "\\1\W*", $pat);
				$regex .= $spat;
			}

			if ($f = fopen($filere, "w")) {
				fwrite($f, $regex);
				fclose($f);
			}

		}
	}

	if ($regex) {
		$regex = "/\b((?:".$regex.")+)\b/sie";
		$result = preg_replace($regex, 'str_repeat("*", strlen("\\1"))', $text);
	}
	return $result;
}

?>

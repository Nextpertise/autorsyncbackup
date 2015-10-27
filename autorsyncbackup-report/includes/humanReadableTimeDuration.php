<?php
/*
 * Convert seconds to human readable text.
 * Found at: http://csl.sublevel3.org/php-secs-to-human-text/
 * @see: https://gist.github.com/erickpatrick/3039081
 *
 * @param $secs
 * @return string
 */
function humanReadableTimeDuration($secs)
{
	$units = array(
		"week"   => 7*24*3600,
		"day"    =>   24*3600,
		"hour"   =>      3600,
		"minute" =>        60,
		"second" =>         1,
	);

	// specifically handle zero
	if ( $secs == 0 ) return "0 seconds";

	$s = "";

	foreach ( $units as $name => $divisor ) {
		if ( $quot = intval($secs / $divisor) ) {
			$s .= "$quot $name";
			$s .= (abs($quot) > 1 ? "s" : "") . ", ";
			$secs -= $quot * $divisor;
		}
	}

	return substr($s, 0, -2);
}

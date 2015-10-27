<?php
/**
 * @author Jeffrey Sambells
 * @see http://jeffreysambells.com/2012/10/25/human-readable-filesize-php
 * @param $bytes
 * @param int $decimals
 * @return string
 */
function humanReadableFileSize($bytes, $decimals = 2) {
	$size = array('B','kB','MB','GB','TB','PB','EB','ZB','YB');
	$factor = floor((strlen($bytes) - 1) / 3);

	return sprintf("%.{$decimals}f", $bytes / pow(1024, $factor)) . ' ' . (isset($size[$factor]) ? $size[$factor] : '');
}

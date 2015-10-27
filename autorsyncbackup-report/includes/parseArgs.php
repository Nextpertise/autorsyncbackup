<?php

/**
 * @param array $arguments
 * @return array
 */
function parseArgs(Array $arguments)
{
	$parsedArgs = array();

	foreach ($arguments as $i => $argumentValue) {
		if ($i == 0) {
			continue;
		}

		$argExp = explode('=', $argumentValue);

		if (count($argExp) > 1) {
			$parsedArgs[$argExp[0]] = $argExp[1];
		} else {
			$parsedArgs[$argumentValue] = null;
		}
	}

	return $parsedArgs;
}

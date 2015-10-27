<?php

// Fow now, only CLI calls are allowed
if (php_sapi_name() !== 'cli') {
    echo 'This method can only be called from the cli.';
    exit(1);
}

try {
    /**
     * Load classes and other includes for logging and settings, those are needed first.
     * Later on we'll load the rest of the files in the classes/ directory
     */
    require_once 'classes/CliOutput.php';
    require_once 'classes/Loggable.php';
    require_once 'classes/GlobalSettings.php';
    $globalSettings = GlobalSettings::instance();
    $globalSettings->verboseMode = true;
    $globalSettings->verboseLevel = 'info';
    $loggable =  Loggable::instance();
    $cliOutput = CliOutput::instance();

    // Debug mode
    if ($globalSettings->phpdebug) {
        $loggable->logEvent('PHP Debug mode on, displaying all PHP errors', NXTHD_LOG_DEBUG);

        ini_set('display_errors', 1);
        error_reporting(E_ALL);
    } else {
        $loggable->logEvent('PHP Debug mode off, suppressing all PHP errors', NXTHD_LOG_DEBUG);

        ini_set('display_errors', 0);
        error_reporting(0);
    }

    /**
     * @param string $dirname
     */
    function includeFilesFromDir($dirname) {
        if (substr($dirname, -1) == '/') {
            $dirname = substr($dirname, -1);
        }

        if (!file_exists($dirname)) {
            Loggable::instance()->logEvent('Cannot include files from dir ' . $dirname, NXTHD_LOG_ERR);
            exit(1);
        }

        foreach (glob($dirname . '/*.php') as $filename) {
            Loggable::instance()->logEvent('Loading file ' . $filename . ' from ' . __FILE__, NXTHD_LOG_DEBUG);
            require_once $filename;
        }
    }

    // Require the includes folder
    includeFilesFromDir('includes');
    includeFilesFromDir('classes');

    // Grab timezone from config. If not available: use default
    $timezone = (isset($globalSettings->timezone) && $globalSettings->timezone !== false ?
        GlobalSettings::instance()->timezone :
        'Europe/Amsterdam');
    $loggable->logEvent('Setting ' . $timezone . ' as timezone', NXTHD_LOG_DEBUG);
    date_default_timezone_set($timezone);

    // Parse CLI arguments and set verbose info
    $cliOutput = CliOutput::instance();
    $cliOutput->msg('User ' . get_current_user() . ' started autorsyncbackup-report @ ' . date('Y-m-d H:i:s'));

    $globalSettings->parsedCliArgs = parseArgs($argv);
    if (array_key_exists('-v', $globalSettings->parsedCliArgs)) {
        if (!is_null($globalSettings->parsedCliArgs['-v'])) {
            switch ($globalSettings->parsedCliArgs['-v']) {
                case 'i':
                    $globalSettings->verboseLevel = 'info';
                    break;

                case 'd':
                    $globalSettings->verboseLevel = 'debug';
                    break;

                case 'w':
                    $globalSettings->verboseLevel = 'warning';
                    break;

                case 'e':
                    $globalSettings->verboseLevel = 'error';
                    break;

                default:
                    echo 'Unknown verbose level ' . $globalSettings->parsedCliArgs['-v'];
                    exit(1);
            }
        }
        $settingsArray['verboseMode'] = true;
        $loggable->logEvent('Verbose mode on');
        $loggable->logEvent('Set verbose level to ' . $globalSettings->verboseLevel);
    }

    // Require Smarty
    require 'vendor/smarty/smarty/libs/Smarty.class.php';
    $loggable->logEvent('Loaded Smarty', NXTHD_LOG_DEBUG);

    foreach ($globalSettings->getSettingsArray() as $key => $value) {
        $logStr = 'Found and set config key ' . $key;

        if (is_string($value) || is_int($value)) {
            $logStr .= ' with string or integer value ' .  $value;
        } else {
            $logStr .= ' with ' . gettype($value);
        }

        $loggable->logEvent($logStr, NXTHD_LOG_DEBUG);
    }

    $controller = new AutorsyncbackupController($globalSettings->parsedCliArgs);
    // Parse Singe logFile
    if (isset($globalSettings->parsedCliArgs['-sf'])) {
        $loggable->logEvent('Found -sf parameter, so parsing single log file.');

        $controller->parseSingeLogFileAction($globalSettings->parsedCliArgs['-sf']);
    } else {
        $controller->parseLogAction();
    }

    // Recap of result of execution of this script
    $errorCount = count($cliOutput->errorMessages);
    $warningCount = count($cliOutput->warningMessages);
    if ($errorCount > 0) {
        $loggable->logEvent('Script finished with ' . $errorCount . ' error(s) and ' . $warningCount .
            ' warnings @ ' . date('Y-m-d H:i:s'), NXTHD_LOG_ERR);
    } elseif ($warningCount > 0) {
        $loggable->logEvent('Script finished with 0 errors and ' . $warningCount . ' warning(s) @ ' .
            date('Y-m-d H:i:s'), NXTHD_LOG_WARN);
    } else {
        $loggable->logEvent('Script finished with 0 errors and 0 warnings @ ' . date('Y-m-d H:i:s'), NXTHD_LOG_SUCCESS);
    }
    echo PHP_EOL;

}

catch (\Exception $e) {
    echo $e->getMessage() . PHP_EOL;
    exit(1);
}
<?php

/**
 * Class CliOutput
 */
class CliOutput
{
	/**
     * @var mixed
     */
    protected $initMicrotime;

	/**
     * Several message types
     *
     * @var array
     */
    public   $infoMessages       = array(),
                $debugMessages      = array(),
                $warningMessages    = array(),
                $errorMessages      = array(),
                $successMessages    = array();

	/**
     * Private constructor for Singleto
     */
    private function __construct()
    {
        $this->initMicrotime = microtime(true);
    }

    /**
     * Call this method to get singleton
     *
     * @return CliOutput
     **/
    public static function instance()
    {
        static $inst = null;
        if ($inst === null) {
            $inst = new CliOutput();
        }
        return $inst;
    }

	/**
     * @param $name
     * @return bool|mixed
     */
    public function __get($name)
    {
        $methodName = 'get' . ucfirst($name);

        if (method_exists($this, $methodName)) {
            return call_user_func(array($this, $methodName));
        }

        return false;
    }

	/**
     * @return array
     */
    public function getInfoMessages()
    {
        return $this->infoMessages;
    }

	/**
     * @return array
     */
    public function getDebugMessages()
    {
        return $this->debugMessages;
    }

	/**
     * @return array
     */
    public function getWarningMessages()
    {
        return $this->warningMessages;
    }

	/**
     * @return array
     */
    public function getErrorMessages()
    {
        return $this->errorMessages;
    }

    /**
     * @param string $text
     * @param string $status
     * @return string
     * @throws Exception
     *
     * @author Mario Awad
     * @see http://softkube.com/blog/generating-command-line-colors-with-php
     */
    public static function colorize($text, $status) {
        switch($status) {
            case "SUCCESS":
                $out = "[30;42m"; //Green background
                break;
            case "FAILURE":
                $out = "[41m"; //Red background
                break;
            case "WARNING":
                $out = "[43m"; //Yellow background
                break;
            case "NOTE":
                $out = "[44m"; //Blue background
                break;
            default:
                throw new Exception("Invalid status: " . $status);
        }
        return chr(27) . "$out" . "$text" . chr(27) . "[0m";
    }

    /**
     * @param string $msg
     * @param int $level
     * @param return void
     */
    public function msg($msg, $level = NXTHD_LOG_INFO) {
        $output = false;

        switch (GlobalSettings::instance()->verboseLevel) {
            case 'info':
                if ($level === NXTHD_LOG_INFO || $level == NXTHD_LOG_SUCCESS ||
                    $level === NXTHD_LOG_WARN || $level === NXTHD_LOG_ERR) {
                        $output = true;
                }
                break;

            case 'debug':
                $output = true;
                break;

            case 'success':
                if ($level == NXTHD_LOG_SUCCESS) {
                    $output = true;
                }
                break;

            case 'warning':
                if ($level === NXTHD_LOG_DEBUG || $level == NXTHD_LOG_SUCCESS) {
                    $output = false;
                }
                break;

            case 'error':
                if ($level === NXTHD_LOG_ERR || $level == NXTHD_LOG_SUCCESS) {
                    $output = true;
                }
                break;

            default:
                echo 'NXTHD warning : Unknown output verbose level, outputting everything' . PHP_EOL;
                $output = true;
        }

        if (!GlobalSettings::instance()->verboseMode) {
            $output = false;
        }

        if ($output) {
            switch ($level) {
                case NXTHD_LOG_INFO:
                    $this->infoMessages[] = $msg;

                    echo 'NXTHD info : ' . $msg . PHP_EOL;
                    break;

                case NXTHD_LOG_DEBUG:
                    $this->debugMessages[] = $msg;

                    echo 'NXTHD debug : ' . $msg . PHP_EOL;
                    break;

                case NXTHD_LOG_SUCCESS:
                    $this->successMessages[] = $msg;

                    echo self::colorize('NXTHD success : ' . $msg, 'SUCCESS') . PHP_EOL;
                    break;

                case NXTHD_LOG_WARN:
                    $this->warningMessages[] = $msg;

                    echo self::colorize('NXTHD warning : ' . $msg, 'WARNING') . PHP_EOL;
                    break;

                case NXTHD_LOG_ERR:
                    $this->errorMessages[] = $msg;

                    echo self::colorize('NXTHD error : ' . $msg, 'FAILURE') . PHP_EOL;
                    break;
            }
        }
    }
}

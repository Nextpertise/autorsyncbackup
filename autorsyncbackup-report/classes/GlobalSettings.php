<?php

/**
 * Class GlobalSettings
 *
 * @property string $verboseLevel
 * @property bool $verboseMode
 * @property string $timezone
 * @property string $title
 * @property string $spooldir
 * @property bool $phpdebug
 * @property string|int $maxBackupThresholdInHours
 * @property array $emailReportRecipients
 * @property array $emailReportCc
 * @property array $emailReportBcc
 * @property string $hostsToBackup
 * @property array $parsedCliArgs
 * @todo Stop using this class as a registry and create a separate class for it.
 */
class GlobalSettings
{
    private $settingsArray;

	/**
     * Class is singleton, so method is private, use static method instance.
     *
     * @throws Exception
     */
    private function __construct()
    {
        // Require Spyc (Yaml support)
        require_once 'vendor/mustangostang/spyc/Spyc.php';

        if (!file_exists('config.yaml') || !is_readable('config.yaml')) {
            throw new Exception('Cannot read config.yaml!');
        }

        $this->setSettingsArray( Spyc::YAMLLoad('config.yaml') );
    }

    /**
     * Call this method to get singleton
     *
     * @return GlobalSettings
     **/
    public static function instance()
    {
        static $inst = null;
        if ($inst === null) {
            $inst = new GlobalSettings();
        }
        return $inst;
    }

    public function __get($property) {
        if (array_key_exists($property, $this->getSettingsArray())) {
          return $this->settingsArray[$property];
        } else {
         return false;
        }
    }

    public function __set($property, $value) {
        $this->settingsArray[$property] = $value;
        return true;
    }

    // Getters & Setters
    public function getSettingsArray() {
      return $this->settingsArray;
    }

    private function setSettingsArray($settingsArray) {
      $this->settingsArray = $settingsArray;
    }
}

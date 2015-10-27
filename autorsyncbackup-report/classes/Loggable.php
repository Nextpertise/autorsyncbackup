<?php

define('NXTHD_LOG_INFO', 1);
define('NXTHD_LOG_DEBUG', 2);
define('NXTHD_LOG_SUCCESS', 3);
define('NXTHD_LOG_WARN', 4);
define('NXTHD_LOG_ERR', 5);

/**
 * Class Loggable
 */
class Loggable
{
	protected $logDirectory;

	/**
	 * Class is singleton, so method is private, use static method instance.
	 *
	 * @throws Exception
	 */
	private function __construct()
	{
		$this->logDirectory = GlobalSettings::instance()->logdir;

		if (!file_exists($this->logDirectory) || ! is_writable($this->logDirectory)) {
			throw new \Exception(sprintf('Cannot write to directory %s. Please make this directory writable.',
				$this->logDirectory));
		}
	}

	/**
	 * Call this method to get singleton
	 *
	 * @return Loggable
	 **/
	public static function instance()
	{
		static $inst = null;
		if ($inst === null) {
			$inst = new Loggable();
		}
		return $inst;
	}

	/**
	 * @param string $msg
	 * @param int $level
	 */
	public function logEvent($msg, $level = NXTHD_LOG_INFO)
	{
		$msg = date('Y-m-d H:i:s') . ' - ' . $msg;

		file_put_contents('log/' . date('Y-m-d') . '.log', $msg . PHP_EOL, FILE_APPEND);

		CliOutput::instance()->msg($msg, $level);
	}
}

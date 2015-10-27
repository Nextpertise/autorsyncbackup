<?php

/**
 * Class BackupLogModel
 */
class BackupLogModel
{
	protected $jobfile,
			$hostname,
			$username,
			$share,
			$destinationFolder,
			$speedLimitInKbs,
			$startTime,
			$startTimeStamp,
			$endTime,
			$endTimestamp,
			$fileset,
			$fileSetArray, // Generated on the fle
			$fileSetRotate,
			$fileSetRotateArray, // Generated on the fly
			$rsyncError, // Determined after calling rsyncOutputParsedAsArray
			$rsyncOutput,
			$rsyncOutputParsedAsArray, // Generated on the fly
			$rsyncReturnCode,
			$rsyncReturnCodeMessage, // Generated on the fly
			$autoRsyncBackupErrorCode,
			$autoRsyncBackupErrorMessage;

	/**
	 * Filled on construct
	 *
	 * @var
	 */
	protected $rsyncErrorCodesArray;

	/**
	 * Populates the rsyncErrorCodesArray
	 */
	public function __construct()
	{
		$this->rsyncErrorCodesArray = array(
			0 => 'Success',
			1 => 'Syntax or usage error',
			2 => 'Protocol incompatibility',
			3 => 'Errors selecting input/output files, dirs',
			4 => 'Requested action not supported: an attempt was made to manipulate 64-bit files on a platform that ' .
				'cannot support them; or an option was specified that is supported by the client and not by the server.',
			5 => 'Error starting client-server protocol',
			6 => 'Daemon unable to append to log-file',
			10 => 'Error in socket I/O',
			11 => 'Error in file I/O',
			12 => 'Error in rsync protocol data stream',
			13 => 'Errors with program diagnostics',
			14 => 'Error in IPC code',
			20 => 'Received SIGUSR1 or SIGINT',
			21 => 'Some error returned by waitpid()',
			22 => 'Error allocating core memory buffers',
			23 => 'Partial transfer due to error',
			24 => 'Partial transfer due to vanished source files',
			25 => 'The --max-delete limit stopped deletions',
			30 => 'Timeout in data send/receive',
			35 => 'Timeout waiting for daemon connection',
		);
	}

	/**
	 * @param string $method
	 * @param string $msg
	 * @param int $level
	 */
	private function logEvent($method, $msg, $level = NXTHD_LOG_INFO)
	{
		Loggable::instance()->logEvent(__CLASS__ . '::' . $method . '(): ' . $msg, $level);
	}

	/**
	 * @param $name
	 * @return bool|mixed
	 */
	public function __get($name)
	{
		$this->logEvent(__METHOD__, 'Executed', NXTHD_LOG_DEBUG);

		$methodName = 'get' . ucfirst($name);

		$this->logEvent(__METHOD__,
			'Getting key ' . $name . ' from method ' . $methodName . ' from class ' . __CLASS__, NXTHD_LOG_DEBUG);

		if (method_exists($this, $methodName)) {
			return call_user_func(array($this, $methodName));
		}

		$this->logEvent(__METHOD__, 'Cannot find method ' . __CLASS__ . '::' . $methodName, NXTHD_LOG_WARN);

		return false;
	}

	/**
	 * @param string $name
	 * @param mixed $value
	 */
	public function __set($name, $value)
	{
		$this->logEvent(__METHOD__, 'Executed', NXTHD_LOG_DEBUG);

		$methodName = 'set' . ucfirst($name);

		if (method_exists($methodName, $this)) {
			$this->logEvent(__METHOD__, 'Setting value ' . $value . ' for key ' . $name, NXTHD_LOG_DEBUG);

			$this->$methodName($value);
		} else {
			$this->logEvent(__METHOD__, 'Cannot set value ' . $value . ' for key ' . $name, NXTHD_LOG_ERR);

			throw new OutOfRangeException(sprintf('Not allowed to set value for property %s.', $name));
		}
	}

	/**
	 * @return string
	 */
	public function getJobfile()
	{
		$this->logEvent(__METHOD__, 'Executed', NXTHD_LOG_DEBUG);

		return $this->jobfile;
	}

	/**
	 * @param string $jobfile
	 * @return BackupLogModel
	 */
	public function setJobfile($jobfile)
	{
		$this->logEvent(__METHOD__, 'Executed', NXTHD_LOG_DEBUG);

		$this->jobfile = $jobfile;
		
		return $this;
	}

	/**
	 * @return mixed
	 */
	public function getHostname()
	{
		$this->logEvent(__METHOD__, 'Executed', NXTHD_LOG_DEBUG);

		if (!is_string($this->hostname)) {
			$this->logEvent(__METHOD__, 'Hostname is not string!'. NXTHD_LOG_WARN);
		} elseif (empty($this->hostname)) {
			$this->logEvent(__METHOD__, 'Hostname is empty!'. NXTHD_LOG_WARN);
		} elseif (strlen($this->hostname) <= 1) {
			$this->logEvent(__METHOD__, 'Hostname strlen < 1'. NXTHD_LOG_WARN);
		}

		return $this->hostname;
	}

	/**
	 * @param string $hostname
	 * @return BackupLogModel
	 */
	public function setHostname($hostname)
	{
		$this->logEvent(__METHOD__, 'Executed with param ' . $hostname, NXTHD_LOG_DEBUG);

		$this->hostname = $hostname;

		return $this;
	}

	/**
	 * @return mixed
	 */
	public function getUsername()
	{
		$this->logEvent(__METHOD__, 'Executed', NXTHD_LOG_DEBUG);

		return $this->username;
	}

	/**
	 * @param string $username
	 * @return BackupLogModel
	 */
	public function setUsername($username)
	{
		$this->logEvent(__METHOD__, 'Executed', NXTHD_LOG_DEBUG);

		$this->username = $username;

		return $this;
	}

	/**
	 * @return mixed
	 */
	public function getShare()
	{
		$this->logEvent(__METHOD__, 'Executed', NXTHD_LOG_DEBUG);

		return $this->share;
	}

	/**
	 * @param string $share
	 * @return BackupLogModel
	 */
	public function setShare($share)
	{
		$this->logEvent(__METHOD__, 'Executed', NXTHD_LOG_DEBUG);

		$this->share = $share;

		return $this;
	}

	/**
	 * @return mixed
	 */
	public function getDestinationFolder()
	{
		$this->logEvent(__METHOD__, 'Executed', NXTHD_LOG_DEBUG);

		return $this->destinationFolder;
	}

	/**
	 * @param string $destinationFolder
	 * @return BackupLogModel
	 */
	public function setDestinationFolder($destinationFolder)
	{
		$this->logEvent(__METHOD__, 'Executed', NXTHD_LOG_DEBUG);

		$this->destinationFolder = $destinationFolder;

		return $this;
	}

	/**
	 * @return mixed
	 */
	public function getSpeedLimitInKbs()
	{
		$this->logEvent(__METHOD__, 'Executed', NXTHD_LOG_DEBUG);

		return $this->speedLimitInKbs;
	}

	/**
	 * @param string $speedLimitInKbs
	 * @return BackupLogModel
	 */
	public function setSpeedLimitInKbs($speedLimitInKbs)
	{
		$this->logEvent(__METHOD__, 'Executed', NXTHD_LOG_DEBUG);

		$this->speedLimitInKbs = $speedLimitInKbs;

		return $this;
	}

	/**
	 * @return mixed
	 */
	public function getStartTime()
	{
		$this->logEvent(__METHOD__, 'Executed', NXTHD_LOG_DEBUG);

		return $this->startTime;
	}

	/**
	 * @param string $startTime
	 * @return BackupLogModel
	 */
	public function setStartTime($startTime)
	{
		$this->logEvent(__METHOD__, 'Executed', NXTHD_LOG_DEBUG);

		$this->startTime = $startTime;

		return $this;
	}

	/**
	 * @return mixed
	 */
	public function getStartTimeStamp()
	{
		$this->logEvent(__METHOD__, 'Executed', NXTHD_LOG_DEBUG);

		return $this->startTimeStamp;
	}

	/**
	 * @param string $startTimeStamp
	 * @return BackupLogModel
	 */
	public function setStartTimeStamp($startTimeStamp)
	{
		$this->logEvent(__METHOD__, 'Executed', NXTHD_LOG_DEBUG);

		$this->startTimeStamp = $startTimeStamp;

		return $this;
	}

	/**
	 * @return mixed
	 */
	public function getEndTime()
	{
		return $this->endTime;
	}

	/**
	 * @param string $endTime
	 * @return BackupLogModel
	 */
	public function setEndTime($endTime)
	{
		$this->logEvent(__METHOD__, 'Executed', NXTHD_LOG_DEBUG);

		$this->endTime = $endTime;

		return $this;
	}

	/**
	 * @return mixed
	 */
	public function getEndTimestamp()
	{
		$this->logEvent(__METHOD__, 'Executed', NXTHD_LOG_DEBUG);

		return $this->endTimestamp;
	}

	/**
	 * @param string $endTimestamp
	 * @return BackupLogModel
	 */
	public function setEndTimestamp($endTimestamp)
	{
		$this->logEvent(__METHOD__, 'Executed', NXTHD_LOG_DEBUG);

		$this->endTimestamp = $endTimestamp;

		return $this;
	}

	/**
	 * @return mixed
	 */
	public function getFileset()
	{
		$this->logEvent(__METHOD__, 'Executed', NXTHD_LOG_DEBUG);

		return $this->fileset;
	}

	/**
	 * @param string $fileset
	 * @return BackupLogModel
	 */
	public function setFileset($fileset)
	{
		$this->logEvent(__METHOD__, 'Executed', NXTHD_LOG_DEBUG);

		$this->fileset = $fileset;

		return $this;
	}

	/**
	 * @return array
	 */
	public function getFileSetArray()
	{
		$this->logEvent(__METHOD__, 'Executed', NXTHD_LOG_DEBUG);

		if (!is_array($this->fileSetArray)) {
			$this->fileSetArray = explode(':', $this->fileset);
		}

		return $this->fileSetArray;
	}

	/**
	 * @return mixed
	 */
	public function getFilesetRotate()
	{
		$this->logEvent(__METHOD__, 'Executed', NXTHD_LOG_DEBUG);

		return $this->fileSetRotate;
	}

	/**
	 * @param string $filesetRotate
	 * @return BackupLogModel
	 */
	public function setFilesetRotate($filesetRotate)
	{
		$this->logEvent(__METHOD__, 'Executed', NXTHD_LOG_DEBUG);

		$this->fileSetRotate = $filesetRotate;

		return $this;
	}

	public function getFileSetRotateArray()
	{
		$this->logEvent(__METHOD__, 'Executed', NXTHD_LOG_DEBUG);

		if (!is_array($this->fileSetRotateArray)) {
			$this->fileSetRotateArray = explode(PHP_EOL, $this->fileSetRotate);
		}

		return $this->fileSetRotateArray;
	}

	/**
	 * @return mixed
	 */
	public function getRsyncOutput()
	{
		$this->logEvent(__METHOD__, 'Executed', NXTHD_LOG_DEBUG);

		return $this->rsyncOutput;
	}

	/**
	 * @param string $rsyncOutput
	 * @return BackupLogModel
	 */
	public function setRsyncOutput($rsyncOutput)
	{
		$this->logEvent(__METHOD__, 'Executed', NXTHD_LOG_DEBUG);

		$this->rsyncOutput = $rsyncOutput;

		return $this;
	}

	public function getRsyncOutputParsedAsArray()
	{
		if (is_null($this->rsyncOutputParsedAsArray)) {
			$defaultMinimumRsyncOutputArray = array(
				'keyValuePairs' 					=> array(
					'Number of files' 				=> 0,
					'Number of files transferred'	=> 0,
					'Total file size' 				=> 0,
					'Total transferred file size' 	=> 0,
					'Literal data'				 	=> 0,
					'Matched data' 					=> 0,
					'File list size' 				=> 0,
					'File list generation time' 	=> 0,
					'File list transfer time' 		=> 0,
					'Total bytes sent' 				=> 0,
					'Total bytes received' 			=> 0
				),
				'rsyncErrors'		=> array(),
				'rsyncMessages' 	=> array(),
				'rsyncMissingFiles' => array(),
				'miscData'			=> array()
			);

			if ($this->rsyncOutput == 'Rsync was never invoked') {
				$this->rsyncOutputParsedAsArray = $defaultMinimumRsyncOutputArray;
				$this->rsyncOutputParsedAsArray['rsyncErrors'] = array($this->rsyncOutput);
			} elseif (strtolower(substr($this->rsyncOutput, 0, 6)) == '@error') {
				$this->rsyncOutputParsedAsArray = $defaultMinimumRsyncOutputArray;
				$this->rsyncOutputParsedAsArray['rsyncErrors'] = array($this->rsyncOutput);
			} else {
				$rsyncOutputRows = explode(PHP_EOL, $this->rsyncOutput);

				$this->rsyncOutputParsedAsArray['keyValuePairs'] 		= array();
				$this->rsyncOutputParsedAsArray['rsyncErrors']   		= array();
				$this->rsyncOutputParsedAsArray['rsyncMessages'] 		= array();
				$this->rsyncOutputParsedAsArray['rsyncMissingFiles']	= array();
				$this->rsyncOutputParsedAsArray['miscData']	     		= array();

				foreach($rsyncOutputRows as $row) {

					$this->logEvent(__METHOD__, 'Read row from rsync output: ' . $row, NXTHD_LOG_DEBUG);

					$row = trim($row);
					if (substr($row, 0, 5) == 'rsync') {
						if (substr($row, 5, 2) == ': ') {
							$rsyncMessage = trim(substr($row, 7));
						} else {
							$rsyncMessage = trim(substr($row, 5));
						}

						$this->logEvent(__METHOD__, 'Rsync message: ' . $rsyncMessage, NXTHD_LOG_DEBUG);

						if (preg_match('/^error: (.*?)+$/i', $rsyncMessage)) {
							$this->rsyncOutputParsedAsArray['rsyncErrors'][] = $rsyncMessage;
						// Missing files
						} elseif (preg_match('/^link_stat "(.*?)" (.*?) ' . preg_quote('(2)') . '+$/i', $rsyncMessage)) {
							// Todo: find out if and how this regexp can be improved
							preg_match_all('/^link_stat "(.*?)" (.*?) ' . preg_quote('(2)') . '+$/i', $rsyncMessage, $missingFileLocationMatches);
							$this->rsyncOutputParsedAsArray['rsyncMissingFiles'][] = $missingFileLocationMatches[1][0];
						} else {
							$this->rsyncOutputParsedAsArray['rsyncMessages'][] = $rsyncMessage;
						}
					} elseif (preg_match('/^IO error encountered/i', $row)) {
						$this->rsyncOutputParsedAsArray['rsyncErrors'][] = $row;
					} elseif (preg_match('/^sent [0-9]{1,32} bytes[\s]{1,32}received [0-9]{1,32} bytes[\s]{1,8}[0-9.]{1,32} bytes\/sec+$/i', $row) ||
							  preg_match('/^total size is [0-9]{1,32}[\s]{1,8}speedup is [0-9.]{1,32}+$/i', $row)) {
						// Ignoring since we should already know that.
						// TODO: Teun let me what do you think?
					} elseif (preg_match('/file has vanished: "(.*?)"/i', $row)) {
						preg_match('/file has vanished: "(.*?):(.*?)"/i', $row, $missingFileLocationMatches);
						$this->rsyncOutputParsedAsArray['rsyncMissingFiles'][] = $missingFileLocationMatches[1];
					} elseif (preg_match('/^(.*?):(.*?)+$/i', $row)) {
						$rowExp = explode(':', $row);

						$key = $rowExp[0];
						unset($rowExp[0]);
						$value = trim(implode('', $rowExp));
						if (isset($this->rsyncOutputParsedAsArray['keyValuePairs'][$key])) {
							$i = 1;
							while (isset($this->rsyncOutputParsedAsArray['keyValuePairs'][$key . '-' . $i])) {
								++$i;
							}

							$this->rsyncOutputParsedAsArray['keyValuePairs'][$key . '-' . $i] = $value;
						} else {
							$this->rsyncOutputParsedAsArray['keyValuePairs'][$key] = $value;
						}
					} elseif (!empty($row)) {
						$this->rsyncOutputParsedAsArray['miscData'][] = $row;
					}
				}

				/**
				 * Removing the bytes addition, because it's always returned in bytes
				 *
				 * @todo make sure it's returned in bytes and if not, then we should change it ourselves
				 */
				$this->rsyncOutputParsedAsArray['keyValuePairs']['Total file size'] =
					trim(str_replace(
						' bytes',
						'',
						$this->rsyncOutputParsedAsArray['keyValuePairs']['Total file size']));

				$this->rsyncOutputParsedAsArray['keyValuePairs']['Total transferred file size'] =
					trim(str_replace(
						' bytes',
						'',
						$this->rsyncOutputParsedAsArray['keyValuePairs']['Total transferred file size']));

				$this->rsyncOutputParsedAsArray['keyValuePairs']['Literal data'] =
					trim(str_replace(
						' bytes',
						'',
						$this->rsyncOutputParsedAsArray['keyValuePairs']['Literal data']));

				$this->rsyncOutputParsedAsArray['keyValuePairs']['Matched data'] =
					trim(str_replace(
						' bytes',
						'',
						$this->rsyncOutputParsedAsArray['keyValuePairs']['Matched data']));
			}
		}
		
		return $this->rsyncOutputParsedAsArray;
	}

	/**
	 * @return mixed
	 */
	public function getRsyncReturnCode()
	{
		$this->logEvent(__METHOD__, 'Executed', NXTHD_LOG_DEBUG);

		return $this->rsyncReturnCode;
	}

	/**
	 * @param string $rsyncReturnCode
	 * @return BackupLogModel
	 */
	public function setRsyncReturnCode($rsyncReturnCode)
	{
		$this->logEvent(__METHOD__, 'Executed', NXTHD_LOG_DEBUG);

		$this->rsyncReturnCode = $rsyncReturnCode;

		return $this;
	}

	/**
	 * @return mixed
	 */
	public function getAutoRsyncBackupErrorCode()
	{
		$this->logEvent(__METHOD__, 'Executed', NXTHD_LOG_DEBUG);

		return $this->autoRsyncBackupErrorCode;
	}

	/**
	 * @param string $autoRsyncBackupErrorCode
	 * @return BackupLogModel
	 */
	public function setAutoRsyncBackupErrorCode($autoRsyncBackupErrorCode)
	{
		$this->logEvent(__METHOD__, 'Executed', NXTHD_LOG_DEBUG);

		$this->autoRsyncBackupErrorCode = $autoRsyncBackupErrorCode;

		return $this;
	}

	/**
	 * @return string message
	 */
	public function getRsyncReturnCodeMessage()
	{
		$this->logEvent(__METHOD__, 'Executed', NXTHD_LOG_DEBUG);

		$code = $this->getRsyncReturnCode();

		if (!isset($this->rsyncErrorCodesArray[$code])) {
			return 'Unknown';
		}

		return $this->rsyncErrorCodesArray[$code];
	}

	/**
	 * @return mixed
	 */
	public function getAutoRsyncBackupErrorMessage()
	{
		$this->logEvent(__METHOD__, 'Executed', NXTHD_LOG_DEBUG);

		return $this->autoRsyncBackupErrorMessage;
	}

	/**
	 * @param string $autoRsyncBackupErrorMessage
	 * @return BackupLogModel
	 */
	public function setAutoRsyncBackupErrorMessage($autoRsyncBackupErrorMessage)
	{
		$this->logEvent(__METHOD__, 'Executed', NXTHD_LOG_DEBUG);

		$this->autoRsyncBackupErrorMessage = $autoRsyncBackupErrorMessage;

		return $this;
	}
}

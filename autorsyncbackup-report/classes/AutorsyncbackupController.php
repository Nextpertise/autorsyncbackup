<?php

/**
 * Class AutorsyncbackupController
 */
class AutorsyncbackupController
{
	private $parsedArguments;
	private $logDir;

	/**
	 * @param array $parsedArguments
	 */
	public function __construct(Array $parsedArguments)
	{
		$this->parsedArguments = $parsedArguments;

		$this->locateLogDir();
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
	 * Locates the log directory
	 *
	 * First, the CLI argument -l is checked, if that's present, that value will be used.
	 * Otherwise, we'll use the spooldir setting.
	 * One of those two settings MUST be available!
	 */
	private function locateLogDir()
	{
		$this->logEvent(__METHOD__, 'Executing', NXTHD_LOG_DEBUG);

		// Parameter -l overwrites config value spooldir, so we first check if this value is present
		if (array_key_exists('-l', $this->parsedArguments)) {
			$this->logEvent(__METHOD__,
				'Found parameter -l with logdir, overwriting any default config values', NXTHD_LOG_INFO);

			$this->logDir = $this->parsedArguments['-l'];
		// Grabbing log location from config file
		} elseif (($this->logDir = GlobalSettings::instance()->spooldir) === false) {
			$this->logEvent(__METHOD__,
				'Missing mandatory parameter -l=AUTORSYNCBACKUP_LOG_FOLDER' . 'since spooldir was not defined' .
				'in config', NXTHD_LOG_ERR);
			exit(1);
		}

		if (!file_exists($this->logDir)) {
			$this->logEvent(__METHOD__,
				'Folder "' . $this->logDir . '" not found, please provide an existing location', NXTHD_LOG_ERR);
			exit(1);
		}

		// Make sure the logDir has a trailing slash
		if (substr($this->logDir, -1 ) != '/') {
			$this->logEvent(__METHOD__, 'Adding trailing slash to log directory', NXTHD_LOG_DEBUG);

			$this->logDir = $this->logDir . '/';
		}

		$this->logEvent(__METHOD__, 'Accepted location ' . $this->logDir .
			' as autorsync backup log location');
	}

	/**
	 * Parses a filename.
	 * Expecting format: hostname_timestamp
	 *
	 * @param string $filename
	 * @return array
	 */
	private function parseLogFilename($filename)
	{
		/**
		 * Filenames should look like: host.ext_timestamp
		 */
		$filenameExp = explode('_', $filename);
		if (count($filenameExp) < 2 || !ctype_digit($filenameExp[1])) {
			$this->logEvent(__METHOD__, 'Invalid filename found, filename should end with _TIMESTAMP',
				NXTHD_LOG_DEBUG);
		}

		$timestamp = $filenameExp[1];
		$host = '';
		$i = 0;
		foreach ($filenameExp as $partial) {
			if ($i == 1) {
				$i = 2;
				continue;
			}

			$host .= $partial;
			++$i;
		}

		return array($host, $timestamp);
	}

	/**
	 * Iterates through the log directory and finds out whch files should be parsed.
	 *
	 * @return array
	 */
	private function findLogFilesToParse()
	{
		$this->logEvent(__METHOD__, 'Executing', NXTHD_LOG_DEBUG);

		// Log dir must be readable
		if (!is_readable($this->logDir)) {
			$this->logEvent(__METHOD__, 'Cannot read log directory ' . $this->logDir . ', exiting', NXTHD_LOG_ERR);
			exit(1);
		}

		$directoryIterator = new DirectoryIterator($this->logDir);

		$logFilesToParse = array();
		// Iterate through directory files
		foreach ($directoryIterator as $fileInfo) {
			if ($fileInfo->isDot() || !$fileInfo->isFile()) {
				continue;
			}
			$filename = $fileInfo->getFilename();

			$this->logEvent(__METHOD__, 'Found file ' . $filename, NXTHD_LOG_DEBUG);

			// Parse filename to find out which file is the most recent
			list($host, $timestamp) = $this->parseLogFilename($filename);

			$this->logEvent(__METHOD__,
				'Parsed filename to host: ' . $host . ' timestamp: ' . $timestamp, NXTHD_LOG_DEBUG);

			if (!isset($logFilesToParse[$host])) {
				$this->logEvent(__METHOD__,
					'Considering ' . date('Y-m-d H:i:s', $timestamp) . ' as most recent backup for ' . $host,
					NXTHD_LOG_DEBUG);

				$logFilesToParse[$host] = $timestamp;
			} else {
				if ($timestamp > $logFilesToParse[$host]) {
					$this->logEvent(__METHOD__,
						'Considering ' . date('Y-m-d H:i:s', $timestamp) . ' as most recent backup for ' . $host,
						NXTHD_LOG_DEBUG);

					$logFilesToParse[$host] = $timestamp;
				}
			}
		}

		return $logFilesToParse;
	}

	/**
	 * Reads a XML structured Autorsync backup log file and puts the data into a BackupLogModel.
	 * This model can be used to determine if the backup has succeed, to fetch information about the backup process
	 * and determine why a backup has failed.
	 *
	 * @param string $fileLocation
	 * @return BackupLogModel
	 */
	private function readAndParseLogFile($fileLocation)
	{
		$this->logEvent(__METHOD__, 'Executing', NXTHD_LOG_DEBUG);

		// File must be readable
		if (!is_readable($fileLocation)) {
			$this->logEvent(__METHOD__, 'Cannot read file ' . $fileLocation . ', skipping file', NXTHD_LOG_ERR);
		}

		// Fetch contents (expecting valid XML)
		$fileContents = file_get_contents($fileLocation);

		$this->logEvent(__METHOD__,
			'Read ' . count(explode(PHP_EOL, $fileContents)) . ' lines from file ' . $fileLocation,
			NXTHD_LOG_DEBUG);

		// Try to parse XML file
		try {
			$logFileParsedXml = new SimpleXMLElement($fileContents);

			$this->logEvent(__METHOD__, 'Read file ' . $fileLocation . ' and successfully parsed XML', NXTHD_LOG_INFO);
			$this->logEvent(__METHOD__,
				'Creating BackupLogModel for host ' . (string) $logFileParsedXml->hostname . ' with XML data',
				NXTHD_LOG_DEBUG);

			/**
			 * Assuming all the values below are present in the XML file
			 *
			 * @todo check if the properties exists, and when they don't an error should be shown.
			 */
			$backupLogModel = new BackupLogModel();
			$backupLogModel->setJobfile((string) $logFileParsedXml->jobfile)
				->setHostname((string) $logFileParsedXml->hostname)
				->setUsername((string) $logFileParsedXml->username)
				->setShare((string) $logFileParsedXml->jobfile)
				->setDestinationFolder((string) $logFileParsedXml->destfolder)
				->setSpeedLimitInKbs((string) $logFileParsedXml->speedlimitkb)
				->setStartTime((string) $logFileParsedXml->starttime)
				->setStartTimestamp((string) $logFileParsedXml->starttimestamp)
				->setEndTime((string) $logFileParsedXml->endtime)
				->setEndTimestamp((string) $logFileParsedXml->endtimestamp)
				->setFileset((string) $logFileParsedXml->fileset)
				->setFilesetRotate((string) $logFileParsedXml->filesetrotate)
				->setRsyncOutput((string) $logFileParsedXml->rsyncoutput)
				->setRsyncReturnCode((string) $logFileParsedXml->rsyncreturncode)
				->setAutoRsyncBackupErrorCode((string) $logFileParsedXml->autorsyncbackuperrorcode)
				->setAutoRsyncBackupErrorMessage((string) $logFileParsedXml->autorsyncbackuperrormsg);

			return $backupLogModel;
		}

		catch (Exception $e) {
			$this->logEvent(__METHOD__,
				'Error "' . $e->getMessage() . '" while parsing XML from file ' . $fileLocation . ', skipping file',
				NXTHD_LOG_ERR);
		}

		return null;
	}

	/**
	 * Reads and parse one or more files into models, puts them in an array and returns them.
	 *
	 * @param array $logFilesToParse
	 * @return array
	 */
	private function getBackupLogModelsByFileInfo(Array $logFilesToParse)
	{
		$backupLogModels = array();
		foreach ($logFilesToParse as $host => $timestamp) {
			$this->logEvent(__METHOD__,
				'Found log file for ' . $host . ' created @ ' . date('Y-m-d H:i:s', $timestamp), NXTHD_LOG_INFO);

			$fileLocation = $this->logDir . $host . '_' . $timestamp;

			$backupLogModel = $this->readAndParseLogFile($fileLocation);
			if (is_null($backupLogModel)) {
				$this->logEvent(__METHOD__, 'Couldn\'t read log file ' . $fileLocation . ', skipping!', NXTHD_LOG_ERR);
				continue;
			}
			$backupLogModels[] = $backupLogModel;
		}

		$this->logEvent(__METHOD__, 'Returning ' . count($backupLogModels) . ' bacupLogModels', NXTHD_LOG_DEBUG);

		return $backupLogModels;
	}

	/**
	 * @param string $subject
	 * @param string $html
	 * @throws Exception
	 * @throws phpmailerException
	 * @return bool
	 */
	private function sendMailReport($subject, $html)
	{
		require_once 'vendor/phpmailer/phpmailer/PHPMailerAutoload.php';
		$mail = new PHPMailer;

		// @todo: put this in a separate function
		if(isset(GlobalSettings::instance()->fqdn)) {
			$fqdn = GlobalSettings::instance()->fqdn;
		} else {
			$fqdn = shell_exec('hostname -f');
		}

		// @todo: Implement valid FQDN check, hostname -f could give back localhost which leads to a unvalid from e-mail address.
		$mail->From = 'autorsyncbackup@' . $fqdn;
		$mail->FromName = 'Autorsyncbackup';

		$mail->isHTML(true);
		$mail->Subject = $subject;
		$mail->Body    = $html;
		$mail->AltBody = 'This is the body in plain text for non-HTML mail clients';
	
		if (GlobalSettings::instance()->emailReportRecipients) {
			foreach(GlobalSettings::instance()->emailReportRecipients as $mailTo) {
				$mail->addAddress($mailTo);
				echo $mailTo;
			}
		} else {
			$this->logEvent(__METHOD__, "Error when sending mail report, no 'emailReportRecipients' field specified in config.yaml", NXTHD_LOG_ERR);
			exit(1);
		}

		if (GlobalSettings::instance()->emailReportCc) {
			foreach (GlobalSettings::instance()->emailReportCc as $mailCc) {
				$mail->addCC($mailCc);
			}
		}

		if (GlobalSettings::instance()->emailReportBcc) {
			foreach (GlobalSettings::instance()->emailReportBcc as $mailBcc) {
				$mail->addBCC($mailBcc);
			}
		}

		if (!$mail->send()) {
			$this->logEvent(__METHOD__, 'Error when sending mail report', NXTHD_LOG_ERR);

			return false;
		} else {
			$this->logEvent(__METHOD__, 'Report mail is sent', NXTHD_LOG_INFO);

			return true;
		}
	}

	/**
	 * External callable action which parses a single log file
	 *
	 * @param string $filename
	 * @todo finish method, should mail report
	 */
	public function parseSingeLogFileAction($filename)
	{
		$this->logEvent(__METHOD__, 'Executing', NXTHD_LOG_DEBUG);

		if (!preg_match('/^[a-z0-9\-_.]+$/i', $filename)) {
			$this->logEvent(__METHOD__,
				'Invalid format for parameter with log file name. ' .
				'Allowed: a-z, A-Z, 0-9, -, _, .. Received: ' . $filename, NXTHD_LOG_ERR);
			exit(1);
		}

		list($host, $timestamp) = $this->parseLogFilename($filename);

		$backupLogModel = $this->getBackupLogModelsByFileInfo(array(
			$host => $timestamp
		))[0];

		// TODO: mail report command
		$smarty = new Smarty;
		$smarty->assign('backupLogModel', $backupLogModel);
		$this->sendMailReport('Single backup report of ' . $backupLogModel->hostname,
			$smarty->fetch('single-backup-log.tpl'));
	}

	/**
	 * External callable action which parsed the most recent log file for every host
	 */
	public function parseLogAction()
	{
		$this->logEvent(__METHOD__, 'Executing', NXTHD_LOG_DEBUG);

		// Find log files to pare
		$logFilesToParse = $this->findLogFilesToParse();
		// Parse log files into models
		$backupLogModels = $this->getBackupLogModelsByFileInfo($logFilesToParse);

		// No hosts were backed up? Notify administrator and exit
		if (count($backupLogModels) == 0) {
			$smarty = new Smarty();
			$smarty->assign('mailSubject', 'Backup error: NO BACKUPS FOUND');

			$this->sendMailReport('No hosts backed up!', $smarty->fetch('no-backups.tpl'));
			return true;
		} else {
			$this->logEvent(__METHOD__, 'Received ' . count($backupLogModels) . ' BackupLogModel(s)');
		}

		/**
		 * State is used as an overall state which is used to determine if a human has to take a look at the
		 * backup logs.
		 *
		 * ok		= nothing is wrong
		 * warning	= please take a look, it could be important
		 * error	= serious issue which cause one or more backups to fail
		 */
		$overallBackupState					= 'ok';
		// Some values which are totaled for reporting purposes
		$numberOfFilesPerHost		 		= array();
		$numberOfFilesTransferredPerHost	= array();
		$totalFileSizePerHost		 		= array();
		$totalTransferredFileSizePerHost 	= array();
		$literalDataPerHost	 				= array();
		$matchedDataPerHost	 				= array();
		$fileListSizePerHost	 			= array();
		$fileListGenerationTimePerHost 		= array();
		$fileListTransferTimePerHost 		= array();
		$totalBytesSentPerHost				= array();
		$totalBytesReceivedPerHost	 		= array();
		$speedLimitsPerHost			 		= array();
		$backupDurationPerHost				= array();
		// Holds the backupLogModels sorted by hostname
		$backupLogs					 		= array();
		// Array of hostnames
		$hostnameList						= array();
		// Hostnames to backup (array with hosts)
		// Array with hostnames
		$hostsToBackup = GlobalSettings::instance()->hostsToBackup;
		// Array which holds complete backup info per host
		$backupReportPerHost				= array();

		/**
		 * If the max backup treshold in hours (maxBackupThresholdInHours) is defined, we should check
		 * if every host has been backed up within that time
		 */
		if (GlobalSettings::instance()->maxBackupThresholdInHours !== false) {
			$maxBackupThresholdInHours = GlobalSettings::instance()->maxBackupThresholdInHours;
		}

		// Iterate over the backupLogModels
		foreach ($backupLogModels as $backupLogModel) {
			$currentBackupState				= 'ok';
			$hostname 						= $backupLogModel->hostname;
			$hostnameList[]					= $hostname;
			$backupLogs[$hostname]			= $backupLogModel;
			$rsyncResponse					= $backupLogModel->rsyncOutputParsedAsArray;
			$backupReportPerHost[$hostname] = array(
				'hostname' 				=> $hostname,
				'rsyncReturnMessage'	=> $backupLogModel->rsyncReturnCodeMessage,
				'rsyncNotifications'	=> array(),
				'rsyncErrors'			=> array(),
				'missingFilesAndDirs'	=> array(),
			);

			$rsyncFoundAllDirectories = null;

			if (count($rsyncResponse['rsyncErrors']) > 0) {
				foreach ($rsyncResponse['rsyncErrors'] as $rsyncError) {
					/**
					 * Rsync error which says that some files that should be transferred could not be found is a minor
					 * problem which should not require the attention of a sysadmin.
					 *
					 * The error "IO error encountered -- skipping file deletion" could be severe, so
					 *
					 * All other errors issue at least a warning!
					 *
					 * @todo find out more common errors to handle them
					 */
					if ($rsyncError == 'IO error encountered -- skipping file deletion' ||
						preg_match(
						'/error:(.*?)(code 23|24)/i',
						$rsyncError)) {

						if (is_null($rsyncFoundAllDirectories)) {
							/**
							 * Let the user know not all files were found.
							 *
							 * @todo Show the user which files or directories haven't been found.
							 */
							$this->logEvent(__METHOD__, 'Rsync was not able to find all directories that should have been backed up', implode(':', $rsyncResponse['rsyncMissingFiles']));
							$backupReportPerHost[$hostname]['rsyncNotifications'][] =
								'Was not able to find all directories that should have been backed up.';
						}

						$rsyncFoundAllDirectories = false;
					} else {
						$this->logEvent(__METHOD__,
							'Host Rsync backup error: ' . str_replace("\n", '--newline--', $rsyncError),
							NXTHD_LOG_ERR);
						$currentBackupState = 'error';
						$backupReportPerHost[$hostname]['rsyncErrors'][] = $rsyncError;
					}
				}
			}

			/**
			 * When backing up data, the backup server should always send some data.
			 * There must be a problem when no bytes are sent.
			 */
			if ($rsyncResponse['keyValuePairs']['Total bytes sent'] == 0) {
				$currentBackupState = 'error';
			}

			/**
			 * When backing up date, the backup server should always receive some data.
			 * There must me a problem when no bytes are received.
			 */
			if ($rsyncResponse['keyValuePairs']['Total bytes sent'] == 0) {
				$currentBackupState = 'error';
			}

			/**
			 * We want to know if a backup job has been running recently (within our definable time threshold in hours.
			 */
			if (isset($maxBackupThresholdInHours)) {
				if ($backupLogModel->starttimestamp > (time() - (3600 * $maxBackupThresholdInHours))) {
					$this->logEvent(__METHOD__, 'Backup of host ' . $hostname . ' started within threshold of ' .
						$maxBackupThresholdInHours . ' hours');

					$backupWithinTimeThreshold = true;
				} else {
					$this->logEvent(__METHOD__, 'Backup of host ' . $hostname . ' NOT started within threshold of ' .
						$maxBackupThresholdInHours . ' hours. ' .
						'Actual time: ' . date('Y-m-d H:i:s', $backupLogModel->starttimestamp)
						. ' VS ' . $maxBackupThresholdInHours . ' hours ago: ' .
						date('Y-m-d H:i:s', (time() - (3600 * $maxBackupThresholdInHours))), NXTHD_LOG_ERR);

					$backupWithinTimeThreshold = false;
					$currentBackupState = 'error';
				}
			}

			/**
			 * When the current backup state is worse than the overall backup state, we should update the overall
			 * backup state.
			 */
			if ($overallBackupState == 'ok') {
				if ($currentBackupState != 'ok') {
					$overallBackupState = $currentBackupState;
				}
			} elseif ($overallBackupState == 'warning') {
				if ($currentBackupState == 'error') {
					$overallBackupState = $currentBackupState;
				}
			}

			$backupReportPerHost[$hostname]['backupState'] = $currentBackupState;
			$backupReportPerHost[$hostname]['backupDatetime'] = $backupLogModel->starttime;
			if (isset($maxBackupThresholdInHours)) {
				$backupReportPerHost[$hostname]['backupWithinTimeThreshold'] =
					(isset($backupWithinTimeThreshold) && $backupWithinTimeThreshold ? 'yes' : 'no');
			}

			$backupReportPerHost[$hostname]['backupDuration'] =
				humanReadableTimeDuration($backupLogModel->endtimestamp - $backupLogModel->starttimestamp);
			$backupReportPerHost[$hostname]['numberOfFiles'] = $rsyncResponse['keyValuePairs']['Number of files'];
			$backupReportPerHost[$hostname]['numberOfFilesTransferred'] =
				$rsyncResponse['keyValuePairs']['Number of files transferred'];
			$backupReportPerHost[$hostname]['totalFileSize'] =
				humanReadableFileSize($rsyncResponse['keyValuePairs']['Total file size']);
			$backupReportPerHost[$hostname]['totalTransferredFileSize'] =
				humanReadableFileSize($rsyncResponse['keyValuePairs']['Total transferred file size']);
			$backupReportPerHost[$hostname]['literalData'] =
				humanReadableFileSize($rsyncResponse['keyValuePairs']['Literal data']);
			$backupReportPerHost[$hostname]['matchedData'] =
				humanReadableFileSize($rsyncResponse['keyValuePairs']['Matched data']);
			$backupReportPerHost[$hostname]['fileListSize'] = $rsyncResponse['keyValuePairs']['File list size'];
			$backupReportPerHost[$hostname]['fileListGenerationTime'] =
				$rsyncResponse['keyValuePairs']['File list generation time'];
			$backupReportPerHost[$hostname]['fileListTransferTime'] =
				$rsyncResponse['keyValuePairs']['File list transfer time'];
			$backupReportPerHost[$hostname]['totalSent'] =
				humanReadableFileSize($rsyncResponse['keyValuePairs']['Total bytes sent']);
			$backupReportPerHost[$hostname]['totalReceived'] =
				humanReadableFileSize($rsyncResponse['keyValuePairs']['Total bytes received']);

			// Calculate the totals
			$numberOfFilesPerHost[$hostname]			= $rsyncResponse['keyValuePairs']['Number of files'];
			$numberOfFilesTransferredPerHost[$hostname]	= $rsyncResponse['keyValuePairs']['Number of files transferred'];
			$totalFileSizePerHost[$hostname]		 	= $rsyncResponse['keyValuePairs']['Total file size'];
			$totalTransferredFileSizePerHost[$hostname]	= $rsyncResponse['keyValuePairs']['Total transferred file size'];
			$literalDataPerHost[$hostname]	 			= $rsyncResponse['keyValuePairs']['Literal data'];
			$matchedDataPerHost[$hostname]	 			= $rsyncResponse['keyValuePairs']['Matched data'];
			$fileListSizePerHost[$hostname]	 			= $rsyncResponse['keyValuePairs']['File list size'];
			$fileListGenerationTimePerHost[$hostname] 	= $rsyncResponse['keyValuePairs']['File list generation time'];
			$fileListTransferTimePerHost[$hostname] 	= $rsyncResponse['keyValuePairs']['File list transfer time'];
			$totalBytesSentPerHost[$hostname]			= $rsyncResponse['keyValuePairs']['Total bytes sent'];
			$totalBytesReceivedPerHost[$hostname]	 	= $rsyncResponse['keyValuePairs']['Total bytes received'];
			$speedLimitsPerHost[$hostname] 				= $backupLogModel->speedLimitInKbs;
			$backupDurationPerHost[$hostname]			= $backupLogModel->endtimestamp - $backupLogModel->starttimestamp;
		}

		// Number of hosts that have been backed up (or have been tried to backup)
		$backupsCount = count($backupLogs);

		$missingHosts = array();
		/**
		 * Code inspector shows an error for statement while it's ok and works. Suppressing error.
		 */
		/** @noinspection PhpWrongForeachArgumentTypeInspection */
		foreach ($hostsToBackup as $hostname) {
			if (!in_array($hostname, $hostnameList)) {
				$missingHosts[] = $hostname;

				// Host that should have been backed up, hasn't been backed up, that's an error!
				$this->logEvent(__METHOD__, 'Host ' . $hostname . ' should have been backed up, but has not!',
					NXTHD_LOG_ERR);
				$overallBackupState = 'error';
			}
		}

		$cliOutput			= CliOutput::instance();
		$errorMessages		= array();
		foreach ($cliOutput->errorMessages as $errorMessage) {
			$errorMessages[] = preg_replace(
				'/[0-9]{2,4}\-[0-9]{2,4}\-[0-9]{2,4}[\s]{0,2}[0-9]{2}\:[0-9]{2}\:[0-9]{2}[\s]{0,2}\-[\s]{0,2}[a-z\:\(\)]{0,128}/i', '', $errorMessage);
		}
		$warningMessages	= $cliOutput->warningMessages;
		$errorCount 		= count($errorMessages);
		$warningCount		= count($warningMessages);

		// The desired mail subject
		if ($overallBackupState == 'ok') {
			$mailSubject = 'Backup succeed';
		} elseif ($overallBackupState == 'warning') {
			$mailSubject = 'Backup WARNING: ' . $warningCount . ' warnings';
		} else {
			$mailSubject = 	'Backup ERROR: ' . $errorCount . ' error(s) and ' . $warningCount .
				' warnings';
		}

		$totalBackupDuration = array_sum($backupDurationPerHost);

		$smarty = new Smarty;

		// Overall backup info
		$smarty->assign('overallBackupState',				$overallBackupState);
		$smarty->assign('errors', 							$errorMessages);
		$smarty->assign('warnings', 						$warningMessages);

		$smarty->assign('numberOfHostsBackedUp',			$backupsCount);
		$smarty->assign('hostnameList',						$hostnameList);
		$smarty->assign('missingHosts',						$missingHosts);
		$smarty->assign('totalBackupDuration',				humanReadableTimeDuration($totalBackupDuration));
		$smarty->assign('averageBackupDuration',			humanReadableTimeDuration($totalBackupDuration / $backupsCount));
		$smarty->assign('averageSpeedLimitInKbs',			(array_sum($speedLimitsPerHost) / $backupsCount));
		$smarty->assign('totalNumberOfFiles',				number_format(array_sum($numberOfFilesPerHost), 0, ',', '.'));
		$smarty->assign('totalNumberOfFilesTransferred',
			number_format(array_sum($numberOfFilesTransferredPerHost), 0, ',', '.'));
		$smarty->assign('totalFileSize',					humanReadableFileSize(array_sum($totalFileSizePerHost)));
		$smarty->assign('totalTransferredFileSize',
			humanReadableFileSize(array_sum($totalTransferredFileSizePerHost)));
		$smarty->assign('totalLiteralData',					humanReadableFileSize(array_sum($literalDataPerHost)));
		$smarty->assign('totalMatchedData',					humanReadableFileSize(array_sum($matchedDataPerHost)));
		$smarty->assign('totalFileListSize',				humanReadableFileSize(array_sum($fileListSizePerHost)));
		$smarty->assign('totalFileListGenerationTime',
			number_format(array_sum($fileListGenerationTimePerHost), 3, ',', '.') . ' seconds');
		$smarty->assign('totalFileListTransferTime',
			number_format(array_sum($fileListTransferTimePerHost), 3, ',', '.') . ' seconds');
		$smarty->assign('totalSent',						humanReadableFileSize(array_sum($totalBytesSentPerHost)));
		$smarty->assign('totalReceived',					humanReadableFileSize(array_sum($totalBytesReceivedPerHost)));

		// Backup info per host
		$smarty->assign('backupReportPerHost',				$backupReportPerHost);

		$this->sendMailReport($mailSubject, $smarty->fetch('email-template.tpl'));

		return true;
	}
}

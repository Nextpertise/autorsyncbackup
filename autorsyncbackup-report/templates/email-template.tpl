<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
		"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
	<meta name="viewport" content="width=device-width, initial-scale=1"/>
	<title>Zen Flat Confirm Email</title>
	<style type="text/css" media="screen">
		/* Force Hotmail to display emails at full width */
		.ExternalClass {
			display: block !important;
			width: 100%;
		}

		/* Force Hotmail to display normal line spacing */
		.ExternalClass,
		.ExternalClass p,
		.ExternalClass span,
		.ExternalClass font,
		.ExternalClass td,
		.ExternalClass div {
			line-height: 100%;
		}

		body,
		p,
		h1,
		h2,
		h3,
		h4,
		h5,
		h6 {
			margin: 0;
			padding: 0;
		}

		body,
		p,
		td {
			font-family: Arial, Helvetica, sans-serif;
			font-size: 15px;
			color: #333333;
			line-height: 1.2em;
		}

		h1 {
			font-size: 24px;
			font-weight: normal;
			line-height: 24px;
		}

		body,
		p {
			margin-bottom: 0;
			-webkit-text-size-adjust: none;
			-ms-text-size-adjust: none;
		}

		img {
			line-height: 100%;
			outline: none;
			text-decoration: none;
			-ms-interpolation-mode: bicubic;
		}

		a img {
			border: none;
		}

		.background {
			background-color: #333333;
		}

		table.background {
			margin: 0;
			padding: 0;
			width: 100% !important;
		}

		.block-img {
			display: block;
			line-height: 0;
		}

		a {
			color: white;
			text-decoration: none;
		}

		a,
		a:link {
			color: #2A5DB0;
			text-decoration: underline;
		}

		table td {
			border-collapse: collapse;
		}

		td {
			vertical-align: top;
			text-align: left;
		}

		.wrap {
			width: 90%;
		}

		.wrap-cell {
			padding-top: 30px;
			padding-bottom: 30px;
		}

		.header-cell,
		.body-cell,
		.footer-cell {
			padding-left: 20px;
			padding-right: 20px;
		}

		.header-cell {
			background-color: #eeeeee;
			font-size: 24px;
			color: #000000;
		}

		.body-cell {
			background-color: #ffffff;
			padding-top: 30px;
			padding-bottom: 34px;
		}

		.footer-cell {
			background-color: #eeeeee;
			text-align: center;
			font-size: 13px;
			padding-top: 30px;
			padding-bottom: 30px;
		}

		.card {
			width: 100%;
			margin: 0 auto;
		}

		.data-heading {
			text-align: left;
			padding: 0 10px 0 10px;
			background-color: #ffffff;
			font-weight: bold;
		}

		.data-value {
			text-align: left;
			padding: 0 10px 0 10px;
			background-color: #ffffff;
		}

		.force-full-width {
			width: 100% !important;
		}
	</style>
	<style type="text/css" media="only screen and (max-width: 600px)">
		@media only screen and (max-width: 600px) {
			body[class*="background"],
			table[class*="background"],
			td[class*="background"] {
				background: #eeeeee !important;
			}

			table[class="card"] {
				width: auto !important;
			}

			td[class="data-heading"],
			td[class="data-value"] {
				display: block !important;
			}

			td[class="data-heading"] {
				text-align: left !important;
				padding: 10px 10px 0;
			}

			table[class="wrap"] {
				width: 100% !important;
			}

			td[class="wrap-cell"] {
				padding-top: 0 !important;
				padding-bottom: 0 !important;
			}
		}
	</style>
</head>
<body leftmargin="0" marginwidth="0" topmargin="0" marginheight="0" offset="0" bgcolor="" class="background">
<table align="center" border="0" cellpadding="0" cellspacing="0" height="100%" width="100%" class="background">
	<tr>
		<td align="center" valign="top" width="100%" class="background">
			<center>
				<table cellpadding="0" cellspacing="0" width="600" class="wrap">
					<tr>
						<td valign="top" class="wrap-cell" style="padding-top:30px; padding-bottom:30px;">
							<table cellpadding="0" cellspacing="0" class="force-full-width">
								<tr>
									<td height="60" valign="top" class="header-cell" style="padding-top:15px;">
										Auto Rsync Backup report
									</td>
								</tr>
								<tr>
									<td valign="top" class="body-cell">
										<table cellpadding="0" cellspacing="0" width="100%" bgcolor="#ffffff">
											<tr>
												<td>
													<table cellspacing="0" cellpadding="0" width="100%"
													       bgcolor="#ffffff">
														<tr>
															<td align="center" style="padding:20px 0;">
																<center>
																	<table cellspacing="0" cellpadding="0" class="card">
																		<tr>
																			{if $overallBackupState eq 'error'}
																			<td style="background-color:red; text-align:center; padding:10px; color:white;">
																				Overall backup state: error
																			</td>
																			{elseif $overallBackupState eq 'warning'}
																			<td style="background-color:orange; text-align:center; padding:10px; color:white;">
																				Overall backup state: warning
																			</td>
																			{else}
																			<td style="background-color:green; text-align:center; padding:10px; color:white;">
																				Overall backup state: success
																			</td>
																			{/if}
																		</tr>
																		<tr>
																			<td style="border:1px solid green;">
																				<table cellpadding="0" cellspacing="20"
																				       width="100%">
																					{if !empty($errors)}
																						<tr><td><h2>Errors</h2></td></tr>
																						{foreach from=$errors item=error}
																							<tr>
																								<td>{$error}</td>
																							</tr>
																						{/foreach}
																					{/if}
																					{if !empty($warnings)}
																						<tr><td><h2>Warnings</h2></td></tr>
																						{foreach from=$warnings item=warning}
																							<tr>
																								<td>{$warning}</td>
																							</tr>
																						{/foreach}
																					{/if}
																					{if $overallBackupState eq 'ok'}
																						No errors found, backup succeeded
																					{/if}
																				</table>
																			</td>
																		</tr>
																	</table>
																</center>
															</td>
														</tr>
													</table>
													<table cellspacing="0" cellpadding="0" width="100%"
													       bgcolor="#ffffff">
														<tr>
															<td align="center" style="padding:20px 0;">
																<center>
																	<table cellspacing="0" cellpadding="0" class="card">
																		<tr>
																			<td style="background-color:white; text-align:center; padding:10px; color:black;">
																				Overall backup info
																			</td>
																		</tr>
																		<tr>
																			<td style="border:1px solid green; padding: 20px 0 20px;">
																				<table cellspacing="0" cellpadding="0"
																				       width="100%">
																					<tr>
																						<td>
																							<table cellpadding="0"
																							       cellspacing="0"
																							       width="100%"
																							       bgcolor="#ffffff">
																								<tr>
																									<td width="50%"
																									    class="data-heading">
																										Overall backup state
																									</td>
																									<td class="data-value">
																										{$overallBackupState}
																									</td>
																								</tr>
																								<tr>
																									<td width="50%"
																									    class="data-heading">
																										Backup host count
																									</td>
																									<td class="data-value">
																										{$numberOfHostsBackedUp}
																									</td>
																								</tr>
																								<tr><td colspan="2">&nbsp;</td></tr>
																								<tr>
																									<td width="50%"
																									    class="data-heading">
																										Backup host list
																									</td>
																									<td class="data-value">
																										{foreach from=$hostnameList item=hostname name=hostnameListForeach}
																											{$hostname}<br />
																										{/foreach}
																									</td>
																								</tr>
																								<tr><td colspan="2">&nbsp;</td></tr>
																								<tr>
																									<td width="50%"
																									    class="data-heading">
																										Missing hosts:
																									</td>
																									<td class="data-value">
																										{foreach from=$missingHosts item=missingHostname name=missingHostListForeach}
																											{$missingHostname}<br />
																										{/foreach}
																									</td>
																								</tr>
																								<tr><td colspan="2">&nbsp;</td></tr>
																								<tr>
																									<td width="50%"
																									    class="data-heading">
																										Total backup duration
																									</td>
																									<td class="data-value">
																										{$totalBackupDuration}
																									</td>
																								</tr>
																								<tr>
																									<td width="50%"
																									    class="data-heading">
																										Average backup duration
																									</td>
																									<td class="data-value">
																										{$averageBackupDuration}
																									</td>
																								</tr>
																								<tr>
																									<td width="50%"
																									    class="data-heading">
																										Average speed limit in KBs
																									</td>
																									<td class="data-value">
																										{$averageSpeedLimitInKbs}
																									</td>
																								</tr>
																								<tr>
																									<td width="50%"
																									    class="data-heading">
																										Total number of files
																									</td>
																									<td class="data-value">
																										{$totalNumberOfFiles}
																									</td>
																								</tr>
																								<tr>
																									<td width="50%"
																									    class="data-heading">
																										Total number of files transferred
																									</td>
																									<td class="data-value">
																										{$totalNumberOfFilesTransferred}
																									</td>
																								</tr>
																								<tr>
																									<td width="30%"
																									    class="data-heading">
																										Total file size
																									</td>
																									<td class="data-value">
																										{$totalFileSize}
																									</td>
																								</tr>
																								<tr>
																									<td width="50%"
																									    class="data-heading">
																										Total transferred file size
																									</td>
																									<td class="data-value">
																										{$totalTransferredFileSize}
																									</td>
																								</tr>
																								<tr>
																									<td width="50%"
																									    class="data-heading">
																										Total literal data
																									</td>
																									<td class="data-value">
																										{$totalLiteralData}
																									</td>
																								</tr>
																								<tr>
																									<td width="50%"
																									    class="data-heading">
																										Total matched data
																									</td>
																									<td class="data-value">
																										{$totalMatchedData}
																									</td>
																								</tr>
																								<tr>
																									<td width="50%"
																									    class="data-heading">
																										Total file list size
																									</td>
																									<td class="data-value">
																										{$totalFileListSize}
																									</td>
																								</tr>
																								<tr>
																									<td width="50%"
																									    class="data-heading">
																										Total file list generation time
																									</td>
																									<td class="data-value">
																										{$totalFileListGenerationTime}
																									</td>
																								</tr>
																								<tr>
																									<td width="50%"
																									    class="data-heading">
																										Total file list transfer time
																									</td>
																									<td class="data-value">
																										{$totalFileListTransferTime}
																									</td>
																								</tr>
																								<tr>
																									<td width="50%"
																									    class="data-heading">
																										Total sent
																									</td>
																									<td class="data-value">
																										{$totalSent}
																									</td>
																								</tr>
																								<tr>
																									<td width="50%"
																									    class="data-heading">
																										Total received
																									</td>
																									<td class="data-value">
																										{$totalReceived}
																									</td>
																								</tr>
																							</table>
																						</td>
																					</tr>
																				</table>
																			</td>
																		</tr>
																	</table>
																	{foreach from=$backupReportPerHost item=serverBackupReport}
																		<table cellspacing="0" cellpadding="0" class="card" style="margin-top: 20px">
																			<tr>
																				{if $serverBackupReport.backupState eq 'error'}
																					<td style="background-color:red; text-align:center; padding:10px; color:white !important;">
																						{$serverBackupReport.hostname}
																					</td>
																				{elseif $serverBackupReport.backupState eq 'warning'}
																					<td style="background-color:orange; text-align:center; padding:10px; color:white !important;">
																						{$serverBackupReport.hostname}
																					</td>
																				{else}
																					<td style="background-color:green; text-align:center; padding:10px; color:white !important;">
																						<span style="color: #fff">{$serverBackupReport.hostname}</span>
																					</td>
																				{/if}
																			</tr>
																			<tr>
																				<td style="border:1px solid green; padding: 20px 0 20px;">
																					<table cellspacing="0" cellpadding="0"
																					       width="100%">
																						<tr>
																							<td>
																								<table cellpadding="0"
																								       cellspacing="0"
																								       width="100%"
																								       bgcolor="#ffffff">
																									<tr>
																										<td width="50%"
																										    class="data-heading">
																											Rsync return message
																										</td>
																										<td class="data-value">
																											{$serverBackupReport.rsyncReturnMessage}
																										</td>
																									</tr>
																									<tr>
																										<td width="50%"
																										    class="data-heading">
																											Rsync notifications
																										</td>
																										<td class="data-value">
																											<ul>
																												{if (count($serverBackupReport.rsyncNotifications) gt 0)}
																													{foreach from=$serverBackupReport.rsyncNotifications item=rsyncNotification}
																														<li>{$rsyncNotification}</li>
																													{/foreach}
																												{else}
																													<li>No notifications</li>
																												{/if}
																											</ul>
																										</td>
																									</tr>
																									<tr>
																										<td width="50%"
																										    class="data-heading">
																											Rsync errors
																										</td>
																										<td class="data-value">
																											<ul>
																												{if (count($serverBackupReport.rsyncErrors) gt 0)}
																													{foreach from=$serverBackupReport.rsyncErrors item=rsyncError}
																														<li>{$rsyncError}</li>
																													{/foreach}
																												{else}
																													<li>No errors</li>
																												{/if}
																											</ul>
																										</td>
																									</tr>
																									<tr>
																										<td width="50%"
																										    class="data-heading">
																											Missing files and directories
																										</td>
																										<td class="data-value">
																											<ul>
																												{if (count($serverBackupReport.missingFilesAndDirs) gt 0)}
																													{foreach from=$serverBackupReport.missingFilesAndDirs item=missingLocation}
																														<li>{$missingLocation}</li>
																													{/foreach}
																												{else}
																													<li>Nothing is missing</li>
																												{/if}
																											</ul>
																										</td>
																									</tr>
																									<tr>
																										<td width="50%"
																										    class="data-heading">
																											Backup state
																										</td>
																										<td class="data-value">
																											{$serverBackupReport.backupState}
																										</td>
																									</tr>
																									<tr>
																										<td width="50%"
																										    class="data-heading">
																											Backup datetime
																										</td>
																										<td class="data-value">
																											{$serverBackupReport.backupDatetime}
																										</td>
																									</tr>
																									<tr>
																										<td width="50%"
																										    class="data-heading">
																											Backup within time threshold
																										</td>
																										<td class="data-value">
																											{$serverBackupReport.backupWithinTimeThreshold}
																										</td>
																									</tr>
																									<tr>
																										<td width="50%"
																										    class="data-heading">
																											Backup duration
																										</td>
																										<td class="data-value">
																											{$serverBackupReport.backupDuration}
																										</td>
																									</tr>
																									<tr>
																										<td width="50%"
																										    class="data-heading">
																											Number of files
																										</td>
																										<td class="data-value">
																											{$serverBackupReport.numberOfFiles}
																										</td>
																									</tr>
																									<tr>
																										<td width="50%"
																										    class="data-heading">
																											Number of files transferred
																										</td>
																										<td class="data-value">
																											{$serverBackupReport.numberOfFilesTransferred}
																										</td>
																									</tr>
																									<tr>
																										<td width="50%"
																										    class="data-heading">
																											Total file size
																										</td>
																										<td class="data-value">
																											{$serverBackupReport.totalFileSize}
																										</td>
																									</tr>
																									<tr>
																										<td width="50%"
																										    class="data-heading">
																											Total file size transferred
																										</td>
																										<td class="data-value">
																											{$serverBackupReport.totalTransferredFileSize}
																										</td>
																									</tr>
																									<tr>
																										<td width="50%"
																										    class="data-heading">
																											Literal data
																										</td>
																										<td class="data-value">
																											{$serverBackupReport.literalData}
																										</td>
																									</tr>
																									<tr>
																										<td width="50%"
																										    class="data-heading">
																											Matched data
																										</td>
																										<td class="data-value">
																											{$serverBackupReport.matchedData}
																										</td>
																									</tr>
																									<tr>
																										<td width="50%"
																										    class="data-heading">
																											File list size
																										</td>
																										<td class="data-value">
																											{$serverBackupReport.fileListSize}
																										</td>
																									</tr>
																									<tr>
																										<td width="50%"
																										    class="data-heading">
																											File list generation time
																										</td>
																										<td class="data-value">
																											{$serverBackupReport.fileListGenerationTime}
																										</td>
																									</tr>
																									<tr>
																										<td width="50%"
																										    class="data-heading">
																											File list transfer time
																										</td>
																										<td class="data-value">
																											{$serverBackupReport.fileListTransferTime}
																										</td>
																									</tr>
																									<tr>
																										<td width="50%"
																										    class="data-heading">
																											Total sent
																										</td>
																										<td class="data-value">
																											{$serverBackupReport.totalSent}
																										</td>
																									</tr>
																									<tr>
																										<td width="50%"
																										    class="data-heading">
																											Total received
																										</td>
																										<td class="data-value">
																											{$serverBackupReport.totalReceived}
																										</td>
																									</tr>
																								</table>
																							</td>
																						</tr>
																					</table>
																				</td>
																			</tr>
																		</table>
																	{/foreach}
																</center>
															</td>
														</tr>
													</table>
												</td>
											</tr>
											<tr>
												<td style="padding-top:20px;background-color:#ffffff;">
													Kind Regards,<br>
													Auto Rsync Backup report tool
												</td>
											</tr>
										</table>
									</td>
								</tr>
								<tr>
									<td valign="top" class="footer-cell">
										<a href="https://github.com/ivodvb/AutoRsyncBackup-Report">Auto Rsync Backup
											report on Github</a>
									</td>
								</tr>
							</table>
						</td>
					</tr>
				</table>
			</center>
		</td>
	</tr>
</table>
</body>
</html>

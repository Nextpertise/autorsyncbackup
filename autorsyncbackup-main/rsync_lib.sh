#!/bin/bash

#
# @author Teun Ouwehand (teun@nextpertise.nl)
# @company Nextpertise B.V.
# 

#
#  This file is part of autorsyncbackup.
#
#  autorsyncbackup is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  autorsyncbackup is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with autorsyncbackup. If not, see <http://www.gnu.org/licenses/>.
#

contains() {
    local n=$#
    local value=${!n}
    for ((i=1;i < $#;i++)) {
        if [ "${!i}" == "${value}" ]; then
            echo "y"
            return 0
        fi
    }
    echo "n"
    return 1
}

parseYaml() {
   local prefix=$2
   local s='[[:space:]]*' w='[a-zA-Z0-9_]*' fs=$(echo @|tr @ '\034')
   sed -ne "s|^\($s\)\($w\)$s:$s\"\(.*\)\"$s\$|\1$fs\2$fs\3|p" \
        -e "s|^\($s\)\($w\)$s:$s\(.*\)$s\$|\1$fs\2$fs\3|p"  $1 |
   awk -F$fs '{
      indent = length($1)/2;
      vname[indent] = $2;
      for (i in vname) {if (i > indent) {delete vname[i]}}
      if (length($3) > 0) {
         vn=""; for (i=0; i<indent; i++) {vn=(vn)(vname[i])("_")}
         printf("%s%s%s=\"%s\"\n", "'$prefix'",vn, $2, $3);
      }
   }'
}

setBeforeDateTime() {
  beforedatetime=$(date +%Y-%m-%d_%H:%M:%S)
  beforetimestamp=$(date +%s)
}

setAfterDateTime() {
  afterdatetime=$(date +%Y-%m-%d_%H:%M:%S)
  aftertimestamp=$(date +%s)
}

# @param backupfolder
getBackupId() {
  local retint=0
  if [ -d $1 ]; then
    for i in `ls $1`; do
      if [[ $i =~ .*_backup\.([[:digit:]]+) ]]; then
        if [[ ${BASH_REMATCH[1]} -ge $retint ]]; then
          if [ ! $(contains "${processedBackups[@]}" "${BASH_REMATCH[1]}") == "y" ]; then
            local retint=${BASH_REMATCH[1]}
          fi
        fi
      fi
    done
  fi
  echo $retint
}

rotateBackupFolders() {
  id=0
  folder=`ls -d $1/*_backup.0 2>/dev/null`
  if [[ "$?" == "0" ]]; then 
    if [ -d $folder ]; then
      # Set id=1 so the while loop actually starts
      id=1
    fi
  fi
  rotatelog=""
  processedBackups=()

  while [ $id -gt 0 ]
  do
    id=`getBackupId "$1"`
    processedBackups=( ${processedBackups[@]} $(($id+1)) )
    foldera=`ls -d $1/*_backup.$id`
    if [[ $foldera =~ ^(.*\.)[[:digit:]]+ ]]; then
      folderb="${BASH_REMATCH[1]}$((id+1))"
    fi
    # check if folder a exists
    if [ ! -d $foldera ]; then
      autorsyncbackuperror=1
      autorsyncbackuperrormsg="rotateBackupFolders: ${foldera} should exist"
      return 1
    fi
    # check if folder b does NOT exists
    if [ -d $folderb ]; then
      autorsyncbackuperror=2
      autorsyncbackuperrormsg="rotateBackupFolders: ${folderb} should NOT exist"
      return 2
    fi
    if [[ $id -ge $config_maxcycles ]]; then
      rotatelog="${rotatelog}delete: $foldera\n"
      rm -rf $foldera
    else
      rotatelog="${rotatelog}move: ${foldera} -> ${folderb}\n"
      mv $foldera $folderb
    fi
    processedBackups=(${processedBackups[@]} $id)
  done
}

createFolderZero() {
  #Timestamp used for naming directories.
  tstamp=$(date +%Y-%m-%d_%H-%M-%S)
  #This starts the naming convention. It sets the name and directory for the current backup. 
  bkdir0="$1/${tstamp}_backup.0"

  # Check if folder 0 exists
  folder=`ls -d $1/*_backup.0 2>/dev/null`
  if [[ "$?" == "0" ]]; then
    autorsyncbackuperror=3
    autorsyncbackuperrormsg="createFolderZero: Folder 0 should not exists: ${folder}"
    return 3
  fi

  # Create the directory
  mkdir $bkdir0

  # Check if folder 0 exists
  if [ ! -d $bkdir0 ] ; then
    autorsyncbackuperror=4
    autorsyncbackuperrormsg="createFolderZero: Folder 0 should exists after creating: ${folder}"
    return 4
  fi
  echo $bkdir0
}

checkBackupEnvironment() {
  if [ ! -d ${config_backupdir} ]; then
    autorsyncbackuperror=1
    autorsyncbackuperrormsg="checkBackupEnvironment: Backupdir does not exists: ${config_backupdir}"
    return 1
  fi
  
  # Add ${hostname} to ${bkdir}
  bkdir="${config_backupdir}/${config_hostname}"

  # Be sure the backup server directory exists
  mkdir -p ${bkdir}
}

checkRemoteHost() {
  # Export password for rsync
  export RSYNC_PASSWORD=${config_password}
  # Test rsync connection
  test=`rsync rsync://${config_username}@${config_hostname} &>/dev/null`
  if [[ "$?" != "0" ]]; then
    autorsyncbackuperror=5
    autorsyncbackuperrormsg="checkRemoteHost: Rsync connection error (${config_username}@${config_hostname})"
    return 5
  fi
}

getHardlinkOption() {
  # Check if folder 1 exists
  local folder=`ls -d $1/*_backup.1 2>/dev/null`
  if [[ "$?" == "0" ]]; then
    echo "--link-dest=$folder"
  fi
  echo ""
  return 0
}

readHostConfig() {
  eval $(parseYaml $jobfile "config_")
  # Check if values are set:
  # hostname
  if [[  ! "$config_hostname" ]]; then
    echo "Error: 'hostname' not set in: ${jobfile}"
    autorsyncbackuperror=6
    autorsyncbackuperrormsg="readHostConfig: 'hostname' not set in: ${jobfile}"
    return 6
  fi
  # username
  if [[  ! "$config_username" ]]; then
    echo "Error: 'username' not set in: ${jobfile}"
    autorsyncbackuperror=6
    autorsyncbackuperrormsg="readHostConfig: 'username' not set in: ${jobfile}"
    return 6
  fi
  # password
  if [[  ! "$config_password" ]]; then
    echo "Error: 'password' not set in: ${jobfile}"
    autorsyncbackuperror=6
    autorsyncbackuperrormsg="readHostConfig: 'password' not set in: ${jobfile}"
    return 6
  fi
  # share
  if [[  ! "$config_share" ]]; then
    echo "Error: 'share' not set in: ${jobfile}"
    autorsyncbackuperror=6
    autorsyncbackuperrormsg="readHostConfig: 'share' not set in: ${jobfile}"
    return 6
  fi
  if [[  ! "$config_backupdir" ]]; then
    echo "Error 'backupdir' not set in: ${jobfile}"
    autorsyncbackuperror=6
    autorsyncbackuperrormsg="readHostConfig: 'backupdir' not set in: ${jobfile}"
    return 6
  fi
  if [[  ! "$config_speedlimitkb" ]]; then
    config_speedlimitkb=0
  fi
  if [[  ! "$config_maxcycles" ]]; then
    config_maxcycles=10
  fi
}

unsetHostVariables() {
  i=0
  var="config_fileset_${i}"
  while [[  "${!var}" ]]; do
    eval config_fileset_${i}=""
    i=$(( $i + 1 ))
    var="config_fileset_${i}"
  done
  jobfile=""
  config_hostname=""
  config_password=""
  config_share=""
  config_backupdir=""
  config_speedlimitkb="0"
  config_maxcycles=10
}

generateFileset() {
  fileset=""
  i=0
  var="config_fileset_${i}"
  while [[  "${!var}" ]]; do
    fileset="$fileset rsync://${config_username}@${config_hostname}:/${config_share}/${!var}"
    i=$(( $i + 1 ))
    var="config_fileset_${i}"
  done
  if [[  ! "$fileset" ]]; then
    printf 'No fileset defined for host: %s\n' "$config_hostname"
  fi
}

generateFilesetLog() {
  filesetlog=""
  i=0
  var="config_fileset_${i}"
  while [[  "${!var}" ]]; do
    filesetlog="${filesetlog}${!var}:"
    i=$(( $i + 1 ))
    var="config_fileset_${i}"
  done
  if [[  ! "$filesetlog" ]]; then
    printf 'No fileset defined for host: %s\n' "$config_hostname"
  fi
  # remove last semicolon/character
  filesetlog=${filesetlog%?}
}

writeXmlOutput() {
  generateFilesetLog
  local logfile="$log_dir/${config_hostname}_$(date '+%s')"
  printf 'Create log file: %s\n' "$logfile"
  echo -e "<?xml version=\"1.0\"?>\n<backup>" > $logfile
  echo -e "  <jobfile>$jobfile</jobfile>" >> $logfile
  echo -e "  <hostname>$config_hostname</hostname>" >> $logfile 
  echo -e "  <username>$config_username</username>" >> $logfile
  echo -e "  <share>$config_share</share>" >> $logfile
  echo -e "  <destfolder>$bkdir</destfolder>" >> $logfile
  echo -e "  <speedlimitkb>$config_speedlimitkb</speedlimitkb>" >> $logfile
  echo -e "  <starttime>$beforedatetime</starttime>" >> $logfile
  echo -e "  <starttimestamp>$beforetimestamp</starttimestamp>" >> $logfile
  echo -e "  <endtime>$afterdatetime</endtime>" >> $logfile
  echo -e "  <endtimestamp>$aftertimestamp</endtimestamp>" >> $logfile
  echo -e "  <fileset>${filesetlog}</fileset>" >> $logfile
  echo -e "  <filesetrotate>${rotatelog}</filesetrotate>" >> $logfile
  echo -e "  <rsyncoutput>${rsyncoutput}</rsyncoutput>" >> $logfile
  echo -e "  <rsyncreturncode>${rsyncreturncode}</rsyncreturncode>" >> $logfile
  echo -e "  <autorsyncbackuperrorcode>${autorsyncbackuperror}</autorsyncbackuperrorcode>" >> $logfile
  echo -e "  <autorsyncbackuperrormsg>${autorsyncbackuperrormsg}</autorsyncbackuperrormsg>" >> $logfile
  echo -e "</backup>" >> $logfile
}

executeRsync() {
  # TODO: implement rsync dryrun for testing as -d flag.
  rsyncoutput=`rsync $hardlink --stats --bwlimit=${config_speedlimitkb} -aR --delete ${fileset} $folder 2>&1`
  rsyncreturncode=$?
}

executeJob() {
  jobfile="$@"
  autorsyncbackuperror=0
  autorsyncbackuperrormsg=""
  
  printf 'Execute job file: %s\n' "$jobfile"
  setBeforeDateTime
  readHostConfig
  checkRemoteHost
  checkBackupEnvironment
  rotateBackupFolders "${bkdir}"
  folder=`createFolderZero "${bkdir}"`
  hardlink=`getHardlinkOption "${bkdir}"`
  generateFileset
  executeRsync
  setAfterDateTime
  if [[ "$log" == "1" ]]; then
    writeXmlOutput
  fi
}

startJobs() {
  printf 'Read jobs from jobdir: %s\n' "$job_dir"
  for i in `ls $1/*.yml 2> /dev/null`; do
    if [ -f $i ]; then
      executeJob $i
      unsetHostVariables
    fi
  done
}

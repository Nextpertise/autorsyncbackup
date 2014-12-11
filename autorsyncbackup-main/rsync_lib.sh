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

# In array implementation
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

# Left and right trim spaces
trim() {
  shopt -s extglob
  local output=$1
  local output="${output##*( )}"
  local output=${output%%*( )}
  echo $output
  shopt -u extglob
}

# Parser found at pastebin.com, thank you @gron (http://pastebin.com/Pm1PcRmx)
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

# This function rotates the backup in the given folder, when number of backups is greater than maxcycles the oldest backup will be removed.
# @param $folder
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

createFolderCurrent() {
  local bkdircurrent="$1/current"

  # Create the directory
  mkdir -p ${bkdircurrent}

  # Check if folder 0 exists
  if [ ! -d ${bkdircurrent} ] ; then
    autorsyncbackuperror=4
    autorsyncbackuperrormsg="createFolderCurrent: Folder current should exists after creating: ${bkdircurrent}"
    return 1
  fi
  echo ${bkdircurrent}
}

# If rsync backup successfull, copy current to backup folder zero.
mvCurrentToZero() {
  local bkdircurrent="$1/current"
  #Timestamp used for naming directories.
  local tstamp=$(date +%Y-%m-%d_%H-%M-%S)
  #This starts the naming convention. It sets the name and directory for the current backup. 
  local bkdir0="$1/${tstamp}_backup.0"

  # Check if folder 0 exists
  folder=`ls -d $1/*_backup.0 2>/dev/null`
  if [[ "$?" == "0" ]]; then
    autorsyncbackuperror=3
    autorsyncbackuperrormsg="createFolderZero: Folder 0 should not exists: ${folder}"
    return 3
  fi
  
  # preform actual move
  mv ${bkdircurrent} ${bkdir0}
  # Check if folder 0 exists
  if [ ! -d $bkdir0 ] ; then
    autorsyncbackuperror=4
    autorsyncbackuperrormsg="createFolderZero: Folder 0 should exists after creating: ${bkdir0}"
    return 4
  fi
}

checkBackupEnvironment() {
  local ret=0
  if [ ! -d ${config_backupdir} ]; then
    autorsyncbackuperror=5
    autorsyncbackuperrormsg="checkBackupEnvironment: Backupdir does not exists: ${config_backupdir}"
    local ret=1
  else
    # Add ${hostname} to ${bkdir}
    local bkdir="${config_backupdir}/${config_hostname}"
    
    # Be sure the backup server directory exists
    mkdir -p ${bkdir} &>/dev/null
    if [[ "$?" != "0" ]]; then
      autorsyncbackuperror=6
      autorsyncbackuperrormsg="checkBackupEnvironment: Can't create directory: ${bkdir}"
      local ret=1
    else
      echo "${bkdir}"
    fi 
  fi
  return $ret
}

checkRemoteHost() {
  local ret=0
  # Export password for rsync
  export RSYNC_PASSWORD=${config_password}
  # Test rsync connection
  rsync --contimeout=5 rsync://${config_username}@${config_hostname} &>/dev/null
  if [[ "$?" != "0" ]]; then
    autorsyncbackuperror=7
    autorsyncbackuperrormsg="checkRemoteHost: Rsync connection error (${config_username}@${config_hostname})"
    local ret=1
  fi
  return $ret
}

getHardlinkOption() {
  # Check if folder 1 exists
  folder=`ls -d $1/*_backup.0 2>/dev/null`
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
  config_hostname=`trim "$config_hostname"`
  if [[  ! "$config_hostname" ]]; then
    echo "Error: 'hostname' not set in: ${jobfile}"
    autorsyncbackuperror=8
    autorsyncbackuperrormsg="readHostConfig: 'hostname' not set in: ${jobfile}"
    return 6
  fi
  # username
  config_username=`trim "$config_username"`
  if [[  ! "$config_username" ]]; then
    echo "Error: 'username' not set in: ${jobfile}"
    autorsyncbackuperror=8
    autorsyncbackuperrormsg="readHostConfig: 'username' not set in: ${jobfile}"
    return 6
  fi
  # password
  config_password=`trim "$config_password"`
  if [[  ! "$config_password" ]]; then
    echo "Error: 'password' not set in: ${jobfile}"
    autorsyncbackuperror=8
    autorsyncbackuperrormsg="readHostConfig: 'password' not set in: ${jobfile}"
    return 6
  fi
  # share
  config_share=`trim "$config_share"`
  if [[  ! "$config_share" ]]; then
    echo "Error: 'share' not set in: ${jobfile}"
    autorsyncbackuperror=8
    autorsyncbackuperrormsg="readHostConfig: 'share' not set in: ${jobfile}"
    return 6
  fi
  config_backupdir=`trim "$config_backupdir"`
  if [[  ! "$config_backupdir" ]]; then
    echo "Error 'backupdir' not set in: ${jobfile}"
    autorsyncbackuperror=8
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
  local folder=$1
  rsyncoutput=`rsync --contimeout=5 $hardlink --stats --bwlimit=${config_speedlimitkb} -aR --delete ${fileset} $folder 2>&1`
  rsyncreturncode=$?
  
  # Return code 23, could be a warning about directories/files in fileset which doesn't exists
  if [[ "$?" == "23" ]]; then
    rsyncreturncode=0
  fi
  # Return code 24, isn't an error, it's a warning about vanished files. Normal behaviour for example tmp files in large backups
  if [[ "$?" == "24" ]]; then
    rsyncreturncode=0
  fi
  
  return ${rsyncreturncode}
}

executeJob() {
  jobfile=$1
  rsyncreturncode=9
  rsyncoutput="Rsync was never invoked"
  autorsyncbackuperror=0
  autorsyncbackuperrormsg=""
  printf 'Execute job file: %s\n' "$jobfile"
  setBeforeDateTime
  readHostConfig
  checkRemoteHost
  if [[ "$?" == "0" ]]; then
    bkdir=`checkBackupEnvironment`
    if [[ "$?" == "0" ]]; then
      folder=`createFolderCurrent "${bkdir}"`
      if [[ "$?" == "0" ]]; then
        hardlink=`getHardlinkOption "${bkdir}"`
        generateFileset
        executeRsync "$folder"
        if [[ "$?" == "0" ]]; then
          rotateBackupFolders "${bkdir}"
          mvCurrentToZero "${bkdir}"
        fi
      fi
    fi
  fi
  setAfterDateTime
  if [[ "$log" == "1" ]]; then
    writeXmlOutput
  fi
}

startJobs() {
  printf 'Read jobs from jobdir: %s\n' "$job_dir"
  for i in `ls $1/*.job 2> /dev/null`; do
    if [ -f $i ]; then
      executeJob "$i"
      unsetHostVariables
    fi
  done
}

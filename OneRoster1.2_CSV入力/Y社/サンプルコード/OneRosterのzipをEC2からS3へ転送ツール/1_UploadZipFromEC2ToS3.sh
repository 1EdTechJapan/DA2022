#!/usr/bin/bash
s3path="s3://mpoc-opeid-dev-common-s3-api-1/oneroster/zip/"
zippath="/home/scp-user/one_roster_zip"

if [ ! -d "./log" ]; then
    mkdir "./log"
fi
logfile="./log/"$(date +%Y%m%d)".log"
touch  $logfile
#start log echo date 
startstr=$(date)" start"
echo $startstr >> $logfile
filelist=`ls $zippath/RO_*.zip 2> /dev/null`
RET=$?
# if no file, just return
if [ $RET != 0 ]; then
    nofilestr=$(date)" end with no file"
        echo $nofilestr >> $logfile
      exit
fi
#echo $filelist >> $logfile
for fileName in $filelist ; do
    #check s3 command
    aws s3 cp $fileName $s3path --no-verify-ssl 2>> $logfile
    RET=$?
    # if failed, just return
    if [ $RET != 0 ]; then
        echo $fileName"failed" >>$logfile
     else
         # if sucess delete file
         echo  "$fileName has been s3" >> $logfile
         rm -f $fileName
    fi
done
 #log
 echo "upload success!" >>  $logfile
 endstr=$(date)" end"
 echo $endstr >> $logfile

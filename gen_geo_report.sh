#/bin/bash

# Usage
if [ "$1" == "-h" ] || [ "$1" == "-help" ]; then
	echo "[INFO] ***** Usage *****"
	echo "Daily report : $0 <YYYYMMDD>"
	echo "Monthly report : $0 <YYYYMM>"
	echo "Default date : `date '+%Y%m%d'`"
	exit 0
elif [[ "$1" =~ [0-9]{6} ]] || [[ "$1" =~  [0-9]{4} ]]; then
	T_DATE="$1"
else
	T_DATE="`date '+%Y%m%d'`"
fi


# local variables
RPT_NAME=""
RPT_DIR=./report
GEO_RPT_PATH=$RPT_DIR/geo_distruption_rpt_$T_DATE.csv
TMP_DIR=./tmp
RAW_DATA_PATH=./data/47.88.153.124
EXT_DATA=$TMP_DIR/ip_list_$T_DATE.txt
SLEEP_SEC=60


##### extRawData #####
extRawData(){

		V_BOOL=`ls -ltr $RAW_DATA_PATH | egrep $T_DATE | wc -l`;
		if [ $V_BOOL -eq 0 ]; then

			echo "*****[ERROR] No data in $RAW_DATA_PATH/$T_DATE being found, script exists...*****"
			exit 0

		fi

		cat $RAW_DATA_PATH/*$T_DATE* | egrep \'8 | egrep ping | awk '{print $3",", $8,$9, $13, "ms"}' | sort | uniq > $EXT_DATA
		[ ! -r $EXT_DATA ] && echo "[ERROR] $EXT_DATA could not be generated, script exits ...*****!" && exit 0

	return 1
}


#2. Generate the Geo-Summary report
genGeoSummary(){


		estTime=$((`cat $EXT_DATA | awk '{print $1}' | sort | uniq | wc -l` / 145 * 60 ))

		[ $estTime -le 60 ] && echo "[INFO] Start to generate the $GEO_RPT_PATH, it will take around 60 seconds ..."
		[ $estTime -gt 60 ] && echo "[INFO] Start to generate the $GEO_RPT_PATH, it will take around $((estTime / 60)) minutes ..."
		while true; do sleep 15; echo -n '.'; done &
		tPID=$!
 		(c=0; for i in `cat $EXT_DATA | awk -F, '{print $1}' | sort | uniq`; do c=$((c+1)); [ $((c % 145)) -eq 0 ] && sleep $SLEEP_SEC; echo "$i, `curl -s http://ip-api.com/csv/$i?lang=zh-CN`" ;  done) > $TMP_DIR/temp.txt
		echo ""
		pkill -P $!

		echo "Region, Count" > $GEO_RPT_PATH
		cat $TMP_DIR/temp.txt | awk -F, ' $6 != "" {print $6}' | sort | uniq -c | sort -nr | awk '{ a=""; for ( i=2; i<=NF; i++ ) {a=a" "$i} print a",", $1 }' >> $GEO_RPT_PATH
		rm $TMP_DIR/temp.txt

		[ ! -r $GEO_RPT_PATH ] && echo "[ERROR] $GEO_RPT_PATH could not be generated, script exits ...*****!" && exit 0
		[ -r $GEO_RPT_PATH ] && echo "[INFO] $GEO_RPT_PATH has been generated ...!"


		# Generate Latency Report of top 20 slowest IP
		echo "[INFO] Waiting for $SLEEP_SEC seconds"
		sleep $SLEEP_SEC;
		cat $EXT_DATA | sort -nr -k4 | head -20 | awk -F, '{print $1}' | xargs -I {} echo "echo {}, \`curl -s http://ip-api.com/csv/{}?lang=zh-CN\`;"  | bash > $TMP_DIR/temp.txt

		echo "Connections with Slowest Ping Latency" > $RPT_DIR/highest_latency_rpt_$T_DATE.csv
		echo "IP, Location, DC Name, Latency(mc)" >> $RPT_DIR/highest_latency_rpt_$T_DATE.csv

		echo -n "[INFO] Generating the Latency Report ..."
		c=0
		for i in `cat $EXT_DATA | sort -nr -k4 | head -20 | awk -F, '{print $1}'`; do


			dcName="`cat $EXT_DATA |  sort -nr -k4 | egrep -w $i | head -1 | awk -F, '{print $2}'`";
			latencyStat="`cat $EXT_DATA |  sort -nr -k4 | egrep -w $i | head -1 | awk -F, '{print $3}'`";
			tRegion="`curl -s http://ip-api.com/csv/$i?lang=zh-CN | awk -F, '{print $5,$6}'`"

			echo "$i,$tRegion, $dcName, $latencyStat" >> $RPT_DIR/highest_latency_rpt_$T_DATE.csv

			c=$((c+1));
			[ $((c % 145)) -eq 0 ] && sleep $SLEEP_SEC;
			echo -n "."
			done
			echo ""

		[ ! -r $RPT_DIR/highest_latency_rpt_$T_DATE.csv ] && echo "[ERROR] $$RPT_DIR/highest_latency_rpt_$T_DATE.csv could not be generated, script exits ...*****!" && exit 0
		[ -r $RPT_DIR/highest_latency_rpt_$T_DATE.csv ] && echo "[INFO] $$RPT_DIR/highest_latency_rpt_$T_DATE.csv has been generated ...!"


		rm $TMP_DIR/temp.txt
		#rm $TMP_DIR/temp_2.txt
	return 1
}

# clean up on exit
finish(){
	kill $(jobs -pr)
	exit 0
}







##### main #####

# clean up on exit
trap finish SIGINT SIGTERM EXIT

#0 check the INI dir & print the target report date
[ ! -d $RPT_DIR ] && mkdir $RPT_DIR
[ ! -d $TMP_DIR ] && mkdir $TMP_DIR
echo "[INFO] Target report date : $T_DATE"



#1. Extract the IP & ms from the ram data
extRawData

#2. Generate the Geo-Summary & highest ping latency report
genGeoSummary


#!/bin/bash

# TODO: Generate controller like symbols another way
# TODO; How to generate this logic gatter stuff?

. config
. $SCRIPT_DIR/tools.sh

#rm -rf $FOOTPRINT_PATH
#mkdir $FOOTPRINT_PATH

for CSV_FILE in $DATA_DIR/device/*.csv
do
	if [ -f $CSV_FILE ]
	then
		echo "File: $CSV_FILE"

		LIBRARY_NAME=$(basename -s .csv "$CSV_FILE")
		echo "Library name: $LIBRARY_NAME"
		echo
	#	mkdir $SYMBOL_DIR/$LIBRARY_NAME

		COLUMN=()
		SYMBOL_COUNT=0
		ERROR_COUNT=0
		FIRST_LINE=1

		LEFT=()
		RIGHT=()
		TOP=()
		BOTTOM=()
		MAX_TEXT=0

		while read -r LINE && [[ -n $LINE ]]
		do
			if [ $FIRST_LINE -ne "1" ]
			then
				eval "declare -a DATA=($(echo $LINE | awk -v FPAT='[^,]*|(\"[^\"]+\")' '{ for (i = 1; i <= NF; i++) { gsub("^\"|\"$","",$i); printf("\"%s\" ", $i) } }'))"
		
				if [ $MAX_TEXT -lt ${#DATA[$COLUMN_NAME]} ]
				then
					MAX_TEXT=${#DATA[$COLUMN_NAME]}
				fi

				case "${DATA[$COLUMN_DIRECTION]}" in
					left)
						LEFT=("${LEFT[@]}" "${DATA[$COLUMN_NAME]} ${DATA[$COLUMN_PIN]} ${DATA[$COLUMN_TYPE]}")
						;;
					right)
						RIGHT=("${RIGHT[@]}" "${DATA[$COLUMN_NAME]} ${DATA[$COLUMN_PIN]} ${DATA[$COLUMN_TYPE]}")
						;;
					top)
						TOP=("${TOP[@]}" "${DATA[$COLUMN_NAME]} ${DATA[$COLUMN_PIN]} ${DATA[$COLUMN_TYPE]}")
						;;
					bottom)
						BOTTOM=("${BOTTOM[@]}" "${DATA[$COLUMN_NAME]} ${DATA[$COLUMN_PIN]} ${DATA[$COLUMN_TYPE]}")
						;;
				esac

			#	SYMBOL=${DATA[0]}
			#	SYMBOL_FILE=$DATA_DIR/$SYMBOL.lib
			#	SYM=$(head -n -2 $SYMBOL_FILE | tail -n +3 -)

			#	echo ${DATA[0]} ${DATA[1]} ${DATA[2]} ${DATA[3]}

			#	INDEX=0
			#	for COL in ${COLUMN[*]}
			#	do
			#		echo ${COL^^*} $INDEX ${DATA[$INDEX]}
			#		SYM="${SYM//\$${COL^^*}/${DATA[$INDEX]}}"
			#		INDEX=$((INDEX+1))
			#	done
			#	echo "$SYM"

			# TODO: Generate meta file with description and keywords!

			else
				eval "declare -a COLUMN=($(echo $LINE | awk -v FPAT='[^,]*|(\"[^\"]+\")' '{ for (i = 1; i <= NF; i++) { gsub("^\"|\"$","",$i); printf("\"%s\" ", $i) } }'))"

				INDEX=0
				for COL in ${COLUMN[*]}
				do
					eval "COLUMN_${COL^^*}=$INDEX"
					INDEX=$((INDEX+1))
				done
			fi
			FIRST_LINE=0
		done < $CSV_FILE

#SYMBOL_LINE_WIDTH=20
#SYMBOL_PIN_LENGTH=100
#SYMBOL_PIN_DISTANCE=50
#SYMBOL_PIN_SPACE=100
#SYMBOL_PIN_NAME_SIZE=50
#SYMBOL_PIN_NUMBER_SIZE=50

		echo "$SYMBOL_LIB_START"
		echo "#"
		echo "# ${LIBRARY_NAME^^*}"
		echo "#"

# DEF $NAME #PWR 0 0 Y Y 1 F P
#F0 "#PWR" 0 50 60 H I C CNN
#F1 "$NAME" 0 -150 60 H V C CNN
#F2 "" 0 0 60 H V C CNN
#F3 "" 0 0 60 H V C CNN

		HEIGHT=${#LEFT[*]}
		if [ $HEIGHT -lt ${#RIGHT[*]} ]
		then
			HEIGHT=${#RIGHT[*]}
		fi

		echo $HEIGHT
		if [ $((HEIGHT%2)) -eq 0 ]
		then
			echo "even";
		else
			echo "odd";
		fi

	#		HEIGHT=$(gawk "BEGIN { printf(\"%d\n\", ((${#RIGHT[*]} / 2) + 1) * $SYMBOL_PIN_DISTANCE + $SYMBOL_PIN_SPACE ) }")
	#	else
	#		HEIGHT=$(gawk "BEGIN { printf(\"%d\n\", ((${#LEFT[*]} / 2) + 1) * $SYMBOL_PIN_DISTANCE + $SYMBOL_PIN_SPACE ) }")
	#	fi
		WIDTH=$(gawk "BEGIN { printf(\"%d\n\", ($MAX_TEXT + 1) * $SYMBOL_PIN_NAME_SIZE ) }")

		echo "DRAW"
		echo "S -$WIDTH $HEIGHT $WIDTH -$HEIGHT 0 1 $SYMBOL_LINE_WIDTH f"

		POSY=$HEIGHT
		POSY=$((POSY - $SYMBOL_PIN_SPACE))
		POSX=$((WIDTH + $SYMBOL_PIN_LENGTH))
		for ROW in "${LEFT[@]}"
		do
			ITEM=($ROW)
			if [ ${ITEM[0]} != "-" ]
			then
				echo "X ${ITEM[0]} ${ITEM[1]} -$POSX $POSY $SYMBOL_PIN_LENGTH R $SYMBOL_PIN_NAME_SIZE $SYMBOL_PIN_NUMBER_SIZE 1 1 U"
			fi
			POSY=$((POSY - $SYMBOL_PIN_DISTANCE))
		done

		INDEX=0
		POSY=$HEIGHT
		POSY=$((POSY - $SYMBOL_PIN_SPACE))
		for ROW in "${RIGHT[@]}"
		do
			ITEM=($ROW)
			if [ ${ITEM[0]} != "-" ]
			then
				echo "X ${ITEM[0]} ${ITEM[1]} $POSX $POSY $SYMBOL_PIN_LENGTH L $SYMBOL_PIN_NAME_SIZE $SYMBOL_PIN_NUMBER_SIZE 1 1 U"
			else
				ITEM_LEFT=(${LEFT[$INDEX]})
				if [ ${ITEM_LEFT[0]} == "-" ]
				then
					echo "P 2 0 1 $SYMBOL_LINE_WIDTH -$POSX $POSY $POSX $POSY N"
				fi
			fi
			POSY=$((POSY - $SYMBOL_PIN_DISTANCE))
			INDEX=$((INDEX + 1))
		done

		echo "ENDDRAW"
		echo "ENDDEF"

#		echo $HEIGHT
#		echo $WIDTH
#		echo ${#LEFT[*]}
#		echo ${#RIGHT[*]}
#		echo ${#TOP[*]}
#		echo ${#BOTTOM[*]}
		
#		for PIN in "${LEFT[@]}"
#		do
#		#	echo $PIN
#		done

		echo "$SYMBOL_LIB_END"
	fi
done

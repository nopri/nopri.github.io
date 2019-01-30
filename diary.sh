#!/bin/sh

PROGNAME="diary"
VERSION="0.2a"
COPYRIGHT="$PROGNAME $VERSION, (c) Noprianto, 2003-2007. GPL."
KEYGUIDE="Use TAB and arrows to move. Also use vi style navigation: h j k l to move around days"
DIARYDIR=~/temp/DIARY
VISITED="[visited]"

alias dialog="dialog --backtitle \"$COPYRIGHT\""
TEMP=$DIARYDIR/TMP/$$.diary


function del()
{
	rm -rf $TEMP
}

function checkDeps()
{
	if [ -z $EDITOR ]
	then
		w_vi=$(which vi)
		if [ -z $w_vi ]
		then
			echo "I cant find text editor. Sorry. Please update your EDITOR variable , if you don't have vi."
			exit 1
		else
			export DEDITOR=vi
		fi
	else
		export DEDITOR=$EDITOR
	fi
	
	w_dialog=$(which dialog)
	if [ -z $w_dialog ]
	then
		echo "I cant find dialog. Sorry."
		exit 1
	fi

	w_basename=$(which basename)
	if [ -z $w_basename ]
	then
		echo "I cant find basename. Sorry."
		exit 1
	fi


	w_tput=$(which tput)
	if [ -z $w_tput ]
	then
		echo "I cant find tput. Sorry."
		exit 1
	fi
	
	test ! -d $DIARYDIR && mkdir -p $DIARYDIR
	test ! -d $(dirname $TEMP) && mkdir $(dirname $TEMP)
	chmod go-rwx $DIARYDIR
}

checkDeps

while [ 1 ]
do
	dialog --menu "Choose action" 14 60 6 edit "Create new or view or edit diary"\
		list "List all diaries" search "Search diary" delete "Delete diary" \
		editall "View or edit all diaries one by one" \
		killall "Delete all diaries" 2>$TEMP
	test $? -ne 0 && break
	TODO=`cat $TEMP` && del

	case $TODO in
	edit)	dialog --calendar "$PROGNAME: $KEYGUIDE" 10 40 2>$TEMP
		test $? -ne 0 && continue
		DATE=`cat $TEMP` && del
		DATE=$(echo $DATE | sed -e 's/\//-/g')
		echo -n "$(date +%T) " >> $DIARYDIR/$DATE
		cp $DIARYDIR/$DATE $TEMP
		$DEDITOR  $DIARYDIR/$DATE
		DIFF=$(diff $TEMP $DIARYDIR/$DATE) &&  del
		test -z $DIFF && echo $VISITED >> $DIARYDIR/$DATE
		;;
	delete)	dialog --calendar "$PROGNAME: $KEYGUIDE" 10 40 2>$TEMP
		test $? -ne 0 && continue
		DATE=`cat $TEMP` && del
		DATE=$(echo $DATE | sed -e 's/\//-/g')
		unalias rm
		rm  $DIARYDIR/$DATE	
		if [ $? -eq 0 ]
		then
			dialog --msgbox "diary for $DATE deleted succesfully" 10 40
		else
			dialog --msgbox "diary for $DATE couldnot be deleted" 10 40
		fi
		;;
	list)	echo "Diaries:" > $TEMP
		for i in $(ls $DIARYDIR/)
		do
			test -f $DIARYDIR/$i && echo $i >> $TEMP
		done
		dialog --textbox $TEMP 20 40 
		del
		;;
	
	search) dialog --inputbox "search keyword" 10 40 2> $TEMP
		SEARCH=`cat $TEMP` 
		del
		echo "Diaries contain $SEARCH:" > $TEMP
		#grep $SEARCH -i $DIARYDIR -r | cut -d\/ -f2 | cut -d: -f1 | uniq >> $TEMP
		grep $SEARCH -i $DIARYDIR -r | xargs -i basename '{}' | cut -d: -f1 | uniq >> $TEMP
		dialog --textbox $TEMP 20 40 
		del
		;;	
	editall)for i in $(ls $DIARYDIR)
		do
			test -f $DIARYDIR/$i && $DEDITOR $DIARYDIR/$i
		done
		;;
	killall)dialog --yesno Sure? 10 40
		if [ $? -eq 0 ]
		then
			rm -rf $DIARYDIR
			test $? -eq 0 && dialog --msgbox "All killed. All !" 10 40
			mkdir $DIARYDIR
			chmod go-rwx $DIARYDIR
		else
			dialog --msgbox "Abandoned" 10 40
		fi
		;;
	esac	
	del	
done
chmod go-rwx $DIARYDIR
del
tput reset


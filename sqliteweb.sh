#!/bin/sh

#
# license
####################################################################
#
# 	sqliteweb 
#	Copyright (c) 2005, Noprianto
#	All rights reserved.
#
#	Redistribution and use in source and binary forms, with or without 
#	modification, are permitted provided that the following conditions are met:
#
#	- Redistributions of source code must retain the above copyright notice, 
#	  this list of conditions and the following disclaimer.
#
#	- Redistributions in binary form must reproduce the above copyright 
#	  notice, this list of conditions and the following disclaimer in the 
#	  documentation and/or other materials provided with the distribution.
#
#	- Neither the name of the Noprianto nor the names of its 
#	  contributors may be used to endorse or promote products derived from 
#	  this software without specific prior written permission. 
#
#	THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND 
#	CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED 
#	WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
#	WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
#	PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL 
#	THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY 
#	DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
#	CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
#	PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF 
#	USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
#	CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
#	CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING 
#	NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE 
#	USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY 
#	OF SUCH DAMAGE.
#


#
# changelog
####################################################################
#
# 0.1 (apprx. 22 july 2005): 
# - initial release
#
# 0.2 (30 july 2005):
# - add insert into table
#
# 0.3 (30 july 2005):
# - add delete from table
#
# 0.4 (31 july 2005):
# - add simple url encoding/decoding
# - fix filename on database creating, replace space with _ 
# - fix filename on database rename and delete
#
# bug:
# - when creating database, cannot handle space in filename, so will replace space with _
# - might be in url encoding/decoding function
#
# todo:
# - implement SQL 
# - optimize code
# - add error code 
#



#
# configurations
####################################################################
#
_config()
{
	SQLITE_BINARY="/usr/bin/sqlite3"


	DB_PATH="/tmp"
	DB_EXT="*.db"

}



#
# internal functions
####################################################################
_program_info()
{
	PROGRAM_NAME="sqliteweb"
	PROGRAM_VERSION="0.4"
	PROGRAM_LICENSE="BSD"
	PROGRAM_COPYRIGHT="Noprianto, 2005"
}

_check_prereq()
{
	_config
	ERRSTR=""
	test ! -x $SQLITE_BINARY && ERRSTR="$ERRSTR<BR>Cannot locate SQLITE binary" 
	test ! -r $DB_PATH && ERRSTR="$ERRSTR<BR>Database directory cannot be read"
	test -z $ERRSTR && return 0 || return 1 
}


_cgi_header()
{
	echo Content-type: text/html
	echo
	echo 
}

_html_header()
{
	echo "
	<HTML>
	<HEAD>
	<TITLE>
	$PROGRAM_NAME version $PROGRAM_VERSION
	</TITLE>
	<STYLE TYPE='text/css'>
	<!--

	BODY
	{
		font-family: Arial, Verdana;
	}

	TABLE
	{
		border: 1px solid black;
	}

	TABLE TD
	{
		border: 1px solid black;
	}

	TABLE TH
	{
		border: 1px solid black;
		background: lightgrey;
	}

	.full
	{
		width: 100%;
	}

	.error
	{
		background: red;
	}


	.noborder
	{
		border: 0px;
	}

	A
	{
		text-decoration: underline;
		color: black;
	}

	A:visited
	{
		text-decoration: underline;
		color: black;
	}

	A:hover
	{
		background: lightgrey;
	}

	-->
	</STYLE>
	</HEAD>
	<BODY>
	"
}

_html_footer()
{
	echo "
	</BODY>
	</HTML>
	"
} 

_print_server_info()
{
	echo "
	<TABLE class='full'>
	<CAPTION>Server information</CAPTION>
	<TH>Variable</TH><TH>Value</TH>
	<TR>
	<TD>SERVER_SOFTWARE</TD><TD>$SERVER_SOFTWARE</TD>
	</TR>

	<TR>
	<TD>SERVER_NAME</TD><TD>$SERVER_NAME</TD>
	</TR>

	<TR>
	<TD>SERVER_PROTOCOL</TD><TD>$SERVER_PROTOCOL</TD>
	</TR>

	<TR>
	<TD>SERVER_PORT</TD><TD>$SERVER_PORT</TD>
	</TR>

	<TR>
	<TD>REQUEST_METHOD</TD><TD>$REQUEST_METHOD</TD>
	</TR>

	<TR>
	<TD>GATEWAY_INTERFACE</TD><TD>$GATEWAY_INTERFACE</TD>
	</TR>

	<TR>
	<TD>PATH_INFO</TD><TD>$PATH_INFO</TD>
	</TR>

	<TR>
	<TD>PATH_TRANSLATED</TD><TD>$PATH_TRANSLATED</TD>
	</TR>

	<TR>
	<TD>REMOTE_HOST</TD><TD>$REMOTE_HOST</TD>
	</TR>

	<TR>
	<TD>REMOTE_ADDR</TD><TD>$REMOTE_ADDR</TD>
	</TR>

	<TR>
	<TD>REMOTE_IDENT</TD><TD>$REMOTE_IDENT</TD>
	</TR>

	<TR>
	<TD>SCRIPT_NAME</TD><TD>$SCRIPT_NAME</TD>
	</TR>

	<TR>
	<TD>QUERY_STRING</TD><TD>$QUERY_STRING</TD>
	</TR>

	<TR>
	<TD>CONTENT_TYPE</TD>$CONTENT_TYPE<TD></TD>
	</TR>

	<TR>
	<TD>CONTENT_LENGTH</TD><TD>$CONTENT_LENGTH</TD>
	</TR>
	</TABLE>
	"
}

_simple_urlencode()
{
	ret="$1"
	ret=`echo $ret | sed -e 's/%/%25/ig'  -e 's/ /%20/ig' -e 's/!/%21/ig' -e 's/"/%22/ig' -e 's/#/%23/ig' -e 's/\\$/%24/ig' -e 's/&/%26/ig' -e "s/'/%27/ig" \
		-e 's/(/%28/ig' -e 's/)/%29/ig' -e 's/*/%2A/ig' -e 's/+/%2B/ig' -e 's/,/%2C/ig' -e 's/-/%2D/ig' -e 's/\./%2E/ig' -e 's/\//%2F/ig' \
		-e 's/:/%3A/ig' -e 's/;/%3B/ig' -e 's/</%3C/ig' -e 's/=/%3D/ig' -e 's/>/%3E/ig' -e 's/?/%3F/ig' -e 's/@/%40/ig' -e 's/\[/%5B/ig' \
		-e 's/\\\/%5C/ig' -e 's/\]/%5D/ig' -e 's/\^/%5E/ig' -e 's/_/%5F/ig' -e 's/\`/%60/ig' -e 's/{/%7B/ig' -e 's/|/%7C/ig' -e 's/|/%7D/ig' \
		-e 's/~/%7E/ig' -e 's/&127;/%7F/ig'`
	echo $ret
}

_simple_urldecode()
{
	ret="$1"
	ret=`echo $ret | sed -e 's/%5C/\\\/ig' -e 's/%20/ /ig' -e 's/%21/!/ig' -e 's/%22/"/ig' -e 's/%23/#/ig' -e 's/%24/$/ig' -e 's/%25/%/ig' -e 's/%26/\&/ig' \
		-e "s/%27/'/ig" -e 's/%28/(/ig' -e 's/%29/)/ig' -e 's/%2A/*/ig' -e 's/%2B/+/ig' -e 's/%2C/,/ig' -e 's/%2D/-/ig' -e 's/%2E/./ig' \
		-e 's/%2F/\//ig' -e 's/%3A/:/ig' -e 's/%3B/;/ig' -e 's/%3C/</ig' -e 's/%3D/=/ig' -e 's/%3E/>/ig' -e 's/%3F/?/ig' -e 's/%40/@/ig' \
		-e 's/%5B/\[/ig' -e 's/%5D/\]/ig' -e 's/%5E/^/ig' -e 's/%5F/_/ig' -e 's/%60/\`/ig' -e 's/%7B/{/ig' -e 's/%7C/|/ig' -e 's/%7D/}/ig' \
		-e 's/%7E/~/ig' -e 's/%7F/&127;/ig' -e 's/+/ /ig'`
	echo $ret
}

#
# public functions
####################################################################
print_doc()
{
	echo "
<PRE>
$PROGRAM_NAME version $PROGRAM_VERSION
Copyright $PROGRAM_COPYRIGHT
Licensed under $PROGRAM_LICENSE

Features:
- DB
  - create
  - delete
  - rename
  - browse
- Table
  - create
  - drop
  - browse
  - insert into
  - delete from

Usage: 
- Use menu above to navigate

Installation:
- Make sure GNU coreutils and sed are installed (should be)
- Setup your web server
- Copy this software to your cgi-bin directory
- Create directory (to store databases, default: /tmp) readable/writeable by user who run web server
- Additionally, please change variable in _config function
- That's all.

Tools used:
- Shell script: BASH
- GNU Coreutils:
  - test
  - pwd
  - ls
  - wc
  - cut
  - rm
  - mv
  - touch
  - seq 
- sed

</PRE>
	"
}


print_errmsg()
{
	if [ ! -z "$1" ]
	then
		echo "
		<TABLE class='full'>
		<TR class='error'>
		<TD><B>ERROR</B></TD>
		</TR>
		<TR>
		<TD>$1</TD>
		</TR>
		</TABLE>
		"
		
	fi
}

show_menu()
{
	TASK="$PATH_INFO$QUERY_STRING"
	test -z $TASK && TASK=home
	TASK_MAIN=`echo $TASK | cut -d/ -f2`
	TASK_DETAIL=`echo $TASK | cut -d/ -f3`

	MENU="home browse create"
	echo "
	<TABLE class='full'>
	<TR>
	"
	for i in $MENU
	do
		bgcolor=""
		if [ $TASK_MAIN == $i ]
		then
			bgcolor="bgcolor='lightgrey'"
		fi
		echo "<TD align='center' $bgcolor ><A href='$SCRIPT_NAME/$i'>$i</A></TD>"
	done
	echo "
	</TR>
	</TABLE>
	"
}


go_home()
{
	print_doc
}


go_browse()
{
	if [ -z "$1" ]
	then
		OLDPWD=`pwd`

		DB_NUM=0
		cd $DB_PATH
		ls $DB_EXT 1>/dev/null 2>&1

		if [ $? -eq 0 ]	
		then
			DB_NUM=`ls -l $DB_EXT | wc -l | tr -d [[:space:]]`
		fi

		echo "<BR>Found $DB_NUM database(s) in $DB_PATH"

		echo "<TABLE class='full'>"
		echo "<TH>database</TH><TH>browse</TH><TH>rename</TH><TH>delete</TH>"
		for i in `ls $DB_EXT`
		do
			echo "<TR>"
			echo "<TD>$i</TD>"
			echo "<TD><A href='$SCRIPT_NAME/browse/$i'>browse</A></TD>"
			echo "<TD><A href='$SCRIPT_NAME/rename/$i'>rename</a></TD>"
			echo "<TD><A href='$SCRIPT_NAME/delete/$i'>delete</a></TD>"
			echo "</TR>"
		done
		echo "</TABLE>"
	 
		cd $OLDPWD	
	else
		echo "<BR>"
		echo Browse database "<B>$1</B><BR><BR>"

		OLDPWD=`pwd`
		cd $DB_PATH
		TABLES=`$SQLITE_BINARY $1 .tables`

		
		echo "<A href='$SCRIPT_NAME/add_table/$1'>Add table</A>"
		echo "<TABLE class='full'>"
		echo "<TH>table</TH><TH>browse</TH><TH>drop</TH><TH>insert</TH>"
		for i in $TABLES
		do
			echo "<TR>"
			echo "<TD>$i</TD>"
			echo "<TD><A href='$SCRIPT_NAME/browse_table/$1/$i'>browse</A></TD>"
			echo "<TD><A href='$SCRIPT_NAME/drop_table/$1/$i'>drop</a></TD>"
			echo "<TD><A href='$SCRIPT_NAME/insert_table/$1/$i'>insert</a></TD>"
			echo "</TR>"
		done
		echo "</TABLE>"

		cd $OLDPWD
	fi
}

go_delete()
{
	if [ ! -z "$1" ]
	then
		echo "<BR>Delete database <B>$1</B><BR><BR>"
		OLDPWD=`pwd`
		cd $DB_PATH
		DB_DEL="$1"
		DB_DEL=$(_simple_urldecode "$DB_DEL")	
		DB_DEL=`echo "$DB_DEL" | tr ' ' '_'`
		rm -f "$DB_DEL"
		if [ $? -eq 0 ]
		then
			echo "Status: Database deleted successfully"
		else
			echo "Status: Failed to delete database (error code: $?)"
		fi
		cd $OLDPWD
	fi	 
}

go_rename()
{
	if [ ! -z "$1" ]
	then
		echo "<BR>Rename database <B>$1</B><BR><BR>"
		echo "
		<FORM action='$SCRIPT_NAME/rename_action/$1/' method='get'>
		<TABLE class='noborder'>
		<TR>
		<TD class='noborder'>New database name</TD>
		<TD class='noborder'><INPUT type='text' name='new_name'></TD>
		<TD class='noborder'><INPUT type='submit' value='rename'></TD>
		</TR>	
		</TABLE>
		</FORM>
		"
	fi	 
}


go_rename_action()
{
	if [ ! -z "$1" ] && [ ! -z "$2" ]
	then
		OLD_NAME=$1
		OLD_NAME=$(_simple_urldecode "$OLD_NAME")	
		OLD_NAME=`echo "$OLD_NAME" | tr ' ' '_'`
		NEW_NAME=`echo $2 | cut -d= -f2`	
		NEW_NAME=$(_simple_urldecode "$NEW_NAME")	
		NEW_NAME=`echo "$NEW_NAME" | tr ' ' '_'`
		echo "<BR>Rename database from <B>$OLD_NAME</B> to <B>$NEW_NAME</B><BR><BR>"
		echo "Note: space in name will be replaced with _ (underscore)<BR><BR>"
		OLDPWD=`pwd`
		cd $DB_PATH
		mv $OLD_NAME $NEW_NAME
		if [ $? -eq 0 ]
		then
			echo "Status: Database renamed successfully"
		else
			echo "Status: Failed to rename database (error code: $?)"
		fi
		cd $OLDPWD
	fi
}

go_create()
{
	if [ -z "$1" ]
	then
	
		echo "<BR>Create new database<BR><BR>"
		echo "
		<FORM action='$SCRIPT_NAME/create/' method='get'>
		<TABLE class='noborder'>
		<TR>
		<TD class='noborder'>Database name</TD>
		<TD class='noborder'><INPUT type='text' name='db'></TD>
		<TD class='noborder'><INPUT type='submit' value='create'></TD>
		</TR>	
		</TABLE>
		</FORM>
		"
	else
		DB_TO_CREATE=`echo $1 | cut -d= -f2`
		DB_TO_CREATE=$(_simple_urldecode "$DB_TO_CREATE")	
		DB_TO_CREATE=`echo "$DB_TO_CREATE" | tr ' ' '_'`
		echo "<BR>Create new database <B>$DB_TO_CREATE</B><BR><BR>"

		echo "Note: space in name will be replaced with _ (underscore)<BR><BR>"
		OLDPWD=`pwd`
		cd $DB_PATH
		touch "$DB_TO_CREATE"
		if [ $? -eq 0 ]
		then
			echo "Status: Database created successfully"
		else
			echo "Status: Failed to create database (error code: $?)"
		fi
		cd $OLDPWD
	fi
}


go_browse_table()
{
	echo "<BR>Browse table <B>$2</B> of database <B>$1</B><BR><BR>"

	OLDPWD=`pwd`
	cd $DB_PATH

	field_count=`$SQLITE_BINARY $1 ".schema $2" | cut -d\( -f2 | cut -d\) -f1 | sed -e "s/primary\s*key//i" | tr ',' '\n' | wc -l`
	fields=`$SQLITE_BINARY $1 ".schema $2" | cut -d\( -f2 | cut -d\) -f1 | sed -e "s/primary\s*key//i"`

	REAL_FIELD_COUNT=0
	for i in `seq 1 $field_count`
	do
		temp=`echo $fields | cut -d, -f$i` 
		field_name=`echo $temp | cut -d' ' -f1 | tr -d '[[:space:]]'` 
		if [ ! -z $field_name ]
		then
			let REAL_FIELD_COUNT=$REAL_FIELD_COUNT+1
		fi
	done

	echo "<TABLE class='full'>"




# 	this can be used if you only want to browse
#	when you need to add button or hyperlink for specified row, then problem will arise
#	$SQLITE_BINARY -html -header $1 "select * from $2"

	FIELDS=""

	for i in `seq 1 $field_count`
	do
		temp=`echo $fields | cut -d, -f$i` 
		field_name=`echo $temp | cut -d' ' -f1 | tr -d '[[:space:]]'` 
		if [ ! -z $field_name ]
		then
			echo "<TH>$field_name</TH>"
			[ ! -z $FIELDS ] && FIELDS="$FIELDS|$field_name" || FIELDS="$field_name"
		fi
	done
	echo "<TH><U>delete</U></TH>"

	row_count=`$SQLITE_BINARY $1 "select count(*) from $2" | tr -d '[[:space:]]'`

	if [ $row_count -gt 0 ] 
	then
		for i in `seq 1 $row_count`
		do
			temp_field_info="field_count=$REAL_FIELD_COUNT"

			let temp2=$i-1
			temp=`$SQLITE_BINARY $1 "select * from $2 limit $temp2,1 "`
			echo "<TR>"

			temp_field=""
			for j in `seq 1 $REAL_FIELD_COUNT`
			do
				temp3=`echo $temp | cut -d\| -f$j`
				temp3b=$(_simple_urlencode "$temp3")
				temp4=`echo $FIELDS| cut -d\| -f$j`
				temp_field="$temp4=$temp3b"
				temp_field_info="$temp_field_info&$temp_field"
				echo "<TD>$temp3</TD>"
				
			done
			echo "<TD><A href='$SCRIPT_NAME/delete_from_table/$1/$2/?$temp_field_info'>delete</A></TD>"	
			echo "</TR>"
		done
	fi


	echo "</TABLE>"
	echo "<BR><BR><A href='$SCRIPT_NAME/browse/$1'>browse database $1</A>"
	cd $OLDPWD
	
}

go_drop_table()
{
	echo "<BR>Drop table <B>$2</B> of database <B>$1</B><BR><BR>"

	OLDPWD=`pwd`	
	cd $DB_PATH
	$SQLITE_BINARY $1 "drop table $2" 1>/dev/null 2>&1
	if [ $? -eq 0 ]
	then
		echo "Status: Table $2 deleted successfully"
	else
		echo "Status: Failed to delete table $2"
	fi	

	echo "<BR><BR><A href='$SCRIPT_NAME/browse/$1'>browse database $1</A>"
	cd $OLDPWD
}

go_insert_table()
{
	echo "<BR>Insert into table <B>$2</B> of database <B>$1</B><BR><BR>"

	OLDPWD=`pwd`
	cd $DB_PATH

	field_count=`$SQLITE_BINARY $1 ".schema $2" | cut -d\( -f2 | cut -d\) -f1 | sed -e "s/primary\s*key//i" | tr ',' '\n' | wc -l`
	fields=`$SQLITE_BINARY $1 ".schema $2" | cut -d\( -f2 | cut -d\) -f1 | sed -e "s/primary\s*key//i"`


	REAL_FIELD_COUNT=0
	for i in `seq 1 $field_count`
	do
		temp=`echo $fields | cut -d, -f$i` 
		field_name=`echo $temp | cut -d' ' -f1 | tr -d '[[:space:]]'` 
		if [ ! -z $field_name ]
		then
			let REAL_FIELD_COUNT=$REAL_FIELD_COUNT+1
		fi
	done


	echo "<FORM action='$SCRIPT_NAME/insert_table_action/$1/$2/'>"
	echo "<INPUT type='hidden' name='field_count' value='$REAL_FIELD_COUNT'>"
	echo "<TABLE class='full'>"
	echo "<TH>Field</TH><TH>Value</TH>"

	for i in `seq 1 $field_count`
	do
		temp=`echo $fields | cut -d, -f$i` 
		field_name=`echo $temp | cut -d' ' -f1 | tr -d '[[:space:]]'` 
		if [ ! -z $field_name ]
		then
			echo "<TR>"
			echo "<TD>$field_name</TD>"
			echo "<TD><INPUT TYPE='text' name='$field_name' class='full'></TD>"
			echo "</TR>"	
		fi
	done

	echo "<TR><TD>&nbsp;</TD><TD><INPUT type='submit' value='insert'></TD><TR>"	
	echo "</TABLE>"
	
	echo "</FORM>"

	cd $OLDPWD
}

go_insert_table_action()
{
	echo "<BR>Insert into table <B>$2</B> of database <B>$1</B><BR><BR>"


	FIELD_COUNT_TEMP=`echo $QUERY_STRING | cut -d\& -f1`
	FIELD_COUNT=`echo $FIELD_COUNT_TEMP | cut -d= -f2`

	FIELDS_TEMP=`echo $QUERY_STRING | cut -d\& -f2-`

	for i in `seq 1 $FIELD_COUNT`
	do
		temp=`echo $FIELDS_TEMP | cut -d\& -f$i`
		field=`echo $temp | cut -d= -f1 | tr -d '[[:space:]]'`
		value=`echo $temp | cut -d= -f2 | tr -d '[[:space:]]'`
		value=$(_simple_urldecode $value)
		echo $value
		if [ ! -z $field ]
		then
			if [ $i -lt $FIELD_COUNT ]
			then

				FIELDS="$FIELDS $field,"		
				VALUES="$VALUES '$value',"
			else
				FIELDS="$FIELDS $field"		
				VALUES="$VALUES '$value'"
			fi
		fi

	done


	SQL_COMMAND="INSERT INTO $2($FIELDS) VALUES ($VALUES);"

	OLDPWD=`pwd`
	cd $DB_PATH

	echo $SQL_COMMAND
	echo "<BR><BR>"

	$SQLITE_BINARY $1 "$SQL_COMMAND" > /dev/null 2>&1
	if [ $? -eq 0 ]
	then
		echo "Status: New row added successfully to table $2"
	else
		echo "Status: Failed to insert table $2"
	fi	

	echo "<BR><BR><A href='$SCRIPT_NAME/browse/$1'>browse database $1</A>"

	cd $OLDPWD
}

go_delete_from_table()
{
	echo "<BR>Delete from table <B>$2</B> of database <B>$1</B><BR><BR>"

	FIELD_COUNT_TEMP=`echo $QUERY_STRING | cut -d\& -f1`
	FIELD_COUNT=`echo $FIELD_COUNT_TEMP | cut -d= -f2`

	FIELDS_TEMP=`echo $QUERY_STRING | cut -d\& -f2-`

	for i in `seq 1 $FIELD_COUNT`
	do
		temp=`echo $FIELDS_TEMP | cut -d\& -f$i`
		field=`echo $temp | cut -d= -f1 | tr -d '[[:space:]]'`
		value=`echo $temp | cut -d= -f2 | tr -d '[[:space:]]'`
		value=$(_simple_urldecode $value)

		if [ ! -z $field ]
		then
			if [ $i -lt $FIELD_COUNT ]
			then
				DEL_TEMP="$DEL_TEMP $field='$value' and"
			else
				DEL_TEMP="$DEL_TEMP $field='$value'"
			fi
		fi

	done


	SQL_COMMAND="DELETE FROM  $2 where $DEL_TEMP;"

	OLDPWD=`pwd`
	cd $DB_PATH

	echo $SQL_COMMAND
	echo "<BR><BR>"

	$SQLITE_BINARY $1 "$SQL_COMMAND" > /dev/null 2>&1
	if [ $? -eq 0 ]
	then
		echo "Status: Data deleted successfully"
	else
		echo "Status: Failed to delete data"
	fi	

	echo "<BR><BR><A href='$SCRIPT_NAME/browse/$1'>browse database $1</A>"
	echo "<BR><BR><A href='$SCRIPT_NAME/browse_table/$1/$2'>browse table $2</A>"

	cd $OLDPWD
}

go_add_table()
{
	if [ -z "$2" ]
	then
		echo "<BR>Add table for database <B>$1</B><BR><BR>"
		echo "
		<FORM action='$SCRIPT_NAME/add_table/$1/' method='get'>
		<INPUT type='hidden'  name='task' value='step1'>
		<TABLE class='noborder'>
		<TR>
		<TD class='noborder'>Table name</TD>
		<TD class='noborder'><INPUT type='text' name='table_name'></TD>
		</TR>
		<TR>
		<TD class='noborder'>Field count</TD>
		<TD class='noborder'><INPUT type='text' name='field_count'></TD>
		</TR>
		<TR>
		<TD class='noborder' colspan='2'><INPUT type='submit' value='next'></TD>
		</TR>	
		</TABLE>
		</FORM>
		"
	else
		LOCAL_TASK_INFO=`echo $2 | cut -d\& -f1`
		LOCAL_TASK=`echo $LOCAL_TASK_INFO | cut -d= -f2`

		TABLE_NAME_INFO=`echo $2 | cut -d\& -f2`
		TABLE_NAME=`echo $TABLE_NAME_INFO | cut -d= -f2`
		FIELD_COUNT_INFO=`echo $2 | cut -d\& -f3`
		FIELD_COUNT=`echo $FIELD_COUNT_INFO | cut -d= -f2`
		case $LOCAL_TASK in
		step1)
		
			echo "<BR>Please specify column name and type for table <B>$TABLE_NAME</B><BR><BR>"

			echo "<FORM action='$SCRIPT_NAME/add_table/$1/' method='get'>"
			echo "<INPUT type='hidden'  name='task' value='step2'>"
			echo "<INPUT type='hidden'  name='table_name' value='$TABLE_NAME'>"
			echo "<INPUT type='hidden'  name='field_count' value='$FIELD_COUNT'>"
			echo "<TABLE class='noborder'>"			
			
			for i in `seq 1 $FIELD_COUNT`
			do
				echo "<TR>"
				echo "<TD class='noborder'>Field $i</TD>"
				echo "<TD class='noborder'><INPUT type='text' name='field_$i'></TD>"
				echo "<TD class='noborder'>"
				echo "<SELECT name='type_$i'>"
				echo "<OPTION value='NULL'>NULL</OPTION>"
				echo "<OPTION value='INTEGER'>INTEGER</OPTION>"
				echo "<OPTION value='REAL'>REAL</OPTION>"
				echo "<OPTION value='TEXT'>TEXT</OPTION>"
				echo "<OPTION value='BLOB'>BLOB</OPTION>"
				echo "</SELECT>"
				echo "</TD>"
				echo "<TD class='noborder'><INPUT type='checkbox' name='pk_$i' value='1'>is primary key</TD>"
				echo "</TR>"
			done
			echo "<TR>"
			echo "<TD class='noborder' colspan='2'><INPUT type='submit' value='finish'></TD>"
			echo "</TR>"	
			echo "</TABLE>"

			echo "</FORM>"
			;;
		step2)
			echo "<BR>Create table <B>$TABLE_NAME ($FIELD_COUNT)</B><BR><BR>"
			CMD="CREATE TABLE $TABLE_NAME ("

			FIELDS=`echo $2 | cut -d\& -f4- | tr '\&' ' '`
			POS=0
			POS_PK=0
			for i in $FIELDS
			do
				KEY=`echo $i | cut -d= -f1 | cut -d_ -f1`
				VAL=`echo $i | cut -d= -f2`
			
				TEMP=""
				if [ $KEY == "field" ]
				then
					[ $POS -eq 0 ] && TEMP=$VAL || TEMP=",$VAL"
					PREV_FIELD=$VAL
				elif [ $KEY == "type" ]
				then
					TEMP="$TEMP $VAL"
				elif [ $KEY == "pk" ]
				then
					if [ $POS_PK -eq 0 ]
					then
						PK_TEMP="$PK_TEMP $PREV_FIELD" 
						POS_PK=1 
					else
						PK_TEMP="$PK_TEMP, $PREV_FIELD"
					fi
				fi
				CMD="$CMD $TEMP"
				let POS=$POS+1
			done	
			PK_TEMP_TEST=`echo $PK_TEMP | tr -d [[:space:]]`
			test -z $PK_TEMP_TEST && CMD="$CMD);" || CMD="$CMD, primary key ($PK_TEMP));" 

			echo $CMD
			echo "<BR><BR>"		

			OLDPWD=`pwd`
			cd $DB_PATH
			$SQLITE_BINARY $1 "$CMD"
			if [ $? -eq 0 ]
			then
				echo "Status: Table $TABLE_NAME created successfully"
			else
				echo "Status: Failed to create $TABLE_NAME"
			fi
			cd $OLDPWD
		
			echo "<BR><BR><A href='$SCRIPT_NAME/browse/$1'>browse database $1</A>"
			
		esac	
	fi



	

}

#
# main functions
####################################################################
main()
{
	_cgi_header
	_program_info
	_html_header
	_check_prereq
	if [ $? -ne 0 ]
	then
		print_errmsg "$ERRSTR"
	else
		show_menu
		TASK_MAIN=`echo $TASK | cut -d/ -f2`
		TASK_DETAIL=`echo $TASK | cut -d/ -f3`
		TASK_EXTRAINFO=`echo $TASK | cut -d/ -f4`
		case $TASK_MAIN in
		home)
			go_home
			;;
		browse)
			go_browse $TASK_DETAIL
			;;
		create)
			go_create $TASK_DETAIL
			;;
		delete)
			go_delete $TASK_DETAIL
			;;
		rename)
			go_rename $TASK_DETAIL
			;;
		rename_action)
			go_rename_action $TASK_DETAIL $TASK_EXTRAINFO
			;;
		browse_table)
			go_browse_table $TASK_DETAIL $TASK_EXTRAINFO
			;;
		drop_table)
			go_drop_table $TASK_DETAIL $TASK_EXTRAINFO
			;;
		insert_table)
			go_insert_table $TASK_DETAIL $TASK_EXTRAINFO
			;;
		insert_table_action)
			go_insert_table_action $TASK_DETAIL $TASK_EXTRAINFO
			;;
		delete_from_table)
			go_delete_from_table $TASK_DETAIL $TASK_EXTRAINFO
			;;
		add_table)
			go_add_table $TASK_DETAIL $TASK_EXTRAINFO
			;;
		esac
	fi
	_html_footer
}

#
# main program
####################################################################
main


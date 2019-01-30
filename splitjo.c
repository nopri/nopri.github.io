/*
 * ** Copyright (C) 2006 Noprianto <nop@noprianto.com>
 * **
 * ** This program is free software; you can redistribute it and/or
 * ** modify it under the terms of the GNU General Public License,
 * ** version 2, as published by the Free Software Foundation.
 * ** 
 * ** This program is distributed in the hope that it will be useful,
 * ** but WITHOUT ANY WARRANTY; without even the implied warranty of
 * ** MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * ** GNU General Public License for more details.
 * ** 
 * ** You should have received a copy of the GNU General Public License
 * ** along with this program; if not, write to the Free Software 
 * ** Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
*/


#include <stdio.h>
#include <stdlib.h>
#include <getopt.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <libgen.h>
#include <string.h>
#include <glob.h>

#define VERSION "0.2.3"
#define FN_LEN 255


int dec_len = 5;
long int bytes = 10000;


void print_usage (char * progname)
{
	fprintf (stdout, "splitjo version %s\n",  VERSION);
	fprintf (stdout, "(c) Noprianto, 2006.\n");
	fprintf (stdout, "http://www.noprianto.com/splitjo.php\n");
	fprintf (stdout, "GPL, no warranty.\n");
	fprintf (stdout, "\n");
	
	fprintf (stdout, "Usage: %s ACTION OPTION...\n", progname);
	
	fprintf (stdout, "Actions:\n");
	fprintf (stdout, "  -s, --split    split file\n");
	fprintf (stdout, "  -j, --join     join files\n");
	fprintf (stdout, "  -h, --help     show this screen\n");

	fprintf (stdout, "\n\n");
	fprintf (stdout, "Options:\n");
	fprintf (stdout, "  -i<FILE>, --infile=<FILE>  \n");
	fprintf (stdout, "     File to split (for --split)\n");
	fprintf (stdout, "     or File criterion to join (for --join)\n\n");
	fprintf (stdout, "  -o<FILE>, --outfile=<FILE>  \n");
	fprintf (stdout, "     Output file prefix (for --split), default: basename of input file\n");
	fprintf (stdout, "     or Output file (for --join), default: basename of input file criterion\n\n");
	fprintf (stdout, "  -b<NUM>,  --byte=<NUM>\n");
	fprintf (stdout, "     put NUM byte per output file (only for --split), default: %li\n\n", bytes);
	fprintf (stdout, "  -n<NUM>,  --length=<NUM>\n");
	fprintf (stdout, "     Length of file suffix (only for --split), default: %i\n\n", dec_len);

	
	fprintf (stdout, "\n");
	fprintf (stdout, "Examples:\n");
	fprintf (stdout, "split test (75948 b) into test.00000 - test.00007 (8 pcs each max 10000)\n");
	fprintf (stdout, "  splitjo -s -i test \n");
	fprintf (stdout, "split test (75948 b) into test.00000 - test.00001 (2 pcs each max 50000)\n");
	fprintf (stdout, "  splitjo -s -i test -b 50000\n");
	fprintf (stdout, "split test (75948 b) into part.00000 - part.00001 (2 pcs each max 50000)\n");
	fprintf (stdout, "  splitjo -s -i test -b 50000 -o part\n");
	fprintf (stdout, "join part.00000 - part.00001 as part\n");
	fprintf (stdout, "  splitjo -j -ipart.*\n");
	fprintf (stdout, "join part.00000 - part.00001 as myfile\n");
	fprintf (stdout, "  splitjo -j -ipart.* -omyfile\n");
	fprintf (stdout, "\n");
	fprintf (stdout, "\n");
	fprintf (stdout, "Thank you for using splitjo\n");
	fprintf (stdout, "\n");
	

	
}

int split_file (char * infiles, char * outfiles, long int inbytes)
{
	long int i;
	long int j;
	
	int c;

	char * b_files = (char *) malloc (FN_LEN * sizeof (char *));
	char * c_files = (char *) malloc (FN_LEN * sizeof (char *));
	char * fmt = (char *) malloc (FN_LEN * sizeof (char *));

	int ret_val = 0;
	
	struct stat stat_t;
	int stat_ret = stat(infiles, &stat_t);
	
	if (!stat_ret)
	{	
		long int file_size = stat_t.st_size;
		long int pieces = file_size / inbytes + 1;
		fprintf (stdout, "splitting %s (size %li) for each %li (%li pieces)\n", infiles, file_size, inbytes, pieces);

		if (strcmp(outfiles, "") == 0)
		{	
			b_files = basename (infiles);
		}
		else
		{
			strcpy (b_files, outfiles);
		}
		
		for (i = 0; i < pieces; i++)
		{
			sprintf(fmt, "%%s.%%.%dli", dec_len);
			sprintf(c_files, fmt, b_files, i);
			

			
			FILE *f = fopen(infiles, "rb");
			FILE *f2 = fopen(c_files, "wb");

			fseek (f, i * bytes  , SEEK_SET);

			for (j=0; j< inbytes; j++)
			{
				if (!feof(f))
				{
					c = fgetc (f);
					if (c != EOF) fputc (c, f2);
				}
			}
			
			fclose (f2);
			fclose (f);
		
			fprintf (stdout, "\tfile %s created.\n", c_files);
			
		}
		fprintf (stdout, "done.\n");
		
		
	}
	else
	{
		ret_val =  stat_ret;
	}
	
	free (b_files);
	free (c_files);
	free (fmt);
	return ret_val;
}

int join_files (char * infiles, char * outfiles)
{

	long int found;
	long int i;
	int c;
	int index;
	
	char * b_files = (char *) malloc (FN_LEN * sizeof (char *));
	
	int ret_val;
	glob_t globbuf;
	
	globbuf.gl_offs = 0;
	
	glob(infiles, GLOB_DOOFFS, NULL, &globbuf);


	found = globbuf.gl_pathc;

	ret_val = 0;	

	if (strcmp (outfiles, "") == 0)
	{
		
	
		for (i = 0; i < strlen(infiles); i++)
		{
			if (infiles[i] == '.')
			{
				index = i;
				break;
			}
		}
		strncpy (b_files, infiles, index);
	}
	else
	{
		strcpy (b_files, outfiles);
	}
	
	
	fprintf (stdout, "joining %s (%li files) as %s\n" , infiles, found, b_files);

	FILE *f = fopen(b_files, "wb");
	
	for (i = 0; i < found; i++)
	{
		
		FILE * f2 = fopen (globbuf.gl_pathv[i], "rb");
		while (!feof (f2))
		{
			c = fgetc (f2);
			if (c != EOF) fputc (c, f);
		}
		
		fclose (f2);
	
		fprintf (stdout, "\tfile %s joined\n", globbuf.gl_pathv[i]);

		
	}
		
	fclose (f);
	fprintf (stdout, "done.\n");
	
	free (b_files);
	
	return ret_val;
}


int main (int argc, char * argv[])
{
	int c;
	int option_index = 0;

	int byte_set = 0;
	
	char * outfiles = (char *) malloc (FN_LEN * sizeof (char *));
	char * infiles = (char *) malloc (FN_LEN * sizeof (char *));
	int infile_set = 0;
	int outfile_set = 0;
	
	int temp;
	
	static struct option long_options[] = 
	{
		{"split", 0, 0, 0},
		{"join", 0, 0, 0},
		{"help", 0, 0, 0},
		{"byte", 1, 0, 0},
		{"length", 1, 0, 0},
		{"infile", 1, 0, 0},
		{"outfile", 1, 0, 0},
		{0, 0, 0, 0}
	};


	enum what_t 
	{
		NOT_SET, ERROR_MULTI, JOIN, SPLIT
	};

	enum what_t what = NOT_SET;

	int ret_val = 0;

	while ( (c = getopt_long (argc, argv, "sjhb:i:n:o:", long_options, &option_index)) != -1)
		switch (c)
		{
			case 0:
				if (strcmp (long_options[option_index].name, "help") == 0)
				{
					print_usage (argv[0]);
					exit (0);
					break;
				}
				else
				if (strcmp (long_options[option_index].name, "split") == 0)
				{
					if (what == NOT_SET || what == SPLIT)
						what = SPLIT;
					else
						what = ERROR_MULTI;
					break;
				}
				else
				if (strcmp (long_options[option_index].name, "join") == 0)
				{
					if (what == NOT_SET || what == JOIN)
						what = JOIN;
					else
						what = ERROR_MULTI;
					break;
				}
				else
				if (strcmp (long_options[option_index].name, "byte") == 0)
				{
					temp = atoi(optarg);	
					if (temp > 0)
					{
						bytes = temp;
						byte_set = 1;
					}
					break;
				}
				else
				if (strcmp (long_options[option_index].name, "infile") == 0)
				{
					if (optarg)
					{
						strcpy(infiles, optarg);
						infile_set = 1;
					}
					break;
				}
				if (strcmp (long_options[option_index].name, "length") == 0)
				{
					temp = atoi (optarg);
					if (temp > 0) 
						dec_len = temp;
					break;
				}
				if (strcmp (long_options[option_index].name, "outfile") == 0)
				{
					if (optarg)
					{
						strcpy(outfiles, optarg);
						outfile_set = 1;
					}
					break;
				}
				break;
			case 'h':
				print_usage (argv[0]);
				exit (0);
				break;
			case 's':
				if (what == NOT_SET || what == SPLIT)
					what = SPLIT;
				else
					what = ERROR_MULTI;
				break;
			case 'j':
				if (what == NOT_SET || what == JOIN)
					what = JOIN;
				else
					what = ERROR_MULTI;
				break;
			case 'b':
				temp = atoi(optarg);	
				if (temp > 0)
				{
					bytes = temp;
					byte_set = 1;
				}
				break;
			case 'i':
				if (optarg)
				{
					strcpy(infiles, optarg);
					infile_set = 1;
				}
				break;
			case 'n':
				temp = atoi (optarg);
				if (temp > 0) 
					dec_len = temp;
				break;
			case 'o':
				if (optarg)
				{
					strcpy(outfiles, optarg);
					outfile_set = 1;
				}
				break;
		}



	if (what == ERROR_MULTI)
	{
		fprintf(stderr, "%s: multiple actions are given, but only one allowed (try --help)\n", argv[0]);
		ret_val = 1;
		exit(ret_val);
	}
	else
	if (what == NOT_SET)
	{
		fprintf(stderr, "%s: no action specified (try --help)\n", argv[0]);
		ret_val = 2;
		exit(ret_val);
	}
	else
	if (what == JOIN && byte_set == 1)
	{
		fprintf(stderr, "%s: join given, but --byte also set, ignoring...\n", argv[0]);
	};
	
	if (infile_set == 0)
	{
		fprintf(stderr, "%s: no input filename/input filename criterion given\n", argv[0]);
		ret_val = 3;
		exit(ret_val);
	}

	if (outfile_set == 1)
	{
		if ( strlen(outfiles) < 1)
		{
			fprintf(stderr, "%s: --outfile given with no filename\n", argv[0]);
			ret_val = 4;
			exit(ret_val);
		}
	}


	switch (what)
	{
		case SPLIT: 
			ret_val =  split_file (infiles, outfiles, bytes);
			break;
		case JOIN:
			ret_val = join_files(infiles, outfiles);
	}

	free (outfiles);
	free (infiles);
	
	return ret_val;
}

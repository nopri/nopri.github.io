#include <gtk/gtk.h>

/*
 * nops2pdf
 * (c) Noprianto, 2007
 * <nop@noprianto.com>
 * http://www.noprianto.com
 *
 * GPL
 *
 */

#define APP_NAME "nops2pdf"
#define APP_VERSION "0.7"
#define AUTHOR_INIT "Noprianto <nop@noprianto.com>"

#define PS2PDF_BIN "/usr/bin/ps2pdf"

enum 
{
	OPT_NAME = 0,
	OPT_VAL,
	COLUMNS
};

typedef struct
{
	gchar *name;
	gchar *value;
} OptionItem;

const OptionItem option_list [] =
{
	{"CompatibilityLevel", "1.3"},
	{"PDFSETTINGS", "/prepress"},
	{"AutoRotatePages","/All"},
	{"CompressPages","true"},
	{"SubsetFonts","true"},
	{"MaxSubsetPct","100"},
	{"ConvertCMYKImagesToRGB","false"},
	{"AutoFilterColorImages","false"},
	{"DownsampleColorImages","false"},
	{"ColorImageResolution","300"},
	{"ColorImageDownsampleType","/Bicubic"},
	{"AutoFilterGrayImages","false"},
	{"DownsampleGrayImages","false"},
	{"GrayImageDownsampleType","/Bicubic"},
	{"GrayImageResolution","300"},
	{"MonoImageFilter","/CCITTFaxEncode"},
	{"DownsampleMonoImages","false"},
	{"MonoImageDownsampleType","/Bicubic"},
	{"MonoImageResolution","1200"},
	{NULL, NULL}
};

gchar * input_file = NULL, *output_file = NULL;

static void choose_input_file (GtkButton *button, GtkWindow *parent)
{
	GtkWidget *dialog;
	GtkFileFilter *f_ps, *f_all;
	
	/* file filter for dialog */
	f_ps = gtk_file_filter_new ();
	gtk_file_filter_set_name (f_ps, "PostScript files");
	gtk_file_filter_add_pattern (f_ps, "*.ps");
	
	f_all = gtk_file_filter_new ();
	gtk_file_filter_set_name (f_all, "All files");
	gtk_file_filter_add_pattern (f_all, "*");

	dialog = gtk_file_chooser_dialog_new ("Choose input file",\
			parent, GTK_FILE_CHOOSER_ACTION_OPEN, \
			GTK_STOCK_CANCEL, GTK_RESPONSE_CANCEL, \
			GTK_STOCK_OPEN, GTK_RESPONSE_ACCEPT, NULL);

	/* apply filter */
	gtk_file_chooser_add_filter (GTK_FILE_CHOOSER (dialog), f_ps);
	gtk_file_chooser_add_filter (GTK_FILE_CHOOSER (dialog), f_all);
	

	gint result = gtk_dialog_run (GTK_DIALOG (dialog));
	if (result == GTK_RESPONSE_ACCEPT)
	{
		input_file = gtk_file_chooser_get_filename\
			   (GTK_FILE_CHOOSER (dialog) );
		gtk_button_set_label (button, input_file);
	}
	else
	{
		input_file = NULL;
		gtk_button_set_label (button, "Choose input file");
	};

	gtk_widget_destroy (dialog);
};

static void choose_output_file (GtkButton *button, GtkWindow *parent)
{
	GtkWidget *dialog;
	GtkFileFilter *f_pdf, *f_all;
	
	/* file filter for dialog */
	f_all = gtk_file_filter_new ();
	gtk_file_filter_set_name (f_all, "All files");
	gtk_file_filter_add_pattern (f_all, "*");

	f_pdf = gtk_file_filter_new ();
	gtk_file_filter_set_name (f_pdf, "PDF files");
	gtk_file_filter_add_pattern (f_all, "*.pdf");
	
	dialog = gtk_file_chooser_dialog_new ("Choose output file",\
			parent, GTK_FILE_CHOOSER_ACTION_SAVE, \
			GTK_STOCK_CANCEL, GTK_RESPONSE_CANCEL, \
			GTK_STOCK_SAVE, GTK_RESPONSE_ACCEPT, NULL);

	/* apply filter */
	gtk_file_chooser_add_filter (GTK_FILE_CHOOSER (dialog), f_pdf);
	gtk_file_chooser_add_filter (GTK_FILE_CHOOSER (dialog), f_all);
	
	gint result = gtk_dialog_run (GTK_DIALOG (dialog));
	if (result == GTK_RESPONSE_ACCEPT)
	{
		output_file = gtk_file_chooser_get_filename \
			   (GTK_FILE_CHOOSER (dialog) );
		gtk_button_set_label (button, output_file);
	}
	else
	{
		output_file = NULL;
		gtk_button_set_label (button, "Choose output file");
	};

	gtk_widget_destroy (dialog);

};

static void show_about (GtkWidget *button, GtkWindow *parent)
{
	GtkWidget *dialog;
	
	const gchar * authors[] = {AUTHOR_INIT, NULL} ;

	dialog = gtk_about_dialog_new ();

	gtk_about_dialog_set_name (GTK_ABOUT_DIALOG (dialog), APP_NAME);
	gtk_about_dialog_set_version (GTK_ABOUT_DIALOG (dialog), APP_VERSION);
	gtk_about_dialog_set_copyright (GTK_ABOUT_DIALOG (dialog), "(c) Noprianto, 2007");
	gtk_about_dialog_set_comments (GTK_ABOUT_DIALOG (dialog), "Special for infolinux :)");
	gtk_about_dialog_set_license (GTK_ABOUT_DIALOG (dialog), "GPL");
	gtk_about_dialog_set_website (GTK_ABOUT_DIALOG (dialog), "http://www.noprianto.com");
	gtk_about_dialog_set_authors (GTK_ABOUT_DIALOG (dialog), authors);

	gtk_dialog_run (GTK_DIALOG (dialog));

	gtk_widget_destroy (dialog);
};


static void cell_edited (GtkCellRendererText *renderer, gchar *path, \
		gchar *new_text, GtkTreeView *options)
{
	GtkTreeIter iter;
	GtkTreeModel *tree_model;

	if (g_ascii_strcasecmp (new_text, "") != 0)
	{
		tree_model = gtk_tree_view_get_model (options);
		if (gtk_tree_model_get_iter_from_string (tree_model, &iter, path))
		{
			gtk_list_store_set (GTK_LIST_STORE (tree_model), \
					&iter, OPT_VAL, new_text, -1);
		}
	};
};


static void setup_options (GtkWidget *options )
{
	GtkCellRenderer *renderer;
	GtkTreeViewColumn *column;

	renderer = gtk_cell_renderer_text_new ();
	column = gtk_tree_view_column_new_with_attributes (\
			"Option", renderer, "text", OPT_NAME, NULL);
	gtk_tree_view_append_column (GTK_TREE_VIEW (options), column);
	
	renderer = gtk_cell_renderer_text_new ();
	g_object_set (renderer, "editable", TRUE, "editable-set", TRUE,NULL);

	g_signal_connect (G_OBJECT (renderer), "edited", \
			G_CALLBACK (cell_edited), (gpointer) options);

	column = gtk_tree_view_column_new_with_attributes (\
			"Value", renderer, "text", OPT_VAL, NULL);
	gtk_tree_view_append_column (GTK_TREE_VIEW (options), column);
};

static void do_convert (GtkWidget *button, GtkTreeView *options)
{
	GtkTreeIter iter;
	GtkTreeModel *tree_model;

	gchar *option_name, *option_value;

	gchar *temp = NULL;
	gchar *cmd_args = NULL;
	gchar *real_command = NULL;

	GtkWidget *dialog;

	GtkWidget *parent_temp, *parent_window;

	gboolean status = FALSE;
	gint error_code;

	/* parent get parent get parent :p, fix me :p */
	parent_temp = gtk_widget_get_parent (button);
	parent_temp = gtk_widget_get_parent (parent_temp);
	parent_temp = gtk_widget_get_parent (parent_temp);
	parent_window = gtk_widget_get_parent (parent_temp);

	/* check for i/o files */
	if (input_file == NULL || output_file == NULL)
	{
		dialog = gtk_message_dialog_new (GTK_WINDOW (parent_window),\
			       	GTK_DIALOG_MODAL, \
			       	GTK_MESSAGE_ERROR, GTK_BUTTONS_OK, \
				"Please choose input/output file first");

		gtk_window_set_title (GTK_WINDOW (dialog), "Error");

		gtk_dialog_run (GTK_DIALOG (dialog));

		gtk_widget_destroy (dialog);
		return;
	};

	gtk_widget_set_sensitive (parent_window, FALSE);

	/* generating PDF may take loooong time */
	while (gtk_events_pending ())
	{
		gtk_main_iteration ();
	};

	/* get options, build command args */
	tree_model = gtk_tree_view_get_model (options);

	gtk_tree_model_get_iter_first (tree_model, &iter);

	do
	{
		gtk_tree_model_get (tree_model, &iter,\
			       	OPT_NAME, &option_name, -1);
		gtk_tree_model_get (tree_model, &iter, \
				OPT_VAL, &option_value, -1);


		if (option_name != NULL)
		{
			temp = g_strconcat ("-d", option_name,\
				       	"=", option_value, " ", NULL);
			cmd_args = g_strconcat (temp, cmd_args, NULL);
		};


	} while ( gtk_tree_model_iter_next (tree_model, &iter));
	/* end of command args build */


	/* command check and exec */
	if (!g_file_test (PS2PDF_BIN, \
				G_FILE_TEST_EXISTS | G_FILE_TEST_IS_EXECUTABLE))
	{
		temp = g_strconcat ("Couldn't find ", PS2PDF_BIN, NULL);
		dialog = gtk_message_dialog_new (GTK_WINDOW (parent_window),\
			       	GTK_DIALOG_MODAL, \
			       	GTK_MESSAGE_ERROR, GTK_BUTTONS_OK, \
				temp);

		gtk_window_set_title (GTK_WINDOW (dialog), "Error");

		gtk_dialog_run (GTK_DIALOG (dialog));

		gtk_widget_destroy (dialog);
	}
	else
	{

		real_command = g_strconcat (PS2PDF_BIN, " ", cmd_args, \
				" \"", input_file, "\" \"", output_file, "\"", NULL);
		

		/* exec here */
		status = g_spawn_command_line_sync (real_command, \
				NULL, NULL, &error_code, NULL);

		/* end of exec */
		
		temp = NULL;
		if (error_code == 0 )
		{
			temp = g_strconcat (output_file, " ", "generated", NULL);
			dialog = gtk_message_dialog_new (GTK_WINDOW (parent_window),\
			       	GTK_DIALOG_MODAL, \
			       	GTK_MESSAGE_INFO, GTK_BUTTONS_OK, \
				temp);
		}
		else
		{
			temp = g_strconcat ("Error occured", NULL);
			dialog = gtk_message_dialog_new (GTK_WINDOW (parent_window),\
			       	GTK_DIALOG_MODAL, \
			       	GTK_MESSAGE_ERROR, GTK_BUTTONS_OK, \
				temp);
		};


		gtk_window_set_title (GTK_WINDOW (dialog), "Result");

		gtk_dialog_run (GTK_DIALOG (dialog));

		gtk_widget_destroy (dialog);
	}
	/* end of command check and exec */
	
	g_free (temp);
	g_free (option_name);
	g_free (option_value);
	g_free (real_command);
	g_free (cmd_args);


	gtk_widget_set_sensitive (parent_window, TRUE);
};

int main (int argc, char *argv[])
{
	GtkWidget *window;

	GtkWidget *btn_i, *btn_o, *lbl_i, *lbl_o;
	GtkWidget *btn_about, *btn_quit, *btn_exec;

	GtkWidget *frame_io, *frame_options, *frame_actions;;
	
	GtkWidget *table_main, *table_io;
	GtkWidget *hbox_actions;

	GtkWidget *options, *scrolled_win;
	GtkListStore *list_store;
	GtkTreeIter iter;

	guint i = 0;

	gchar temp[256];

	/* GTK init */
	gtk_init (&argc, &argv); 
	/* end of GTK init */

	/* main window and basic signal*/
	window = gtk_window_new (GTK_WINDOW_TOPLEVEL);
	gtk_widget_set_size_request (window, 640, 480);
	
	g_snprintf (temp, sizeof (temp), "%s version %s", \
			APP_NAME, APP_VERSION);
	gtk_window_set_title (GTK_WINDOW (window), temp);
	gtk_container_set_border_width (GTK_CONTAINER (window), 10);
	
	g_signal_connect_swapped (G_OBJECT (window), "destroy", \
			G_CALLBACK (gtk_main_quit), (gpointer) window);
	/* end of main window setting */


	/* frame IO */
	/* choose input and output file */
	btn_i = gtk_button_new_with_label ("Choose input file");
	btn_o = gtk_button_new_with_label ("Choose output file");

	lbl_i = gtk_label_new ("Input file");
	lbl_o = gtk_label_new ("Output file");
	
	g_signal_connect (G_OBJECT (btn_i), "clicked", \
			G_CALLBACK (choose_input_file), \
			(gpointer) window);
	g_signal_connect (G_OBJECT (btn_o), "clicked", \
			G_CALLBACK (choose_output_file), \
			(gpointer) window);
	
	/* frame for input/output param */
	frame_io = gtk_frame_new ("Input/Output");
	
	/* add i/o widget to table */
	table_io = gtk_table_new (2,6, TRUE);
	gtk_table_set_col_spacings (GTK_TABLE (table_io), 5);
	gtk_table_set_row_spacings (GTK_TABLE (table_io), 5);
	gtk_table_attach_defaults (GTK_TABLE (table_io), lbl_i, 0, 1, 0, 1);
	gtk_table_attach_defaults (GTK_TABLE (table_io), btn_i, 1, 6, 0, 1);
	gtk_table_attach_defaults (GTK_TABLE (table_io), lbl_o, 0, 1, 1, 2);
	gtk_table_attach_defaults (GTK_TABLE (table_io), btn_o, 1, 6, 1, 2);

	gtk_container_add (GTK_CONTAINER (frame_io), table_io);

	/* end of frame IO */


	/* Frame Options */


	/* setup options :) */
	options = gtk_tree_view_new (); 
	setup_options (options);

	list_store = gtk_list_store_new (COLUMNS, G_TYPE_STRING, G_TYPE_STRING);

	while (option_list[i].name != NULL)
	{
		gtk_list_store_append (list_store, &iter);
		gtk_list_store_set (list_store, &iter, \
				OPT_NAME, option_list[i].name, \
				OPT_VAL, option_list[i].value, \
				-1);

		i++;
	
	};

	gtk_tree_view_set_model (GTK_TREE_VIEW (options), GTK_TREE_MODEL (list_store));
	g_object_unref (list_store);

	scrolled_win = gtk_scrolled_window_new (NULL, NULL);
	gtk_scrolled_window_set_policy (GTK_SCROLLED_WINDOW (scrolled_win), \
			GTK_POLICY_AUTOMATIC, GTK_POLICY_AUTOMATIC);

	gtk_container_add (GTK_CONTAINER (scrolled_win), options);


	/* frame for options */
	frame_options = gtk_frame_new ("Options");

	gtk_container_add (GTK_CONTAINER (frame_options), scrolled_win);

	/* end of Frame Options */

	/* Frame Actions */
	/* action buttons */
	btn_about = gtk_button_new_from_stock (GTK_STOCK_ABOUT);
	btn_exec = gtk_button_new_from_stock (GTK_STOCK_EXECUTE);
	btn_quit = gtk_button_new_from_stock (GTK_STOCK_QUIT);
	
	
	g_signal_connect_swapped (G_OBJECT (btn_quit), "clicked", \
				G_CALLBACK (gtk_main_quit), \
				(gpointer) window);

	g_signal_connect (G_OBJECT (btn_about), "clicked", \
			G_CALLBACK (show_about), (gpointer) window);
	
	g_signal_connect (G_OBJECT (btn_exec), "clicked", \
			G_CALLBACK (do_convert), (gpointer) options);

	/* frame for actions */
	frame_actions = gtk_frame_new ("Actions");
	
	/* add widget to actions frame */
	hbox_actions = gtk_hbox_new (TRUE, 5);
	gtk_box_pack_start_defaults (GTK_BOX (hbox_actions), btn_about);
	gtk_box_pack_start_defaults (GTK_BOX (hbox_actions), btn_exec);
	gtk_box_pack_start_defaults (GTK_BOX (hbox_actions), btn_quit);
	
	gtk_container_add (GTK_CONTAINER (frame_actions), hbox_actions);
	/* end of Frame Actions */


	/* main table layout */
	table_main = gtk_table_new (9, 1, TRUE);

	/* add frames to main table */
	gtk_table_attach_defaults (GTK_TABLE (table_main), frame_io, \
					0, 1, 0, 2);
	gtk_table_attach_defaults (GTK_TABLE (table_main), frame_options,\
			       		0, 1, 2, 8);
	gtk_table_attach_defaults (GTK_TABLE (table_main), frame_actions, \
					0, 1, 8, 9);
	/* end of main table */

	
	/* add table to main window */
	gtk_container_add (GTK_CONTAINER (window), table_main);

	/* show all widget */
	gtk_widget_show_all (window);

	/* gtk main */
	gtk_main ();

	g_free (input_file);

	g_free (output_file);

	return 0;
};


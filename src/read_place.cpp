#include <stdexcept>
#include <vector>
#include <stdio.h>
#include <string.h>
#include "util.h"
#include "vpr_types.h"
#include "globals.h"
#include "hash.h"
#include "read_place.h"
#include "Formatter.hpp"


static int get_subblock (int i, int j, int bnum);
static void read_place_header(BufferBase &file_buffer, char *net_file,
                              char *arch_file);


void read_user_pad_loc (char *pad_loc_file) {

/* Reads in the locations of the IO pads from a file. */

 struct s_hash **hash_table, *h_ptr;
 int iblk, i, j, xtmp, ytmp, bnum, isubblk;
 char buf[BUFSIZE], bname[BUFSIZE], *ptr;

 my_printf ("\nReading locations of IO pads from %s.\n", pad_loc_file);
 FileBuffer file_buffer(my_fopen(pad_loc_file, "r", 0));

 hash_table = alloc_hash_table ();
 for (iblk=0;iblk<num_blocks;iblk++) {
    if (block[iblk].type == INPAD || block[iblk].type == OUTPAD) {
       h_ptr = insert_in_hash_table (hash_table, block[iblk].name, iblk);
       block[iblk].x = OPEN;   /* Mark as not seen yet. */
    }
 }

 for (i=0;i<=nx+1;i++) {
    for (j=0;j<=ny+1;j++) {
       if (clb[i][j].type == IO) {
          for (isubblk=0;isubblk<io_rat;isubblk++)
             clb[i][j].u.io_blocks[isubblk] = OPEN;  /* Flag for err. check */
       }
    }
 }

 ptr = file_buffer.get_joined_string(BUFSIZE);

 while (ptr != NULL) {
    ptr = file_buffer.token(buf, TOKENS);
    if (ptr == NULL) {
       ptr = file_buffer.get_joined_string(BUFSIZE);
       continue;      /* Skip blank or comment lines. */
    }

    strcpy (bname, ptr);

    ptr = file_buffer.token(NULL, TOKENS);
    if (ptr == NULL) {
       printf ("Error:  line %d is incomplete.\n", file_buffer.linenum_);
       exit (1);
    }
    sscanf (ptr, "%d", &xtmp);

    ptr = file_buffer.token(NULL, TOKENS);
    if (ptr == NULL) {
       printf ("Error:  line %d is incomplete.\n", file_buffer.linenum_);
       exit (1);
    }
    sscanf (ptr, "%d", &ytmp);

    ptr = file_buffer.token(NULL, TOKENS);
    if (ptr == NULL) {
       printf ("Error:  line %d is incomplete.\n", file_buffer.linenum_);
       exit (1);
    }
    sscanf (ptr, "%d", &isubblk);

    ptr = file_buffer.token(NULL, TOKENS);
    if (ptr != NULL) {
       printf ("Error:  extra characters at end of line %d.\n", file_buffer.linenum_);
       exit (1);
    }

    h_ptr = get_hash_entry (hash_table, bname);
    if (h_ptr == NULL) {
       printf ("Error:  block %s on line %d: no such IO pad.\n",
                bname, file_buffer.linenum_);
       exit (1);
    }
    bnum = h_ptr->index;
    i = xtmp;
    j = ytmp;

    if (block[bnum].x != OPEN) {
       printf ("Error:  line %d.  Block %s listed twice in pad file.\n",
                file_buffer.linenum_, bname);
       exit (1);
    }

    if (i < 0 || i > nx+1 || j < 0 || j > ny + 1) {
       printf("Error:  block #%d (%s) location\n", bnum, bname);
       my_printf("(%d,%d) is out of range.\n", i, j);
       exit (1);
    }

    block[bnum].x = i;   /* Will be reloaded by initial_placement anyway. */
    block[bnum].y = j;   /* I need to set .x only as a done flag.         */

    if (clb[i][j].type != IO) {
       printf("Error:  attempt to place IO block %s in \n", bname);
       my_printf("an illegal location (%d, %d).\n", i, j);
       exit (1);
    }

    if (isubblk >= io_rat || isubblk < 0) {
       printf ("Error:  Block %s subblock number (%d) on line %d is out of "
               "range.\n", bname, isubblk, file_buffer.linenum_);
       exit (1);
    }
    clb[i][j].u.io_blocks[isubblk] = bnum;
    clb[i][j].occ++;

    ptr = file_buffer.get_joined_string(BUFSIZE);
 }

 for (iblk=0;iblk<num_blocks;iblk++) {
    if ((block[iblk].type == INPAD || block[iblk].type == OUTPAD) &&
             block[iblk].x == OPEN) {
       printf ("Error:  IO block %s location was not specified in "
               "the pad file.\n", block[iblk].name);
       exit (1);
    }
 }

 for (i=0;i<=nx+1;i++) {
    for (j=0;j<=ny+1;j++) {
       if (clb[i][j].type == IO) {
          for (isubblk=0;isubblk<clb[i][j].occ;isubblk++) {
             if (clb[i][j].u.io_blocks[isubblk] == OPEN) {
                printf ("Error:  The IO blocks at (%d, %d) do not have \n"
                        "consecutive subblock numbers starting at 0.\n", i, j);
                exit (1);
             }
          }
       }
    }
 }

 free_hash_table (hash_table);
 my_printf ("Successfully read %s.\n\n", pad_loc_file);
}


void dump_clbs (void) {

/* Output routine for debugging. */

 int i, j, index;

 for (i=0;i<=nx+1;i++) {
    for (j=0;j<=ny+1;j++) {
       my_printf("clb (%d,%d):  type: %d  occ: %d\n",
        i,j,clb[i][j].type, clb[i][j].occ);
       if (clb[i][j].type == CLB)
          my_printf("block: %d\n",clb[i][j].u.block);
       if (clb[i][j].type == IO) {
          my_printf("io_blocks: ");
          for (index=0;index<clb[i][j].occ;index++)
              my_printf("%d  ", clb[i][j].u.io_blocks[index]);
          my_printf("\n");
       }
    }
 }

 for (i=0;i<num_blocks;i++) {
    my_printf("block: %d, (i,j): (%d, %d)\n",i,block[i].x,block[i].y);
 }
}


void print_place (char *place_file, char *net_file, char *arch_file) {

/* Prints out the placement of the circuit.  The architecture and    *
 * netlist files used to generate this placement are recorded in the *
 * file to avoid loading a placement with the wrong support files    *
 * later.                                                            */

 FILE *fp;
 int i, subblock;

 fp = my_fopen(place_file,"w",0);

 fprintf(fp,"Netlist file: %s   Architecture file: %s\n", net_file,
    arch_file);
 fprintf (fp, "Array size: %d x %d logic blocks\n\n", nx, ny);
 fprintf (fp, "#block name\tx\ty\tsubblk\tblock number\n");
 fprintf (fp, "#----------\t--\t--\t------\t------------\n");

 for (i=0;i<num_blocks;i++) {
    fprintf (fp,"%s\t", block[i].name);
    if (strlen(block[i].name) < 8)
       fprintf (fp, "\t");

    fprintf (fp,"%d\t%d", block[i].x, block[i].y);
    if (block[i].type == CLB) {
       fprintf(fp,"\t%d", 0);        /* Sub block number not meaningful. */
    }
    else {                /* IO block.  Save sub block number. */
       subblock = get_subblock (block[i].x, block[i].y, i);
       fprintf(fp,"\t%d", subblock);
    }
    fprintf (fp, "\t#%d\n", i);
 }

 fclose(fp);
}


std::vector<std::vector<unsigned int> > extract_block_positions() {
/* Return the position of all blocks in the placement as a two-dimensional vector, with dimensions indexed as follows:
 *
 *     block-index, x=0/y=1/slot-index=2
 */
 std::vector<std::vector<unsigned int> > block_positions(num_blocks,
                                                         std::vector
                                                         <unsigned int>(3));

 for (int i = 0; i < num_blocks; i++) {
    block_positions[i][0] = block[i].x;
    block_positions[i][1] = block[i].y;
    if (block[i].type == CLB) {
        /* Sub block number not meaningful in the case of CLB. */
        block_positions[i][2] = 0;
    } else {
        /* IO block.  Save sub block number as slot-index. */
        block_positions[i][2] = get_subblock (block[i].x, block[i].y, i);
    }
 }

 return block_positions;
}

static int get_subblock (int i, int j, int bnum) {

/* Use this routine only for IO blocks.  It passes back the index of the *
 * subblock containing block bnum at location (i,j).                     */

 int k;

 for (k=0;k<io_rat;k++) {
    if (clb[i][j].u.io_blocks[k] == bnum)
       return (k);
 }

 printf("Error in get_subblock.  Block %d is not at location (%d,%d)\n",
    bnum, i, j);
 exit (1);
}


void parse_placement_file(BufferBase &place_file_buffer, char *net_file,
                          char *arch_file) {

/* Reads the blocks in from a previously placed circuit.             */

 FILE *fp;
 char bname[BUFSIZE];
 char buf[BUFSIZE], *ptr;
 struct s_hash **hash_table, *h_ptr;
 int i, j, bnum, isubblock, xtmp, ytmp;


 read_place_header(place_file_buffer, net_file, arch_file);

 for (i=0;i<=nx+1;i++) {
    for (j=0;j<=ny+1;j++) {
       clb[i][j].occ = 0;
       if (clb[i][j].type == IO) {
          for (isubblock=0;isubblock<io_rat;isubblock++) {
             clb[i][j].u.io_blocks[isubblock] = OPEN;
          }
       }
    }
 }

 for (i=0;i<num_blocks;i++)
    block[i].x = OPEN;        /* Flag to show not read yet. */

 hash_table = alloc_hash_table ();
 for (i=0;i<num_blocks;i++)
    h_ptr = insert_in_hash_table (hash_table, block[i].name, i);

 ptr = place_file_buffer.get_joined_string(BUFSIZE);

 while (ptr != NULL) {
    ptr = place_file_buffer.token(place_file_buffer.buffer_, TOKENS);
    if (ptr == NULL) {
     ptr = place_file_buffer.get_joined_string(BUFSIZE);
       continue;      /* Skip blank or comment lines. */
    }

    strcpy (bname, ptr);

    ptr = place_file_buffer.token(NULL, TOKENS);
    if (ptr == NULL) {
       printf ("Error:  line %d is incomplete.\n", place_file_buffer.linenum_);
       exit (1);
    }
    sscanf (ptr, "%d", &xtmp);

    ptr = place_file_buffer.token(NULL, TOKENS);
    if (ptr == NULL) {
       printf ("Error:  line %d is incomplete.\n", place_file_buffer.linenum_);
       exit (1);
    }
    sscanf (ptr, "%d", &ytmp);

    ptr = place_file_buffer.token(NULL, TOKENS);
    if (ptr == NULL) {
       printf ("Error:  line %d is incomplete.\n", place_file_buffer.linenum_);
       exit (1);
    }
    sscanf (ptr, "%d", &isubblock);

    ptr = place_file_buffer.token(NULL, TOKENS);
    if (ptr != NULL) {
       printf ("Error:  extra characters at end of line %d.\n", place_file_buffer.linenum_);
       exit (1);
    }

    h_ptr = get_hash_entry (hash_table, bname);
    if (h_ptr == NULL) {
       printf ("Error:  block %s on line %d does not exist in the netlist.\n",
                bname, place_file_buffer.linenum_);
       exit (1);
    }
    bnum = h_ptr->index;
    i = xtmp;
    j = ytmp;

    if (block[bnum].x != OPEN) {
       printf ("Error:  line %d.  Block %s listed twice in placement file.\n",
                place_file_buffer.linenum_, bname);
       exit (1);
    }

    if (i < 0 || i > nx+1 || j < 0 || j > ny + 1) {
       printf("Error in read_place.  Block #%d (%s) location\n", bnum, bname);
       my_printf("(%d,%d) is out of range.\n", i, j);
       exit (1);
    }

    block[bnum].x = i;
    block[bnum].y = j;

    if (clb[i][j].type == CLB) {
       if (block[bnum].type != CLB) {
          printf("Error in read_place.  Attempt to place block #%d (%s) in\n",
               bnum, bname);
          my_printf("a logic block location (%d, %d).\n", i, j);
          exit (1);
       }
       clb[i][j].u.block = bnum;
       clb[i][j].occ++;
    }

    else if (clb[i][j].type == IO) {
       if (block[bnum].type != INPAD && block[bnum].type != OUTPAD) {
          printf("Error in read_place.  Attempt to place block #%d (%s) in\n",
               bnum, bname);
          my_printf("an IO block location (%d, %d).\n", i, j);
          exit (1);
       }
       if (isubblock >= io_rat || isubblock < 0) {
          printf ("Error:  Block %s subblock number (%d) on line %d is out of "
                  "range.\n", bname, isubblock, place_file_buffer.linenum_);
          exit (1);
       }
       clb[i][j].u.io_blocks[isubblock] = bnum;
       clb[i][j].occ++;
    }

    else {    /* Block type was ILLEGAL or some unknown value */
       printf("Error in read_place.  Block #%d (%s) is in an illegal ",
           bnum, bname);
       my_printf("location.\nLocation specified: (%d,%d).\n", i, j);
       exit (1);
    }

    ptr = place_file_buffer.get_joined_string(BUFSIZE);
 }

 free_hash_table (hash_table);

 for (i=0;i<num_blocks;i++) {
    if (block[i].x == OPEN) {
       printf ("Error in read_place:  block %s location was not specified in "
               "the placement file.\n", block[i].name);
       exit (1);
    }
 }

 for (i=0;i<=nx+1;i++) {
    for (j=0;j<=ny+1;j++) {
       if (clb[i][j].type == IO) {
          for (isubblock=0;isubblock<clb[i][j].occ;isubblock++) {
             if (clb[i][j].u.io_blocks[isubblock] == OPEN) {
                printf ("Error:  The IO blocks at (%d, %d) do not have \n"
                        "consecutive subblock numbers starting at 0.\n", i, j);
                exit (1);
             }
          }
       }
    }
 }

 //printf ("Successfully read %s.\n", place_file);
}


static void read_place_header(BufferBase &file_buffer, char *net_file,
                              char *arch_file) {
/* Reads the header from the placement file.  Used only to check that this *
 * placement file matches the current architecture, netlist, etc.          */

 char *line_one_names[] = {"Netlist", "file:", " ", "Architecture", "file:"};
 char *line_two_names[] = {"Array", "size:", " ", "x", " ", "logic", "blocks"};
 char net_check[BUFSIZE], arch_check[BUFSIZE], *ptr;
 int nx_check, ny_check, i;


 ptr = file_buffer.get_joined_string(BUFSIZE);

 if (ptr == NULL) {
    printf ("Error:  netlist file and architecture file used not listed.\n");
    exit (1);
 }

 ptr = file_buffer.token(file_buffer.buffer_, TOKENS);
 while (ptr == NULL) {   /* Skip blank or comment lines. */
    ptr = file_buffer.get_joined_string(BUFSIZE);
    if (ptr == NULL) {
       printf ("Error:  netlist file and architecture file used not listed.\n");       exit (1);
    }
    ptr = file_buffer.token(file_buffer.buffer_, TOKENS);
 }

 for (i=0;i<=5;i++) {
    if (i == 2) {
       strcpy (net_check, ptr);
    }
    else if (i == 5) {
       strcpy (arch_check, ptr);
    }
    else {
       if (strcmp (ptr, line_one_names[i]) != 0) {
          printf ("Error on line %d, word %d:  \n"
                  "Expected keyword %s, got %s.\n", file_buffer.linenum_, i+1,
                  line_one_names[i], ptr);
          exit (1);
       }
    }
    ptr = file_buffer.token(NULL, TOKENS);
    if (ptr == NULL && i != 5) {
       printf ("Error:  Unexpected end of line on line %d.\n", file_buffer.linenum_);
       exit (1);
    }
 }

 if (strcmp(net_check, net_file) != 0) {
    my_printf("Warning:  Placement generated with netlist file %s:\n",
            net_check);
    my_printf("current net file is %s.\n", net_file);
 }

 if (strcmp(arch_check, arch_file) != 0) {
    my_printf("Warning:  Placement generated with architecture file %s:\n",
           arch_check);
    my_printf("current architecture file is %s.\n", arch_file);
 }

/* Now check the second line (array size). */

 ptr = file_buffer.get_joined_string(BUFSIZE);

 if (ptr == NULL) {
    printf ("Error:  Array size not listed.\n");
    exit (1);
 }

 ptr = file_buffer.token(file_buffer.buffer_, TOKENS);
 while (ptr == NULL) {   /* Skip blank or comment lines. */
    ptr = file_buffer.get_joined_string(BUFSIZE);
    if (ptr == NULL) {
       printf ("Error:  array size not listed.\n");
       exit (1);
    }
    ptr = file_buffer.token(file_buffer.buffer_, TOKENS);
 }

 for (i=0;i<=6;i++) {
    if (i == 2) {
       sscanf (ptr, "%d", &nx_check);
    }
    else if (i == 4) {
       sscanf (ptr, "%d", &ny_check);
    }
    else {
       if (strcmp (ptr, line_two_names[i]) != 0) {
          printf ("Error on line %d, word %d:  \n"
                  "Expected keyword %s, got %s.\n", file_buffer.linenum_, i+1,
                  line_two_names[i], ptr);
          exit (1);
       }
    }
    ptr = file_buffer.token(NULL, TOKENS);
    if (ptr == NULL && i != 6) {
       printf ("Error:  Unexpected end of line on line %d.\n", file_buffer.linenum_);
       exit (1);
    }
 }

 if (nx_check > nx || ny_check > ny) {
     throw std::runtime_error(Formatter() << "Placement file assumes an "
                              "array size of " << nx_check << " x " << ny_check
                              << ".\n Current size is " << nx << " x " << ny
                              << ".");
 } else if (nx_check < nx && ny_check < ny) {
    printf ("[warning] Placement file assumes an array size of %d x %d.\n",
            nx_check, ny_check);
    printf ("Current size is %d x %d.\n", nx, ny);
 }
}

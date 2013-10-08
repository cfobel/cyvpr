#ifndef ___READ_PLACE__HPP___
#define ___READ_PLACE__HPP___

#include "Buffer.hpp"


void parse_placement_file(BufferBase &place_file_buffer, char *net_file,
                          char *arch_file);

void print_place (char *place_file, char *net_file, char *arch_file);

void read_user_pad_loc (char *pad_loc_file);

void dump_clbs (void);   /* For debugging */

#endif

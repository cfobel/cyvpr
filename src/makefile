# This makefile is written for gcc running under Solaris on a SPARCstation.
# To compile VPR on other systems, you may have to change:
# (1) CC to the name of your C compiler.
# (2) LIB_DIR to point at your directory of X11 libraries (libX11.a, etc.)
# (3) On many systems, the -R/usr/openwin/lib option on the LIB line
#     will have to be removed.
# (4) X11_INCLUDE to point at the directory containing "x11/xlib.h" etc.
# (5) OPT_FLAGS should be changed to whatever options turn on maximum 
#     optimization in your compiler.
# (6) If your system does not support X11 (e.g. you're running on Windows NT)
#     then add -DNO_GRAPHICS to the end of the "FLAGS =" line.

CC = g++

#SunOS lines below.
#LIB_DIR = -L/usr/lib/X11R5
#LIB = -static -lX11 -lm
#X11_INCLUDE = -I/usr/include

# On many non-Solaris machines, use LIB_DIR = -L/usr/lib/X11R5

LIB_DIR = -L/usr/openwin/lib


# Sometimes get errors under Solaris if you don't use the -R option
# to (I think) put info about where the shared object libraries are
# right into the binary.  Shouldn't be necessary, but it is on our machines.

LIB = -lX11 -lm -lrt #-R/usr/openwin/lib

X11_INCLUDE = -I/usr/openwin/include

# Overly strict flags line below.  Lots of useless warnings, but can 
# let you look for redudant declarations. 
# To avoid redundant declarations here I use -D__STDC instead of
# -D__USE_FIXED_PROTOTYPES, but that means some prototypes are missing.

#FLAGS = -Wall -Wpointer-arith -Wcast-qual -Wstrict-prototypes -O -D__STDC__ -ansi -pedantic -Wredundant-decls -Wmissing-prototypes -Wshadow -Wcast-align -D_POSIX_SOURCE

#Flags to be passed to the compiler.  First is for strict warnings, 
#second for interactive debugging and third for optimization. 

#-D_POSIX_SOURCE stops extra declarations from being included in math.h
#and causing -Wshadow to complain about conflicts with y1 in math.h
#(Bessel function 1 of the second kind) 

WARN_FLAGS = -Wall -Wpointer-arith -Wcast-qual -Wstrict-prototypes -O -D__USE_FIXED_PROTOTYPES__ -ansi -pedantic -Wmissing-prototypes -Wshadow -Wcast-align -D_POSIX_SOURCE
DEBUG_FLAGS = -g
OPT_FLAGS = -O3

#FLAGS = $(WARN_FLAGS)
#FLAGS = $(DEBUG_FLAGS) 
FLAGS = $(OPT_FLAGS) -std=c++0x

#Uncomment line below if X Windows isn't installed on your system.
#FLAGS = $(OPT_FLAGS) -DNO_GRAPHICS

#Useful flags on HP machines
#DEBUG_FLAGS = -Aa -g
#OPT_FLAGS = -Aa +O3

EXE = vpr

OBJ = main.o util.o read_netlist.o print_netlist.o check_netlist.o read_arch.o place_and_route.o place.o route_common.o route_timing.o route_tree_timing.o route_breadth_first.o draw.o graphics.o stats.o segment_stats.o rr_graph.o rr_graph2.o rr_graph_sbox.o rr_graph_util.o rr_graph_timing_params.o rr_graph_indexed_data.o rr_graph_area.o check_rr_graph.o check_route.o hash.o heapsort.o read_place.o net_delay.o path_delay.o path_delay2.o vpr_utils.o timing_place_lookup.o timing_place.o md5.o timing.o

SRC = main.cpp util.cpp read_netlist.cpp print_netlist.cpp check_netlist.cpp read_arch.cpp place_and_route.cpp place.cpp route_common.cpp route_timing.cpp route_tree_timing.cpp route_breadth_first.cpp draw.cpp graphics.cpp stats.cpp segment_stats.cpp rr_graph.cpp rr_graph2.cpp rr_graph_sbox.cpp rr_graph_util.cpp rr_graph_timing_params.cpp rr_graph_indexed_data.cpp rr_graph_area.cpp check_rr_graph.cpp check_route.cpp hash.cpp heapsort.cpp read_place.cpp net_delay.cpp path_delay.cpp path_delay2.cpp test_h.cpp vpr_utils.cpp timing_place_lookup.cpp timing_place.cpp

H = util.h vpr_types.h globals.h graphics.h read_netlist.h print_netlist.h check_netlist.h read_arch.h stats.h segment_stats.h draw.h place_and_route.h place.h route_export.h route_common.h route_timing.h route_tree_timing.h route_breadth_first.h rr_graph.h rr_graph2.h rr_graph_sbox.h rr_graph_util.h rr_graph_timing_params.h rr_graph_indexed_data.h rr_graph_area.h check_rr_graph.h check_route.h hash.h heapsort.h read_place.h path_delay.h path_delay2.h net_delay.h vpr_utils.h timing_place_lookup.h timing_place.h


# I haven't been able to make -static work under Solaris.  Use shared
# libraries all the time.

# Add purify before $(CC) in the link line below to run purify on VPR.

$(EXE): $(OBJ) test_h.o
	$(CC) $(FLAGS) $(OBJ) -o $(EXE) $(LIB_DIR) $(LIB)

# test_h.c is a dummy file -- it just checks the header files against each
# other to see if any global variable definitions conflict in the various
# header files.

test_h.o: test_h.cpp $(H)
	$(CC) -c $(WARN_FLAGS) -Wredundant-decls test_h.cpp


main.o: main.cpp $(H)
	$(CC) -c $(FLAGS) main.cpp

read_netlist.o: read_netlist.cpp $(H)
	$(CC) -c $(FLAGS) read_netlist.cpp

print_netlist.o: print_netlist.cpp $(H)
	$(CC) -c $(FLAGS) print_netlist.cpp

check_netlist.o: check_netlist.cpp $(H)
	$(CC) -c $(FLAGS) check_netlist.cpp

read_arch.o: read_arch.cpp $(H)
	$(CC) -c $(FLAGS) read_arch.cpp

place_and_route.o: place_and_route.cpp $(H)
	$(CC) -c $(FLAGS) place_and_route.cpp

place.o: place.cpp $(H)
	$(CC) -c $(FLAGS) place.cpp

route_common.o: route_common.cpp $(H)
	$(CC) -c $(FLAGS) route_common.cpp

route_timing.o: route_timing.cpp $(H)
	$(CC) -c $(FLAGS) route_timing.cpp

route_tree_timing.o: route_tree_timing.cpp $(H)
	$(CC) -c $(FLAGS) route_tree_timing.cpp

route_breadth_first.o: route_breadth_first.cpp $(H)
	$(CC) -c $(FLAGS) route_breadth_first.cpp

stats.o: stats.cpp $(H)
	$(CC) -c $(FLAGS) stats.cpp

segment_stats.o: segment_stats.cpp $(H)
	$(CC) -c $(FLAGS) segment_stats.cpp

util.o: util.cpp $(H)
	$(CC) -c $(FLAGS) util.cpp

draw.o: draw.cpp $(H)
	$(CC) -c $(FLAGS) draw.cpp

rr_graph.o: rr_graph.cpp $(H)
	$(CC) -c $(FLAGS) rr_graph.cpp

rr_graph2.o: rr_graph2.cpp $(H)
	$(CC) -c $(FLAGS) rr_graph2.cpp

rr_graph_sbox.o: rr_graph_sbox.cpp $(H)
	$(CC) -c $(FLAGS) rr_graph_sbox.cpp

rr_graph_util.o: rr_graph_util.cpp $(H)
	$(CC) -c $(FLAGS) rr_graph_util.cpp

rr_graph_timing_params.o: rr_graph_timing_params.cpp $(H)
	$(CC) -c $(FLAGS) rr_graph_timing_params.cpp

rr_graph_indexed_data.o: rr_graph_indexed_data.cpp $(H)
	$(CC) -c $(FLAGS) rr_graph_indexed_data.cpp

rr_graph_area.o: rr_graph_area.cpp $(H)
	$(CC) -c $(FLAGS) rr_graph_area.cpp

check_rr_graph.o: check_rr_graph.cpp $(H)
	$(CC) -c $(FLAGS) check_rr_graph.cpp

graphics.o: graphics.cpp $(H)
	$(CC) -c $(FLAGS) $(X11_INCLUDE) graphics.cpp

check_route.o: check_route.cpp $(H)
	$(CC) -c $(FLAGS) check_route.cpp

hash.o: hash.cpp $(H)
	$(CC) -c $(FLAGS) hash.cpp

heapsort.o: heapsort.cpp $(H)
	$(CC) -c $(FLAGS) heapsort.cpp

read_place.o: read_place.cpp $(H)
	$(CC) -c $(FLAGS) read_place.cpp

net_delay.o: net_delay.cpp $(H)
	$(CC) -c $(FLAGS) net_delay.cpp

path_delay.o: path_delay.cpp $(H)
	$(CC) -c $(FLAGS) path_delay.cpp

path_delay2.o: path_delay2.cpp $(H)
	$(CC) -c $(FLAGS) path_delay2.cpp

vpr_utils.o: vpr_utils.cpp $(H)
	$(CC) -c $(FLAGS) vpr_utils.cpp

timing_place_lookup.o: timing_place_lookup.cpp $(H)
	$(CC) -c $(FLAGS) timing_place_lookup.cpp

timing_place.o: timing_place.cpp $(H)
	$(CC) -c $(FLAGS) timing_place.cpp

md5.o: md5.cpp md5.hpp
	$(CC) -c $(FLAGS) md5.cpp

timing.o: timing.cpp timing.hpp
	$(CC) -c $(FLAGS) timing.cpp

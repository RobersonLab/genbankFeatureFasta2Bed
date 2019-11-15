#!/bin/env python3

###########
# imports #
###########
import argparse
import logging
import re
import sys

#####################
# basic script info #
#####################
__script_path__ = sys.argv[0]
__script_name__ = __script_path__.split( '/' )[-1].split( "\\" )[-1]
__version__ = '1.0.0'

################################
# parse command-line arguments #
################################
parser = argparse.ArgumentParser( prog=__script_name__, epilog="%s v%s" % ( __script_name__, __version__ ) )

parser.add_argument( "genbank_fasta" )
parser.add_argument( "--output_bed", default = "genbank.bed" )
parser.add_argument( "--score", type = int, default = 500 )
parser.add_argument( "--loglevel", choices=[ 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL' ], default = 'INFO' )

args = parser.parse_args()

#################
# start logging #
#################
logging.basicConfig( format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s' )
logger = logging.getLogger( __script_name__ )
logger.setLevel( args.loglevel )

#########################################
# validity check on command-line values #
#########################################
if args.score < 0 or args.score > 1000:
    logger.critical( "score must be an integer from 0 to 1000." )
    sys.exit( 1 )

################################
# work on genbank feature file #
################################
with open( args.genbank_fasta, 'r' ) as INPUT, open( args.output_bed, 'w' ) as OUTPUT:
    for line in INPUT:
        line = line.rstrip()

        if len( line ) == 0:
            continue

        if line[0] == ">":
            line = re.sub( "\[", r"", line )
            line = re.sub( "\]", r"", line )

            values = line.split( r" " )

            ###################
            # set contig name #
            ###################
            contig = values[0].split( r"|" )[1]

            logger.debug( "Original contig: %s" % ( contig ) )

            contig = re.sub( "^([A-Za-z0-9_]+\.[0-9]+)_.*$", "\\1", contig )

            logger.debug( "Contig is: %s" % ( contig ) )

            #############################################
            # pull other values into a value_dictionary #
            # figure out strand info                    #
            #############################################
            value_dictionary = {}

            for value in values:
                split = value.split( r"=" )
                if len( split ) < 2:
                    continue

                if split[0] == r"location":
                    location_value = split[1]

                    if re.match( r"complement", location_value ):
                        strand = "-"
                        location_value = re.sub( "complement\(", r"", location_value )
                        location_value = re.sub( "\)", r"", location_value )
                    else:
                        strand = "+"

                    logger.debug( "Location is %s" % ( location_value ) )

                    start, end = location_value.split( r".." )

                    value_dictionary[ 'strand' ] = strand
                    value_dictionary[ 'start' ] = start
                    value_dictionary[ 'end' ] = end
                else:
                    value_dictionary[ split[0] ] = split[1]

            for key in value_dictionary:
                logger.debug( "%s     %s" % ( key, value_dictionary[ key ] ) )

            #####################################
            # print relevant output to bed file #
            #####################################
            OUTPUT.write( "%s\t%s\t%s\t%s\t%s\t%s\n" % ( contig, value_dictionary[ 'start' ], value_dictionary[ 'end' ], value_dictionary[ 'gene' ], args.score, value_dictionary[ 'strand' ] ) )
        else:
            continue

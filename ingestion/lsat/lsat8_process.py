#!/usr/bin/python

import argparse
import json
import os
import sys

from utils.utils import initLogger

from ingestion.scripts import GDAL

# Make logger global here
logger = initLogger()

def main():
    parser = argparse.ArgumentParser(description="OWS12 Landsat script. Preprocessing scripts.")
    parser.add_argument('-b', '--bands', help='Select the bands to inject into GeoServer mosaic\n'
                                              'Ex: 4 3 2', default='4 3 2', type=int, nargs='+')
    parser.add_argument('-r', '--resample', nargs=1, default='nearest',
                        choices=('nearest', 'average', 'gauss', 'cubic', 'cubicspline', 'lanczos', 'average_mp',
                                 'average_magphase', 'mode'),
                        help='Resample method to use on GDAL utils. default is nearest')
    parser.add_argument('-c', '--config', nargs='?', help='Specific GDAL configuration string\n'
                                                          'Ex: --config COMPRESS_OVERVIEW DEFLATE')
    parser.add_argument('-m', '--mask', action="store_true", default=False,
                        help='Compute and add bitmask workflow')
    parser.add_argument('-o', '--overviews', type=int, nargs='+',
                        help='Overviews to add to the target image. \n'
                        'e.g. 2 4 8 16 32 64')
    parser.add_argument('-w', '--warp', nargs=1,
                        help='The projection EPSG code to use for gdalwarp')
    parser.add_argument('files', help='Mosaic files path')

    args = parser.parse_args()

    gd = GDAL()
    # Add common options
    gd.rmethod = args.resample[0]

    # Before we proceed, check if we retrieved any files during previous download step
    if not os.path.exists(os.path.join(args.files, 'ingest.txt')):
        logger.info('Missing file from previous download job.\nPlease run this job first!')
        sys.exit(1)
    num_lines = sum(1 for l in open(os.path.join(args.files, 'ingest.txt')))
    if num_lines == 0:
        logger.info('Skipping processing step. No files to process found!')
        sys.exit(0)

    if args.warp:
        warp_options = '-srcnodata 0 -dstnodata 0 -co BLOCKXSIZE=512 -co BLOCKYSIZE=512 -co TILED=YES ' \
                       '-wo OPTIMIZE_SIZE=YES -co COMPRESS=DEFLATE'
        with open(os.path.join(args.files, 'ingest.txt'), 'r') as file:
            for l in file:
                row = json.loads(l)
                for b in args.bands:
                    if b == row[0]:
                        granule = os.path.join(args.files, str(row[2]['properties']['sceneID']),
                                     str(row[2]['properties']['sceneID']) + '_B' + str(b) + '.TIF')
                        output_granule = granule.replace('.TIF', '_WARPED.TIF')
                        # TODO: Enable parallel processing
                        gd.warp(inputf=granule, outputf=output_granule, t_srs=args.warp[0], options=warp_options)
                        # Stick with original filenames
                        os.remove(granule)
                        if os.path.exists(output_granule[:-3] + 'IMD'):
                            os.remove(output_granule[:-3] + 'IMD')
                        os.rename(output_granule, granule)
                        break

    if args.mask:
        with open(os.path.join(args.files, 'ingest.txt'), 'r') as file:
            for l in file:
                row = json.loads(l)
                for b in list(args.bands):
                    if b == row[0]:
                        granule = os.path.join(args.files, str(row[2]['properties']['sceneID']),
                                     str(row[2]['properties']['sceneID']) + '_B' + str(b) + '.TIF')
                        outfile = granule.replace('.TIF', '.MSK')
                        # TODO: Enable parallel processing
                        gd.calc(outputf=outfile, datatype='UInt16', filemap='-A ' + granule,
                                bandsmap='--A_band=1', creation_options='--creation-option=TILED=YES '
                                                                        '--creation-option=BLOCKXSIZE=512 '
                                                                        '--creation-option=BLOCKYSIZE=512 '
                                                                        '--creation-option=COMPRESS=DEFLATE '
                                                                        '--creation-option=INTERLEAVE=BAND',
                                calc_expr='\"logical_not(A==0)\"')
                        outmaskedfile = granule.replace('.TIF', '_MASKED.TIF')
                        gd.merge(outputf=outmaskedfile, datatype='UInt16', fformat='GTiff', separate=True,
                                 inputf=(granule, outfile), creation_options='-co TILED=YES '
                                                                             '-co BLOCKXSIZE=512 '
                                                                             '-co BLOCKYSIZE=512 '
                                                                             '-co COMPRESS=DEFLATE '
                                                                             '-co INTERLEAVE=BAND '
                                                                             '-co ALPHA=NO')
                        os.remove(outfile)
                        os.remove(granule)
                        os.rename(outmaskedfile, granule)
                        break

    if args.overviews:
        scales = args.overviews
        with open(os.path.join(args.files, 'ingest.txt'), 'r') as file:
            for l in file:
                row = json.loads(l)
                for b in list(args.bands):
                    if b == row[0]:
                        granule = os.path.join(args.files, str(row[2]['properties']['sceneID']),
                                     str(row[2]['properties']['sceneID']) + '_B' + str(b) + '.TIF')
                        # TODO: Enable parallel processing
                        gd.addOverviews(file=granule, scales=scales, configs=args.config)
                        break


if __name__ == '__main__':
    main()
#!/usr/bin/python

import argparse
import sys
import os
from scripts.sentinel import SentinelSat
from scripts.gdal import GDAL
from utils.utils import initLogger

# Make logger global here
logger = initLogger()

def main():
    parser = argparse.ArgumentParser(description="OWS12 Sentinel preprocess granules script.")
    parser.add_argument('-b', '--bands', help='If you specify bands, landsat-util will try to download '
                                              'the band from S3. If the band does not exist, an error is returned\n'
                                              'Ex: 4 3 2', default='4 3 2', type=int, nargs='+')
    parser.add_argument('-r', '--resample', nargs=1, default='nearest',
                        choices=('nearest', 'average', 'gauss', 'cubic', 'cubicspline', 'lanczos', 'average_mp',
                                 'average_magphase', 'mode'),
                        help='Resample method to use on GDAL utils. default is nearest')
    parser.add_argument('-c', '--config', nargs='?', help='Specific GDAL configuration string\n'
                                                          'Ex: --config COMPRESS_OVERVIEW DEFLATE')
    parser.add_argument('-o', '--overviews', help='Overviews to add to the target image.\n'
                                                  'e.g. 2 4 8 16 32 64',
                        type=int, nargs='+')
    parser.add_argument('-w', '--warp', nargs=1,
                        help='The projection EPSG code to use for gdalwarp')
    parser.add_argument('--download', help='Path to previously saved products packages')
    parser.add_argument('--output', help='Destination path for the processed images')

    args = parser.parse_args()

    gd = GDAL()
    # Add common options
    gd.rmethod = args.resample[0]

    sentinel = SentinelSat()

    # Before we proceed, check if we retrieved any files during previous download step
    if not os.path.exists(os.path.join(args.download, sentinel.products_list)):
        logger.info('Missing file from previous download job.\nPlease run this job first!')
        sys.exit(1)
    num_lines = sum(1 for l in open(os.path.join(args.download, sentinel.products_list)))
    if num_lines == 0:
        logger.info('Skipping processing step. No files to process found!')
        sys.exit(0)

    try:
        sentinel.unpack_products(args.download)
        if args.warp:
            warp_options = '-srcnodata 0 -dstnodata 0 -co BLOCKXSIZE=512 -co BLOCKYSIZE=512 -co TILED=YES ' \
                           '-wo OPTIMIZE_SIZE=YES -co COMPRESS=DEFLATE -of GTiff'
            sentinel.warp_granules(args.download, args.bands, gd, args.warp[0], warp_options)
        if args.overviews:
            sentinel.overviews_granules(args.download, args.bands, gd, args.overviews, args.config)
        # Copy processed granules
        sentinel.copy_granules_s2(args.download, args.output, args.bands)

    except Exception, e:
        logger.error(e)

if __name__ == '__main__':
    main()
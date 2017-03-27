#!/usr/bin/env python

def collect_sentinel2_metadata(safe_pkg, granule):
    return ({
                # USED IN METADATA TEMPLATE and as SEARCH PARAMETERS
                'timeStart':safe_pkg.product_start_time,
                'timeEnd':safe_pkg.product_stop_time,
                'eoParentIdentifier':"S2_MSI_L1C",# from Torsten velocity template see related mail in ML
                'eoAcquisitionType':"NOMINAL",# from Torsten velocity template see related mail in ML
                'eoOrbitNumber':safe_pkg.sensing_orbit_number,
                'eoOrbitDirection':safe_pkg.sensing_orbit_direction,
                'optCloudCover':granule.cloud_percent,
                'eoCreationDate':safe_pkg.generation_time,
                'eoArchivingCenter':"DPA",# from Torsten velocity template see related mail in ML
                'eoProcessingMode':"DATA_DRIVEN",# from Torsten velocity template see related mail in ML
                'footprint':str(granule.footprint),
                'eoIdentifier':granule.granule_identifier
            },
            {
                # USED IN METADATA TEMPLATE ONLY
                'eoProcessingLevel':safe_pkg.processing_level,
                'eoSensorType':"OPTICAL",
                'eoOrbitType':"LEO",
                'eoProductType':safe_pkg.product_type,
                'eoInstrument':safe_pkg.product_type[2:5],
                'eoPlatform':safe_pkg.spacecraft_name[0:10],
                'eoPlatformSerialIdentifier':safe_pkg.spacecraft_name[10:11]
            },
            {
                #TO BE USED IN THE PRODUCT ABSTRACT TEMPLATE
                'timeStart':safe_pkg.product_start_time,
                'timeEnd':safe_pkg.product_stop_time,
            })

def create_ogc_links_dict(list):
    ogc_links = []
    for el in list:
        ogc_links.append({
            'offering':el[1],
            'method':el[2],
            'code':el[3],
            'type':el[4],
            'href':el[5]
        })
    print ogc_links
    return ogc_links

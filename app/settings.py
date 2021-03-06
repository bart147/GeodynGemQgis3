from __future__ import absolute_import
import os, sys
import logging
from datetime import datetime

# settings
root_dir        = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
log_dir         = os.path.join(root_dir, 'log')
result_dir      = ""
INP_FIELDS_XLS  = os.path.join(root_dir, 'inp_fields.xls') ##, 'fields$')
INP_FIELDS_XLS_SHEET    = "fields"
INP_FIELDS_CSV  = os.path.join(root_dir, 'inp_fields.csv')

# logging level
LOGGING_LEVEL = logging.INFO        # set tot DEBUG for all information or INFO for only main info

# zoektermen voor herkennen kaartlagen
keyword_1 = 'kikker' # knooppunten kikker
keyword_2 = 'kikker' # afvoerrelaties kikker
keyword_3 = 'BAG'    # BAG
keyword_4 = 'VE'     # Belasting Vervuilingseenheden
keyword_5 = 'RIGO'   # plancap RIGO ruimtelijke ordening
keyword_6 = 'opp'    # verhard opp (BGT)
keyword_7 = 'bem'    # bemalingsgebieden

# set to False to keep the result after run
l_result_layers_to_remove = [
    ("bemalingsgebieden overlap", False),
    ("eindknooppunten", True),
    ("polygon_kikker_sum", True),
    ("polygon_kikker", True),
    ("knooppunten_sel2", True),
    ("knooppunten_sel1", True),
    ("knooppunten", False),
    ("stats_verh_opp_VGS", True),
    ("stats_verh_opp_OBK", True),
    ("stats_verh_opp_NAG", True),
    ("stats_verh_opp_HWA", True),
    ("stats_verh_opp_GEM", True),
    ("stats_verh_opp_totaal", True),
    ("verhard_opp_intersect", True),
    ("stats_ve", True),
    ("stats_plancap", True),
    ("plancap_overlap", False),
    ("stats_drinkwater", True),
    ("eindresultaat", False),
    ("inp_polygon_copy", True),
    ("eindgebieden", True),
]

b_raise_xlrd_import_error = False  # raise xlrd import error to test csv file.
b_remove_results_after_run = False  # set to False to keep results after run
b_skip_spatial_join = False # toggle True/False to skip the spatial join for faster development. only works if spatial_join results already present

# dict d_velden_tmp
# purpose: dict d_velden_tmp is een aanvulling op d_velden (d_velden wordt uit de inp_fields.xlsx gegenereerd).
#         gebruikt in utl-functies add_field_from_dict() en bereken_veld()

d_velden_tmp = {
    # PWN temp
    "SUMPAR_M3U": {"add_fld": "stap2tmp", "field_type" : "DOUBLE", "field_alias" : "SUM_PAR_RESULT_M3U", "expression": "[PAR_RESULT_sum] / 1000"}, #tmp in STATS_DRINKWATER
    "SUMZAK_M3U": {"add_fld": "stap2tmp", "field_type" : "DOUBLE", "field_alias" : "SUM_ZAK_RESULT_M3U", "expression": "[ZAK_RESULT_sum] / 1000"}, #tmp in STATS_DRINKWATER
    "HA_BEM_G"  : {"add_fld": "stap3tmp", "field_type" : "DOUBLE", "field_alias" : "opp bemalingsgebied ha"}, #, "expression": "[sum]/10000"},
    "PERCENTAGE"  : {"add_fld": "stap4tmp", "field_type" : "DOUBLE", "field_alias" : "percentage", "expression": "[SUM_SHAPE_Area]/[OPP_BEMGEBIED]*100"},
    }

# lijst met velden waarvan de None-waardes omgezet moeten worden naar 0. Omdat 1 + None = None i.p.v. 1 + 0 = 1
l_fld_None_naar_0_omzetten = [
    "X_WON_ONBG", "X_WON_GEB","X_VE_ONBG", "X_VE_GEB", "DWR_GEBIED", "DWR_ONBG",
    "AW_15_24_G", "AW_15_24_O", "AW_25_50_G", "AW_25_50_O", "PAR_RESULT", "ZAK_RESULT",
    ##"AWA_HD_TOT", "AWA_HD_DWA", "AWA_HD_POC", "AWA_TK_TOT", "AWA_TK_DWA", "AWA_TK_POC", # deze op Null laten
    ]

try:
    from .local_settings import *
except:
    pass

# logging
if not os.path.exists(log_dir): os.mkdir(log_dir)
strftime = datetime.strftime(datetime.now(),"%Y%m%d-%H.%M")
logFileName = 'GeoDyn_{}.log'.format(strftime)
logFile = os.path.join(log_dir,logFileName)
logging.basicConfig(filename=logFile, level=LOGGING_LEVEL)
logging.getLogger().setLevel(LOGGING_LEVEL)
qgis_warnings_log = os.path.join(log_dir,'qgis_warnings.log')


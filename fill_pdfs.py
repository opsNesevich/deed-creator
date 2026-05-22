#!/usr/bin/env python3
"""
NJ Deed PDF form filler using pikepdf.
Usage: python3 fill_pdfs.py <cmd> <json_data> <templates_dir> <output_path>
"""
import sys, json, os, re
import pikepdf
from pikepdf import Name

DEFAULT_DA = '/Helv 9 Tf 0 g'

NJ_MUNI_CODES = {
    'ABSECON|ATLANTIC':'0101','ATLANTIC CITY|ATLANTIC':'0102','BRIGANTINE|ATLANTIC':'0103',
    'BUENA|ATLANTIC':'0104','BUENA VISTA|ATLANTIC':'0105','CORBIN CITY|ATLANTIC':'0106',
    'EGG HARBOR CITY|ATLANTIC':'0107','EGG HARBOR|ATLANTIC':'0108','ESTELL MANOR|ATLANTIC':'0109',
    'FOLSOM|ATLANTIC':'0110','GALLOWAY|ATLANTIC':'0111','HAMILTON|ATLANTIC':'0112',
    'HAMMONTON|ATLANTIC':'0113','LINWOOD|ATLANTIC':'0114','LONGPORT|ATLANTIC':'0115',
    'MARGATE CITY|ATLANTIC':'0116','MULLICA|ATLANTIC':'0117','NORTHFIELD|ATLANTIC':'0118',
    'PLEASANTVILLE|ATLANTIC':'0119','PORT REPUBLIC|ATLANTIC':'0120','SOMERS POINT|ATLANTIC':'0121',
    'VENTNOR CITY|ATLANTIC':'0122','WEYMOUTH|ATLANTIC':'0123',
    'ALLENDALE|BERGEN':'0201','ALPINE|BERGEN':'0202','BERGENFIELD|BERGEN':'0203',
    'BOGOTA|BERGEN':'0204','CARLSTADT|BERGEN':'0205','CLIFFSIDE PARK|BERGEN':'0206',
    'CLOSTER|BERGEN':'0207','CRESSKILL|BERGEN':'0208','DEMAREST|BERGEN':'0209',
    'DUMONT|BERGEN':'0210','ELMWOOD PARK|BERGEN':'0211','EAST RUTHERFORD|BERGEN':'0212',
    'E RUTHERFORD|BERGEN':'0212','EDGEWATER|BERGEN':'0213','EMERSON|BERGEN':'0214',
    'ENGLEWOOD|BERGEN':'0215','ENGLEWOOD CLIFFS|BERGEN':'0216','FAIR LAWN|BERGEN':'0217',
    'FAIRLAWN|BERGEN':'0217','FAIRVIEW|BERGEN':'0218','FORT LEE|BERGEN':'0219',
    'FRANKLIN LAKES|BERGEN':'0220','GARFIELD|BERGEN':'0221','GLEN ROCK|BERGEN':'0222',
    'HACKENSACK|BERGEN':'0223','HARRINGTON PARK|BERGEN':'0224','HASBROUCK HEIGHTS|BERGEN':'0225',
    'HAWORTH|BERGEN':'0226','HILLSDALE|BERGEN':'0227','HOHOKUS|BERGEN':'0228',
    'LEONIA|BERGEN':'0229','LITTLE FERRY|BERGEN':'0230','LODI|BERGEN':'0231',
    'LYNDHURST|BERGEN':'0232','MAHWAH|BERGEN':'0233','MAYWOOD|BERGEN':'0234',
    'MIDLAND PARK|BERGEN':'0235','MONTVALE|BERGEN':'0236','MOONACHIE|BERGEN':'0237',
    'NEW MILFORD|BERGEN':'0238','NORTH ARLINGTON|BERGEN':'0239','NORTHVALE|BERGEN':'0240',
    'NORWOOD|BERGEN':'0241','OAKLAND|BERGEN':'0242','OLD TAPPAN|BERGEN':'0243',
    'ORADELL|BERGEN':'0244','PALISADES PARK|BERGEN':'0245','PARAMUS|BERGEN':'0246',
    'PARK RIDGE|BERGEN':'0247','RAMSEY|BERGEN':'0248','RIDGEFIELD|BERGEN':'0249',
    'RIDGEFIELD PARK|BERGEN':'0250','RIDGEWOOD|BERGEN':'0251','RIVER EDGE|BERGEN':'0252',
    'RIVEREDGE|BERGEN':'0252','RIVER VALE|BERGEN':'0253','RIVERVALE|BERGEN':'0253',
    'ROCHELLE PARK|BERGEN':'0254','ROCKLEIGH|BERGEN':'0255','RUTHERFORD|BERGEN':'0256',
    'SADDLE BROOK|BERGEN':'0257','SADDLE RIVER|BERGEN':'0258','SOUTH HACKENSACK|BERGEN':'0259',
    'SO HACKENSACK|BERGEN':'0259','TEANECK|BERGEN':'0260','TENAFLY|BERGEN':'0261',
    'TETERBORO|BERGEN':'0262','UPPER SADDLE RIVER|BERGEN':'0263','WALDWICK|BERGEN':'0264',
    'WALLINGTON|BERGEN':'0265','WASHINGTON|BERGEN':'0266','WESTWOOD|BERGEN':'0267',
    'WOODCLIFF LAKE|BERGEN':'0268','WOOD RIDGE|BERGEN':'0269','WYCKOFF|BERGEN':'0270',
    'BASS RIVER|BURLINGTON':'0301','BEVERLY|BURLINGTON':'0302','BORDENTOWN CITY|BURLINGTON':'0303',
    'BORDENTOWN|BURLINGTON':'0304','BURLINGTON CITY|BURLINGTON':'0305','BURLINGTON|BURLINGTON':'0306',
    'CHESTERFIELD|BURLINGTON':'0307','CINNAMINSON|BURLINGTON':'0308','DELANCO|BURLINGTON':'0309',
    'DELRAN|BURLINGTON':'0310','EASTAMPTON|BURLINGTON':'0311','EDGEWATER PARK|BURLINGTON':'0312',
    'EVESHAM|BURLINGTON':'0313','FIELDSBORO|BURLINGTON':'0314','FLORENCE|BURLINGTON':'0315',
    'HAINESPORT|BURLINGTON':'0316','LUMBERTON|BURLINGTON':'0317','MANSFIELD|BURLINGTON':'0318',
    'MAPLE SHADE|BURLINGTON':'0319','MEDFORD|BURLINGTON':'0320','MEDFORD LAKES|BURLINGTON':'0321',
    'MOORESTOWN|BURLINGTON':'0322','MOUNT HOLLY|BURLINGTON':'0323','MT HOLLY|BURLINGTON':'0323',
    'MOUNT LAUREL|BURLINGTON':'0324','MT LAUREL|BURLINGTON':'0324','NEW HANOVER|BURLINGTON':'0325',
    'NORTH HANOVER|BURLINGTON':'0326','NO HANOVER|BURLINGTON':'0326','PALMYRA|BURLINGTON':'0327',
    'PEMBERTON BORO|BURLINGTON':'0328','PEMBERTON|BURLINGTON':'0329','RIVERSIDE|BURLINGTON':'0330',
    'RIVERTON|BURLINGTON':'0331','SHAMONG|BURLINGTON':'0332','SOUTHAMPTON|BURLINGTON':'0333',
    'SPRINGFIELD|BURLINGTON':'0334','TABERNACLE|BURLINGTON':'0335','WASHINGTON|BURLINGTON':'0336',
    'WESTAMPTON|BURLINGTON':'0337','WILLINGBORO|BURLINGTON':'0338','WOODLAND|BURLINGTON':'0339',
    'WRIGHTSTOWN|BURLINGTON':'0340',
    'AUDUBON|CAMDEN':'0401','AUDUBON PARK|CAMDEN':'0402','BARRINGTON|CAMDEN':'0403',
    'BELLMAWR|CAMDEN':'0404','BERLIN BORO|CAMDEN':'0405','BERLIN|CAMDEN':'0406',
    'BROOKLAWN|CAMDEN':'0407','CAMDEN|CAMDEN':'0408','CHERRY HILL|CAMDEN':'0409',
    'CHESILHURST|CAMDEN':'0410','CLEMENTON|CAMDEN':'0411','COLLINGSWOOD|CAMDEN':'0412',
    'GIBBSBORO|CAMDEN':'0413','GLOUCESTER CITY|CAMDEN':'0414','GLOUCESTER|CAMDEN':'0415',
    'HADDON|CAMDEN':'0416','HADDONFIELD|CAMDEN':'0417','HADDON HEIGHTS|CAMDEN':'0418',
    'HI NELLA|CAMDEN':'0419','LAUREL SPRINGS|CAMDEN':'0420','LAWNSIDE|CAMDEN':'0421',
    'LINDENWOLD|CAMDEN':'0422','MAGNOLIA|CAMDEN':'0423','MERCHANTVILLE|CAMDEN':'0424',
    'MOUNT EPHRAIM|CAMDEN':'0425','OAKLYN|CAMDEN':'0426','PENNSAUKEN|CAMDEN':'0427',
    'PINE HILL|CAMDEN':'0428','RUNNEMEDE|CAMDEN':'0430','SOMERDALE|CAMDEN':'0431',
    'STRATFORD|CAMDEN':'0432','TAVISTOCK|CAMDEN':'0433','VOORHEES|CAMDEN':'0434',
    'WATERFORD|CAMDEN':'0435','WINSLOW|CAMDEN':'0436','WOODLYNNE|CAMDEN':'0437',
    'AVALON|CAPE MAY':'0501','CAPE MAY CITY|CAPE MAY':'0502','CAPE MAY POINT|CAPE MAY':'0503',
    'DENNIS|CAPE MAY':'0504','LOWER|CAPE MAY':'0505','MIDDLE|CAPE MAY':'0506',
    'NORTH WILDWOOD|CAPE MAY':'0507','OCEAN CITY|CAPE MAY':'0508','SEA ISLE CITY|CAPE MAY':'0509',
    'STONE HARBOR|CAPE MAY':'0510','UPPER|CAPE MAY':'0511','WEST CAPE MAY|CAPE MAY':'0512',
    'WEST WILDWOOD|CAPE MAY':'0513','WILDWOOD|CAPE MAY':'0514','WILDWOOD CREST|CAPE MAY':'0515',
    'WOODBINE|CAPE MAY':'0516',
    'BRIDGETON|CUMBERLAND':'0601','COMMERCIAL|CUMBERLAND':'0602','DEERFIELD|CUMBERLAND':'0603',
    'DOWNE|CUMBERLAND':'0604','FAIRFIELD|CUMBERLAND':'0605','GREENWICH|CUMBERLAND':'0606',
    'HOPEWELL|CUMBERLAND':'0607','LAWRENCE|CUMBERLAND':'0608','MAURICE RIVER|CUMBERLAND':'0609',
    'MILLVILLE|CUMBERLAND':'0610','SHILOH|CUMBERLAND':'0611','STOW CREEK|CUMBERLAND':'0612',
    'UPPER DEERFIELD|CUMBERLAND':'0613','VINELAND|CUMBERLAND':'0614',
    'BELLEVILLE|ESSEX':'0701','BLOOMFIELD|ESSEX':'0702','CALDWELL|ESSEX':'0703',
    'CEDAR GROVE|ESSEX':'0704','EAST ORANGE|ESSEX':'0705','ESSEX FELLS|ESSEX':'0706',
    'FAIRFIELD|ESSEX':'0707','GLEN RIDGE|ESSEX':'0708','IRVINGTON|ESSEX':'0709',
    'LIVINGSTON|ESSEX':'0710','MAPLEWOOD|ESSEX':'0711','MILLBURN|ESSEX':'0712',
    'MONTCLAIR|ESSEX':'0713','NEWARK|ESSEX':'0714','NORTH CALDWELL|ESSEX':'0715',
    'NUTLEY|ESSEX':'0716','ORANGE|ESSEX':'0717','ROSELAND|ESSEX':'0718',
    'SOUTH ORANGE|ESSEX':'0719','VERONA|ESSEX':'0720','WEST CALDWELL|ESSEX':'0721',
    'WEST ORANGE|ESSEX':'0722',
    'CLAYTON|GLOUCESTER':'0801','DEPTFORD|GLOUCESTER':'0802','EAST GREENWICH|GLOUCESTER':'0803',
    'ELK|GLOUCESTER':'0804','FRANKLIN|GLOUCESTER':'0805','GLASSBORO|GLOUCESTER':'0806',
    'GREENWICH|GLOUCESTER':'0807','HARRISON|GLOUCESTER':'0808','LOGAN|GLOUCESTER':'0809',
    'MANTUA|GLOUCESTER':'0810','MONROE|GLOUCESTER':'0811','NATIONAL PARK|GLOUCESTER':'0812',
    'NEWFIELD|GLOUCESTER':'0813','PAULSBORO|GLOUCESTER':'0814','PITMAN|GLOUCESTER':'0815',
    'SOUTH HARRISON|GLOUCESTER':'0816','SO HARRISON|GLOUCESTER':'0816',
    'SWEDESBORO|GLOUCESTER':'0817','WASHINGTON|GLOUCESTER':'0818','WENONAH|GLOUCESTER':'0819',
    'WEST DEPTFORD|GLOUCESTER':'0820','WESTVILLE|GLOUCESTER':'0821','WOODBURY|GLOUCESTER':'0822',
    'WOODBURY HEIGHTS|GLOUCESTER':'0823','WOOLWICH|GLOUCESTER':'0824',
    'BAYONNE|HUDSON':'0901','EAST NEWARK|HUDSON':'0902','GUTTENBERG|HUDSON':'0903',
    'HARRISON|HUDSON':'0904','HOBOKEN|HUDSON':'0905','JERSEY CITY|HUDSON':'0906',
    'KEARNY|HUDSON':'0907','NORTH BERGEN|HUDSON':'0908','SECAUCUS|HUDSON':'0909',
    'UNION CITY|HUDSON':'0910','WEEHAWKEN|HUDSON':'0911','WEST NEW YORK|HUDSON':'0912',
    'ALEXANDRIA|HUNTERDON':'1001','BETHLEHEM|HUNTERDON':'1002','BLOOMSBURY|HUNTERDON':'1003',
    'CALIFON|HUNTERDON':'1004','CLINTON TOWN|HUNTERDON':'1005','CLINTON|HUNTERDON':'1006',
    'DELAWARE|HUNTERDON':'1007','EAST AMWELL|HUNTERDON':'1008','FLEMINGTON|HUNTERDON':'1009',
    'FRANKLIN|HUNTERDON':'1010','FRENCHTOWN|HUNTERDON':'1011','GLEN GARDNER|HUNTERDON':'1012',
    'HAMPTON|HUNTERDON':'1013','HIGH BRIDGE|HUNTERDON':'1014','HOLLAND|HUNTERDON':'1015',
    'KINGWOOD|HUNTERDON':'1016','LAMBERTVILLE|HUNTERDON':'1017','LEBANON BORO|HUNTERDON':'1018',
    'LEBANON|HUNTERDON':'1019','MILFORD|HUNTERDON':'1020','RARITAN|HUNTERDON':'1021',
    'READINGTON|HUNTERDON':'1022','STOCKTON|HUNTERDON':'1023','TEWKSBURY|HUNTERDON':'1024',
    'UNION|HUNTERDON':'1025','WEST AMWELL|HUNTERDON':'1026',
    'EAST WINDSOR|MERCER':'1101','EWING|MERCER':'1102','HAMILTON|MERCER':'1103',
    'HIGHTSTOWN|MERCER':'1104','HOPEWELL BORO|MERCER':'1105','HOPEWELL|MERCER':'1106',
    'LAWRENCE|MERCER':'1107','PENNINGTON|MERCER':'1108','TRENTON|MERCER':'1111',
    'ROBBINSVILLE|MERCER':'1112','WEST WINDSOR|MERCER':'1113','PRINCETON|MERCER':'1114',
    'CARTERET|MIDDLESEX':'1201','CRANBURY|MIDDLESEX':'1202','DUNELLEN|MIDDLESEX':'1203',
    'EAST BRUNSWICK|MIDDLESEX':'1204','EDISON|MIDDLESEX':'1205','HELMETTA|MIDDLESEX':'1206',
    'HIGHLAND PARK|MIDDLESEX':'1207','JAMESBURG|MIDDLESEX':'1208','METUCHEN|MIDDLESEX':'1209',
    'MIDDLESEX|MIDDLESEX':'1210','MILLTOWN|MIDDLESEX':'1211','MONROE|MIDDLESEX':'1212',
    'NEW BRUNSWICK|MIDDLESEX':'1213','NORTH BRUNSWICK|MIDDLESEX':'1214','OLD BRIDGE|MIDDLESEX':'1215',
    'PERTH AMBOY|MIDDLESEX':'1216','PISCATAWAY|MIDDLESEX':'1217','PLAINSBORO|MIDDLESEX':'1218',
    'SAYREVILLE|MIDDLESEX':'1219','SOUTH AMBOY|MIDDLESEX':'1220','SOUTH BRUNSWICK|MIDDLESEX':'1221',
    'SOUTH PLAINFIELD|MIDDLESEX':'1222','SOUTH RIVER|MIDDLESEX':'1223','SPOTSWOOD|MIDDLESEX':'1224',
    'WOODBRIDGE|MIDDLESEX':'1225',
    'ABERDEEN|MONMOUTH':'1301','ALLENHURST|MONMOUTH':'1302','ALLENTOWN|MONMOUTH':'1303',
    'ASBURY PARK|MONMOUTH':'1304','ATLANTIC HIGHLANDS|MONMOUTH':'1305','AVON|MONMOUTH':'1306',
    'BELMAR|MONMOUTH':'1307','BRADLEY BEACH|MONMOUTH':'1308','BRIELLE|MONMOUTH':'1309',
    'COLTS NECK|MONMOUTH':'1310','DEAL|MONMOUTH':'1311','EATONTOWN|MONMOUTH':'1312',
    'ENGLISHTOWN|MONMOUTH':'1313','FAIR HAVEN|MONMOUTH':'1314','FARMINGDALE|MONMOUTH':'1315',
    'FREEHOLD BORO|MONMOUTH':'1316','FREEHOLD|MONMOUTH':'1317','HAZLET|MONMOUTH':'1318',
    'HIGHLANDS|MONMOUTH':'1319','HOLMDEL|MONMOUTH':'1320','HOWELL|MONMOUTH':'1321',
    'INTERLAKEN|MONMOUTH':'1322','KEANSBURG|MONMOUTH':'1323','KEYPORT|MONMOUTH':'1324',
    'LITTLE SILVER|MONMOUTH':'1325','LOCH ARBOUR|MONMOUTH':'1326','LONG BRANCH|MONMOUTH':'1327',
    'MANALAPAN|MONMOUTH':'1328','MANASQUAN|MONMOUTH':'1329','MARLBORO|MONMOUTH':'1330',
    'MATAWAN|MONMOUTH':'1331','MIDDLETOWN|MONMOUTH':'1332','MILLSTONE|MONMOUTH':'1333',
    'MONMOUTH BEACH|MONMOUTH':'1334','NEPTUNE|MONMOUTH':'1335','NEPTUNE CITY|MONMOUTH':'1336',
    'OCEAN|MONMOUTH':'1337','OCEANPORT|MONMOUTH':'1338','RED BANK|MONMOUTH':'1339',
    'ROOSEVELT|MONMOUTH':'1340','RUMSON|MONMOUTH':'1341','SEA BRIGHT|MONMOUTH':'1342',
    'SEA GIRT|MONMOUTH':'1343','SHREWSBURY BORO|MONMOUTH':'1344','SHREWSBURY|MONMOUTH':'1345',
    'LAKE COMO|MONMOUTH':'1346','SPRING LAKE BORO|MONMOUTH':'1347',
    'SPRING LAKE HEIGHTS|MONMOUTH':'1348','TINTON FALLS|MONMOUTH':'1349',
    'UNION BEACH|MONMOUTH':'1350','UPPER FREEHOLD|MONMOUTH':'1351','WALL|MONMOUTH':'1352',
    'WEST LONG BRANCH|MONMOUTH':'1353',
    'BOONTON TOWN|MORRIS':'1401','BOONTON|MORRIS':'1402','BUTLER|MORRIS':'1403',
    'CHATHAM BORO|MORRIS':'1404','CHATHAM|MORRIS':'1405','CHESTER BORO|MORRIS':'1406',
    'CHESTER|MORRIS':'1407','DENVILLE|MORRIS':'1408','DOVER|MORRIS':'1409',
    'EAST HANOVER|MORRIS':'1410','FLORHAM PARK|MORRIS':'1411','HANOVER|MORRIS':'1412',
    'HARDING|MORRIS':'1413','JEFFERSON|MORRIS':'1414','KINNELON|MORRIS':'1415',
    'LINCOLN PARK|MORRIS':'1416','MADISON|MORRIS':'1417','MENDHAM BORO|MORRIS':'1418',
    'MENDHAM|MORRIS':'1419','MINE HILL|MORRIS':'1420','MONTVILLE|MORRIS':'1421',
    'MORRIS|MORRIS':'1422','MORRIS PLAINS|MORRIS':'1423','MORRISTOWN|MORRIS':'1424',
    'MOUNTAIN LAKES|MORRIS':'1425','MOUNT ARLINGTON|MORRIS':'1426','MOUNT OLIVE|MORRIS':'1427',
    'NETCONG|MORRIS':'1428','PARSIPPANY|MORRIS':'1429','PARSIPPANY-TROY HILLS|MORRIS':'1429',
    'LONG HILL|MORRIS':'1430','PEQUANNOCK|MORRIS':'1431','RANDOLPH|MORRIS':'1432',
    'RIVERDALE|MORRIS':'1433','ROCKAWAY BORO|MORRIS':'1434','ROCKAWAY|MORRIS':'1435',
    'ROXBURY|MORRIS':'1436','VICTORY GARDENS|MORRIS':'1437','WASHINGTON|MORRIS':'1438',
    'WHARTON|MORRIS':'1439',
    'BARNEGAT|OCEAN':'1501','BARNEGAT LIGHT|OCEAN':'1502','BAY HEAD|OCEAN':'1503',
    'BEACH HAVEN|OCEAN':'1504','BEACHWOOD|OCEAN':'1505','BERKELEY|OCEAN':'1506',
    'BRICK|OCEAN':'1507','TOMS RIVER|OCEAN':'1508','EAGLESWOOD|OCEAN':'1509',
    'HARVEY CEDARS|OCEAN':'1510','ISLAND HEIGHTS|OCEAN':'1511','JACKSON|OCEAN':'1512',
    'LACEY|OCEAN':'1513','LAKEHURST|OCEAN':'1514','LAKEWOOD|OCEAN':'1515',
    'LAVALLETTE|OCEAN':'1516','LITTLE EGG HARBOR|OCEAN':'1517','LONG BEACH|OCEAN':'1518',
    'MANCHESTER|OCEAN':'1519','MANTOLOKING|OCEAN':'1520','OCEAN|OCEAN':'1521',
    'OCEAN GATE|OCEAN':'1522','PINE BEACH|OCEAN':'1523','PLUMSTED|OCEAN':'1524',
    'POINT PLEASANT BORO|OCEAN':'1525','POINT PLEASANT BEACH|OCEAN':'1526',
    'PT PLEASANT BEACH|OCEAN':'1526','SEASIDE HEIGHTS|OCEAN':'1527','SEASIDE PARK|OCEAN':'1528',
    'SHIP BOTTOM|OCEAN':'1529','SOUTH TOMS RIVER|OCEAN':'1530','STAFFORD|OCEAN':'1531',
    'SURF CITY|OCEAN':'1532','TUCKERTON|OCEAN':'1533',
    'BLOOMINGDALE|PASSAIC':'1601','CLIFTON|PASSAIC':'1602','HALEDON|PASSAIC':'1603',
    'HAWTHORNE|PASSAIC':'1604','LITTLE FALLS|PASSAIC':'1605','NORTH HALEDON|PASSAIC':'1606',
    'PASSAIC|PASSAIC':'1607','PATERSON|PASSAIC':'1608','POMPTON LAKES|PASSAIC':'1609',
    'PROSPECT PARK|PASSAIC':'1610','RINGWOOD|PASSAIC':'1611','TOTOWA|PASSAIC':'1612',
    'WANAQUE|PASSAIC':'1613','WAYNE|PASSAIC':'1614','WEST MILFORD|PASSAIC':'1615',
    'WOODLAND PARK|PASSAIC':'1616',
    'ALLOWAY|SALEM':'1701','CARNEYS POINT|SALEM':'1702','ELMER|SALEM':'1703',
    'ELSINBORO|SALEM':'1704','LOWER ALLOWAY CREEK|SALEM':'1705','MANNINGTON|SALEM':'1706',
    'OLDMANS|SALEM':'1707','PENNS GROVE|SALEM':'1708','PENNSVILLE|SALEM':'1709',
    'PILESGROVE|SALEM':'1710','PITTSGROVE|SALEM':'1711','QUINTON|SALEM':'1712',
    'SALEM|SALEM':'1713','UPPER PITTSGROVE|SALEM':'1714','WOODSTOWN|SALEM':'1715',
    'BEDMINSTER|SOMERSET':'1801','BERNARDS|SOMERSET':'1802','BERNARDSVILLE|SOMERSET':'1803',
    'BOUND BROOK|SOMERSET':'1804','BRANCHBURG|SOMERSET':'1805','BRIDGEWATER|SOMERSET':'1806',
    'FAR HILLS|SOMERSET':'1807','FRANKLIN|SOMERSET':'1808','GREEN BROOK|SOMERSET':'1809',
    'HILLSBOROUGH|SOMERSET':'1810','MANVILLE|SOMERSET':'1811','MILLSTONE|SOMERSET':'1812',
    'MONTGOMERY|SOMERSET':'1813','NORTH PLAINFIELD|SOMERSET':'1814',
    'PEAPACK GLADSTONE|SOMERSET':'1815','RARITAN|SOMERSET':'1816','ROCKY HILL|SOMERSET':'1817',
    'SOMERVILLE|SOMERSET':'1818','SOUTH BOUND BROOK|SOMERSET':'1819','SO BOUND BROOK|SOMERSET':'1819',
    'WARREN|SOMERSET':'1820','WATCHUNG|SOMERSET':'1821',
    'ANDOVER BORO|SUSSEX':'1901','ANDOVER|SUSSEX':'1902','BRANCHVILLE|SUSSEX':'1903',
    'BYRAM|SUSSEX':'1904','FRANKFORD|SUSSEX':'1905','FRANKLIN|SUSSEX':'1906',
    'FREDON|SUSSEX':'1907','GREEN|SUSSEX':'1908','HAMBURG|SUSSEX':'1909',
    'HAMPTON|SUSSEX':'1910','HARDYSTON|SUSSEX':'1911','HOPATCONG|SUSSEX':'1912',
    'LAFAYETTE|SUSSEX':'1913','MONTAGUE|SUSSEX':'1914','NEWTON|SUSSEX':'1915',
    'OGDENSBURG|SUSSEX':'1916','SANDYSTON|SUSSEX':'1917','SPARTA|SUSSEX':'1918',
    'STANHOPE|SUSSEX':'1919','STILLWATER|SUSSEX':'1920','SUSSEX|SUSSEX':'1921',
    'VERNON|SUSSEX':'1922','WALPACK|SUSSEX':'1923','WANTAGE|SUSSEX':'1924',
    'BERKELEY HEIGHTS|UNION':'2001','CLARK|UNION':'2002','CRANFORD|UNION':'2003',
    'ELIZABETH|UNION':'2004','FANWOOD|UNION':'2005','GARWOOD|UNION':'2006',
    'HILLSIDE|UNION':'2007','KENILWORTH|UNION':'2008','LINDEN|UNION':'2009',
    'MOUNTAINSIDE|UNION':'2010','NEW PROVIDENCE|UNION':'2011','PLAINFIELD|UNION':'2012',
    'RAHWAY|UNION':'2013','ROSELLE|UNION':'2014','ROSELLE PARK|UNION':'2015',
    'SCOTCH PLAINS|UNION':'2016','SPRINGFIELD|UNION':'2017','SUMMIT|UNION':'2018',
    'UNION|UNION':'2019','WESTFIELD|UNION':'2020','WINFIELD|UNION':'2021',
    'ALLAMUCHY|WARREN':'2101','ALPHA|WARREN':'2102','BELVIDERE|WARREN':'2103',
    'BLAIRSTOWN|WARREN':'2104','FRANKLIN|WARREN':'2105','FRELINGHUYSEN|WARREN':'2106',
    'GREENWICH|WARREN':'2107','HACKETTSTOWN|WARREN':'2108','HARDWICK|WARREN':'2109',
    'HARMONY|WARREN':'2110','HOPE|WARREN':'2111','INDEPENDENCE|WARREN':'2112',
    'KNOWLTON|WARREN':'2113','LIBERTY|WARREN':'2114','LOPATCONG|WARREN':'2115',
    'MANSFIELD|WARREN':'2116','OXFORD|WARREN':'2117','PHILLIPSBURG|WARREN':'2119',
    'POHATCONG|WARREN':'2120','WASHINGTON BORO|WARREN':'2121','WASHINGTON|WARREN':'2122',
    'WHITE|WARREN':'2123',
}

def lookup_muni_code(municipality, county):
    if not municipality or not county:
        return ''
    suffixes = ['TOWNSHIP', 'BOROUGH', 'CITY', 'TOWN', 'VILLAGE', 'TWP', 'BORO']
    muni_upper = municipality.upper().strip()
    county_upper = county.upper().strip().replace(' COUNTY', '')
    key = f'{muni_upper}|{county_upper}'
    if key in NJ_MUNI_CODES:
        return NJ_MUNI_CODES[key]
    for s in suffixes:
        if muni_upper.endswith(' ' + s):
            stripped = muni_upper[:-len(s)-1].strip()
            key2 = f'{stripped}|{county_upper}'
            if key2 in NJ_MUNI_CODES:
                return NJ_MUNI_CODES[key2]
    return ''

def ensure_municipality_format(municipality):
    if not municipality:
        return municipality
    suffixes = ['Township', 'Borough', 'City', 'Town', 'Village']
    if any(municipality.endswith(s) for s in suffixes):
        return municipality
    return municipality + ' Township'

def parse_addr(addr, fallback_zip=''):
    parts = [p.strip() for p in addr.split(',')]
    street = parts[0] if parts else ''
    city   = parts[1] if len(parts) > 1 else ''
    zip_   = fallback_zip
    if not zip_:
        last = parts[-1] if parts else ''
        m = re.search(r'\b(\d{5})\b', last)
        zip_ = m.group(1) if m else ''
    return street, city, zip_

def set_fields(pdf, text_values, check_on_set, check_on_value=Name('/Yes')):
    def walk(fields):
        for f in fields:
            try:
                ft   = str(f.get('/FT', ''))
                t    = str(f.get('/T',  '')).strip('()')
                kids = f.get('/Kids', None)
                if ft == '/Tx' and t in text_values:
                    f['/V'] = text_values[t]
                    if '/DA' not in f or not str(f.get('/DA', '')):
                        f['/DA'] = DEFAULT_DA
                    if '/AP' in f: del f['/AP']
                elif ft == '/Btn' and t in check_on_set:
                    f['/V'] = check_on_value
                    f['/AS'] = check_on_value
                if kids: walk(kids)
            except: pass

    if '/AcroForm' in pdf.Root and '/Fields' in pdf.Root.AcroForm:
        walk(pdf.Root.AcroForm.Fields)

    for page in pdf.pages:
        if '/Annots' not in page: continue
        for annot in page['/Annots']:
            try:
                if str(annot.get('/Subtype','')) != '/Widget': continue
                fn = str(annot.get('/T','')).strip('()')
                ft = str(annot.get('/FT',''))
                if ft == '/Tx' and fn in text_values:
                    annot['/V'] = text_values[fn]
                    if '/DA' not in annot or not str(annot.get('/DA', '')):
                        annot['/DA'] = DEFAULT_DA
                    if '/AP' in annot: del annot['/AP']
                elif ft == '/Btn' and fn in check_on_set:
                    annot['/V'] = check_on_value
                    annot['/AS'] = check_on_value
            except: pass

def fill_residency(data, template_path, output_path):
    pdf = pikepdf.open(template_path)
    grantor      = data.get('grantor', '')
    grantor2     = data.get('grantor2', '')
    relationship = data.get('relationship', '')
    if grantor2:
        rel = (', ' + relationship) if relationship else ''
        name_field = f"{grantor} and {grantor2}{rel}"
    else:
        name_field = grantor
    g_street, g_city, g_zip = parse_addr(data.get('grantorAddr',''), data.get('grantorZip',''))
    p_street, p_city_auto, p_zip_auto = parse_addr(data.get('propAddr',''))
    prop_city = data.get('propCity', p_city_auto)
    prop_zip  = data.get('propZip',  p_zip_auto)
    text_values = {
        'Name':                            name_field,
        'Add1':                            g_street,
        'City Town Post Office':           g_city,
        'State':                           'NJ',
        'ZIP Code':                        g_zip,
        'Block':                           data.get('block', ''),
        'Lot':                             data.get('lot', ''),
        'Qual':                            data.get('qualifier', ''),
        'Add2':                            p_street,
        'City Town Post Office_2':         prop_city,
        'State_2':                         'NJ',
        'ZIP Code_2':                      prop_zip,
        'Sellers Percentage of Ownership': '100%',
        'Total Consideration':             '1.00',
        'Owners Share of Consideration':   '1.00',
        'Closing Date':                    data.get('signingDate', ''),
    }
    set_fields(pdf, text_values, {'Check Box71a','Check Box72a','Check Box76a'}, Name('/Yes'))
    if '/AcroForm' in pdf.Root:
        if '/DA' not in pdf.Root.AcroForm:
            pdf.Root.AcroForm['/DA'] = DEFAULT_DA
        pdf.Root.AcroForm['/NeedAppearances'] = pikepdf.Boolean(True)
    pdf.save(output_path)
    print(f"GIT/REP-3 saved to {output_path}")

def fill_affidavit(data, template_path, output_path):
    pdf = pikepdf.open(template_path)
    grantor      = data.get('grantor', '')
    municipality = ensure_municipality_format(data.get('municipality', ''))
    county       = data.get('county', 'Burlington')
    county_code  = data.get('countyMunicipalCode', '') or lookup_muni_code(municipality, county)
    p_street, p_city_auto, p_zip_auto = parse_addr(data.get('propAddr',''))
    prop_city = data.get('propCity', p_city_auto)
    prop_zip  = data.get('propZip',  p_zip_auto)
    full_prop_addr = f"{p_street}, {prop_city}, NJ {prop_zip}".strip(', ')
    ssn = data.get('ssn', '')
    ssn_display = f"XXX-XX-{ssn}" if ssn else ''
    text_values = {
        'County':                            'Burlington',
        'County Municipal Code':             county_code,
        'Municipality of Property Location': municipality,
        'Deponent Name':                     grantor,
        'Deponent Title':                    'Grantor',
        'Deed Dated':                        '',
        'Block Number':                      data.get('block', ''),
        'Lot Number':                        data.get('lot', ''),
        'Property Address':                  full_prop_addr,
        'Consideration Amount':              '1.00',
        'Full Exemption From Fee, Line 1':   'For consideration of less than $100.',
        'Grantor Name':                      grantor,
        "Last 3 digits of Grant's SSN":      ssn_display,
        'Grantor Address at Time of Sale':   '',
        'Deponent Address':                  '',
    }
    set_fields(pdf, text_values, {'No prior mortgage'}, Name('/On'))
    if '/AcroForm' in pdf.Root:
        if '/DA' not in pdf.Root.AcroForm:
            pdf.Root.AcroForm['/DA'] = DEFAULT_DA
        pdf.Root.AcroForm['/NeedAppearances'] = pikepdf.Boolean(True)
    pdf.save(output_path)
    print(f"RTF-1 saved to {output_path}")

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("Usage: python3 fill_pdfs.py <cmd> <json_data> <templates_dir> <output_path>", file=sys.stderr)
        sys.exit(1)
    cmd           = sys.argv[1]
    templates_dir = sys.argv[3]
    output_path   = sys.argv[4]
    try:
        data = json.loads(sys.argv[2])
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    template_map = {
        'residency': 'residency-template.pdf',
        'affidavit': 'affidavit-template.pdf',
    }
    if cmd not in template_map:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)
    template = os.path.join(templates_dir, template_map[cmd])
    if not os.path.exists(template):
        print(f"Template not found: {template}", file=sys.stderr)
        sys.exit(1)
    try:
        if cmd == 'residency':
            fill_residency(data, template, output_path)
        else:
            fill_affidavit(data, template, output_path)
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)

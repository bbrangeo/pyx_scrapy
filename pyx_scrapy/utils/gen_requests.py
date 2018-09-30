import logging

import openpyxl

from pyx_scrapy.utils.consts import MetaK

logger = logging.getLogger(__name__)


def xlsx_gen_requests(filename):
    try:
        wb = openpyxl.load_workbook(filename)
        sheet = wb[wb.sheetnames[0]]
        idx = 0
        for row in sheet.rows:
            idx += 1
            if idx == 1:
                continue
            c1, c2, c3, c4 = row

            kwargs = {
                MetaK.PKG: {
                    MetaK.CP_ID: c1.value,
                    MetaK.CP_SONG: c2.value,
                    MetaK.CP_ARTIST: c3.value,
                    MetaK.REL_ID: c4.value,
                }
            }

            yield c4.value, kwargs
    except Exception as ex:
        logger.exception(ex)

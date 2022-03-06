import xml.etree.ElementTree as ET
import subprocess
import pandas as pd
import argparse
import os
import zipfile

from dateutil import parser


def process_health_data():
    thefile = open('./apple_health_export/influx-export.txt', 'w', encoding='utf-8')
    thefile.write('# DML\n')
    thefile.write('# CONTEXT-DATABASE: apple_health\n')
    thefile.write('# CONTEXT-RETENTION-POLICY: default\n')
    read_xml_stream(thefile)


def read_xml_stream(file):
    import_count = 0
    import_errors = 0
    context = ET.iterparse("./apple_health_export/export.xml",)
    partial_iter(context, file, import_count, import_errors)


def partial_iter(context, file, import_count, import_errors):
    record_batch = []
    for event, elem in context:
        if elem.tag.endswith('Record'):
            i = elem.attrib
            columns = ['type', 'sourceName', 'unit', 'value', 'startDate']
            try:
                row = {key: i[key] for key in columns}
                record_batch.append([row['type'], row['sourceName'],row['unit'], row['value'], row['startDate']])
            except KeyError:
                import_errors = import_errors + 1
            import_count = import_count + 1
            if import_count % 50000 == 0:
                print("imported {} entries, skipped {} entries".format(import_count, import_errors))
                append_output(record_batch, file)
                record_batch = []
        elem.clear()
    if len(record_batch) > 0:
        print("will import total {} entries".format(import_count))
        append_output(record_batch, file)
    del context


def append_output(data, file):
    local_data_frame = pd.DataFrame(data=data, columns=['type', 'sourceName', 'unit', 'value', 'startDate'])
    local_data_frame['timestamp'] = local_data_frame['startDate'].apply(lambda x: int(parser.parse(x).timestamp()))
    local_data_frame["timestr"] = [str(local_data_frame["timestamp"][t]) + "000000000" for t in range(len(local_data_frame))]
    for d in range(len(local_data_frame)):
        result = 'record,type={},sourceName="{}" unit="{}",value={} {}'.format(local_data_frame['type'][d],
                                                                               local_data_frame["sourceName"][d].replace("’","").replace(" ","_").replace("'", ""),
                                                                               local_data_frame["unit"][d],
                                                                               local_data_frame["value"][d],
                                                                               local_data_frame["timestr"][d]
                                                                              )
        file.write("%s\n" % result)


def export_to_influx(host, username, password):
    print("clearing influx records for health data") 
    cmd = ['influx', '-username', username, '-password', password, '-host', host, '-execute', "'DELETE from record'", "-database='apple_health'"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.communicate()
    print("adding influx records")
    cmd = ['influx', '-username', username, '-password', password, '-host', host, '-import', '-path=apple_health_export/influx-export.txt', '-precision=ns']
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    o, e = proc.communicate()
    if (proc.returncode != 0):
        raise RuntimeError("Job failed wih status code: {} error: {}".format(proc.returncode, e.decode('utf-8'))) 
    print('Output Complete')
    print('code: ' + str(proc.returncode))


def unzipfile(path):
    print("read and unzip export file")
    file = os.path.join(path, "export.zip")
    with zipfile.ZipFile(file, 'r') as zip:
        zip.extractall(".")
    print("finished unzipping contents")


argparser = argparse.ArgumentParser()
argparser.add_argument("importpath", help="path where health zip has been added")
argparser.add_argument("influxhost", help="influxdb host")
argparser.add_argument("influxuser", help="influxdb username")
argparser.add_argument("influxpass", help="influxdb password")


def main():
    args = argparser.parse_args()
    unzipfile(args.importpath)
    process_health_data()
    export_to_influx(args.influxhost, args.influxuser, args.influxpass)


if __name__ == "__main__":
    main()

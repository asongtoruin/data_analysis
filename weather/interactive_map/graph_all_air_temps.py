#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ftplib import FTP
from io import BytesIO
import json
from multiprocessing import Pool
import os

from midas import MidasData


SOURCE = (
    'Data Source - Met Office (2019): MIDAS Open: UK daily weather observation '
    'data, v201901. Centre for Environmental Data Analysis, 01 March 2019.\n'
    'For more information on these graphs visit ruszkow.ski/posts/weather'
)


def connect_ftp():
    with open('credentials.json', 'r') as creds:
        login_details = json.load(creds)

    ftp = FTP('ftp.ceda.ac.uk')
    ftp.login(**login_details)
    return ftp


def threaded_site(directory, csv_file, folder, sub, sub_pretty):
    ftp = connect_ftp()
    ftp.cwd(directory)
    year = csv_file[-8:-4]
    # Based on https://stackoverflow.com/a/48817105
    download = BytesIO()
    ftp.retrbinary("RETR {}".format(csv_file), download.write)
    download.seek(0)

    # Set up the object
    md = MidasData(download)
    md.data = md.data[md.data['Hour'].between(7, 18)]

    # Quit if we don't have the full 12 hours
    if not md.data['Hour'].nunique() == 12:
        print('Not enough hours:', year)
        return None
    md.data['Mean Temp'] = (
        md.data.groupby('Month')['air_temperature'].transform('mean')
    )

    output_folder = os.path.join('Graphs', folder, sub)
    if not os.path.isdir(output_folder):
        os.makedirs(output_folder)

    md.monthly_ridge_plot(
        hue='Mean Temp', value='air_temperature',
        title=f'{year} Daytime (7am-7pm) Temperatures\nSite: {sub_pretty}',
        hue_label='Mean', value_format=u'{:.2f}\u00b0',
        x_label=u'Temperature (\u00b0C)', attribution=SOURCE,
        output_path=os.path.join(output_folder,
                                 f'{year} Daytime Air Temperatures.png'),
        facet_params=dict(aspect=14, height=.8, xlim=(-15, 30)),
        shape_params=dict(bw=.4),
        outline_params=dict(bw=.4)
    )


if __name__ == '__main__':
    ftp = connect_ftp()

    ftp.cwd(
        'badc/ukmo-midas-open/data/uk-hourly-weather-obs/dataset-version-201901'
    )

    for folder in ftp.nlst():
        if '.' in folder:
            continue
        print(folder)
        ftp.cwd(folder)
        for sub in ftp.nlst():
            sub_pretty = sub.split('_')[-1].replace('-', ' ').title()
            print(sub_pretty)
            ftp.cwd(sub + '/qc-version-1')
            func_args = [
                (ftp.pwd(), csv_file, folder, sub, sub_pretty)
                for csv_file in ftp.nlst()
            ]

            with Pool(processes=4) as pool:
                results = pool.starmap(threaded_site, func_args)

            ftp.cwd('../..')
        ftp.cwd('..')

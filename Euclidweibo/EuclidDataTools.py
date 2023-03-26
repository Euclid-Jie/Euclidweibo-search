# -*- coding: utf-8 -*-
# @Time    : 2023/3/11 10:45
# @Author  : Euclid-Jie
# @File    : EuclidDataTools.py
import os
import pandas as pd


class EuclidCsvTools:
    """
    this class include tools used to precess csv file
    """

    def __init__(self, subFolder: str = None, FileName: str = 'DemoOut.csv'):
        # para init
        self.subFolder = subFolder
        self.FileName = FileName
        self.FullFilePath = None
        self.FullFolderPath = None

    def path_clear(self):
        """
        get the full folder path and full file path
        :return:
        """
        if self.subFolder:
            if '\\' in self.subFolder:
                self.FullFolderPath = os.getcwd() + self.subFolder
            else:
                self.FullFolderPath = os.getcwd() + '\\' + self.subFolder
        else:
            self.FullFolderPath = os.getcwd()
        self.FullFilePath = os.path.join(self.FullFolderPath, self.FileName)
        print('文件将存储在: {}'.format(self.FullFilePath))

    def saveCsvFile(self, df, append=False):
        """
        save data to csv
        :param df: pd.DataFrame
        :param append: True(append save) or False(overwrite)
        :return:
        """
        if not self.FullFilePath:
            self.path_clear()

        if os.path.exists(self.FullFolderPath):
            # folder path exit
            if append:
                self.writeDf2Csv(df, self.FullFilePath)
            else:
                df.to_csv(self.FullFilePath, encoding='utf_8_sig', index=False)
        else:
            # no dir exists then make one and save data to csv
            os.mkdir(self.FullFolderPath)
            if append:
                self.writeDf2Csv(df, self.FullFilePath)
            else:
                df.to_csv(self.FullFilePath, encoding='utf_8_sig', index=False)

    @classmethod
    def writeDf2Csv(cls, df, FullFilePath):
        if not os.path.exists(FullFilePath):
            # write out a new file with header
            df.to_csv(FullFilePath, mode='w', encoding='utf_8_sig', header=True, index=False)
        else:
            # write after a exist file without header
            df.to_csv(FullFilePath, mode='a', encoding='utf_8_sig', header=False, index=False)


class CsvClient(EuclidCsvTools):
    def __init__(self, subFolder: str = None, FileName: str = 'DemoOut.csv'):
        """
        :param subFolder:
        :param FileName:
        """
        super().__init__(subFolder=subFolder, FileName=FileName)
        if FileName[-4:] != '.csv':
            self.FileName = self.FileName + '.csv'
        self.path_clear()

    def insert_one(self, data):
        if isinstance(data, dict):
            data = pd.DataFrame([data])
        elif isinstance(data, pd.DataFrame):
            pass
        else:
            raise TypeError("传入参数仅支出dict和pd.DataFrame")
        self.saveCsvFile(df=data, append=True)

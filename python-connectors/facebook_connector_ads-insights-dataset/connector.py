# This file is the actual code for the custom Python dataset facebook_connector_ads-insights-dataset

# import the base class for the custom dataset
from six.moves import xrange
from dataiku.connector import Connector

import facebookads
from facebookads.api import FacebookAdsApi
from facebookads import FacebookSession
from facebookads.adobjects.adaccount import AdAccount
from facebookads.adobjects.adreportrun import AdReportRun

import time
import pandas as pd

"""
A custom Python dataset is a subclass of Connector.

The parameters it expects and some flags to control its handling by DSS are
specified in the connector.json file.

Note: the name of the class itself is not relevant.
"""
class MyConnector(Connector):

    def __init__(self, config, plugin_config):
        """
        The configuration parameters set up by the user in the settings tab of the
        dataset are passed as a json object 'config' to the constructor.
        The static configuration parameters set up by the developer in the optional
        file settings.json at the root of the plugin directory are passed as a json
        object 'plugin_config' to the constructor
        """
        Connector.__init__(self, config, plugin_config)  # pass the parameters to the base class

        # perform some more initialization
        self.date_start = self.config.get("date_start", "defaultValue")
        self.date_stop = self.config.get("date_stop", "defaultValue")
        self.fields = [
            'date_start',
            'date_stop',
            'campaign_name',
            'adset_name',
            'ad_name',
            'reach',
            'impressions',
            'frequency',
            'spend',
            'clicks'
        ]
        self.level = self.config.get("level", "defaultValue")
        self.breakdowns = self.config.get("breakdowns", "defaultValue")
        self.ad_account_id = self.config.get("ad_account_id", "defaultValue")
        self.access_token = self.config.get("access_token")
        
    def get_read_schema(self):
        """
        Returns the schema that this connector generates when returning rows.

        The returned schema may be None if the schema is not known in advance.
        In that case, the dataset schema will be infered from the first rows.

        If you do provide a schema here, all columns defined in the schema
        will always be present in the output (with None value),
        even if you don't provide a value in generate_rows

        The schema must be a dict, with a single key: "columns", containing an array of
        {'name':name, 'type' : type}.

        Example:
            return {"columns" : [ {"name": "col1", "type" : "string"}, {"name" :"col2", "type" : "float"}]}

        Supported types are: string, int, bigint, float, double, date, boolean
        """

        # In this example, we don't specify a schema here, so DSS will infer the schema
        # from the columns actually returned by the generate_rows method
        return None


    def generate_rows(self, dataset_schema=None, dataset_partitioning=None,
                            partition_id=None, records_limit = -1):
        """
        The main reading method.

        Returns a generator over the rows of the dataset (or partition)
        Each yielded row must be a dictionary, indexed by column name.

        The dataset schema and partitioning are given for information purpose.
        """
        FacebookAdsApi.init(access_token=self.access_token, api_version='v3.3')
        
        params = {
            'time_range': {
                'since': self.date_start, 
                'until': self.date_stop
                }, 
            'breakdowns': self.breakdowns,
            'level': self.level,
            'time_increment': 1
        }
        
        async_job = AdAccount(self.ad_account_id).get_insights_async(
            fields=self.fields,
            params=params
        )
        
        while not async_job.remote_read().get("async_status")=='Job Completed':
            time.sleep(1)
        
        resulting_adaccount_lines = async_job.get_result()
        
        for line in resulting_adaccount_lines:
            yield line.export_data()


    def get_writer(self, dataset_schema=None, dataset_partitioning=None,
                         partition_id=None):
        """
        Returns a writer object to write in the dataset (or in a partition).

        The dataset_schema given here will match the the rows given to the writer below.

        Note: the writer is responsible for clearing the partition, if relevant.
        """
        raise Exception("Unimplemented")


    def get_partitioning(self):
        """
        Return the partitioning schema that the connector defines.
        """
        raise Exception("Unimplemented")


    def list_partitions(self, partitioning):
        """Return the list of partitions for the partitioning scheme
        passed as parameter"""
        return []


    def partition_exists(self, partitioning, partition_id):
        """Return whether the partition passed as parameter exists

        Implementation is only required if the corresponding flag is set to True
        in the connector definition
        """
        raise Exception("unimplemented")


    def get_records_count(self, partitioning=None, partition_id=None):
        """
        Returns the count of records for the dataset (or a partition).

        Implementation is only required if the corresponding flag is set to True
        in the connector definition
        """
        raise Exception("unimplemented")


class CustomDatasetWriter(object):
    def __init__(self):
        pass

    def write_row(self, row):
        """
        Row is a tuple with N + 1 elements matching the schema passed to get_writer.
        The last element is a dict of columns not found in the schema
        """
        raise Exception("unimplemented")

    def close(self):
        pass
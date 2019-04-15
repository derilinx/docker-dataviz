from SPARQLWrapper import SPARQLWrapper, JSON, POST, DIGEST
import json
import os
import urllib.request
import sys

sparql = SPARQLWrapper("https://virtuoso.losd-dck.staging.derilinx.com/sparql")
sparql.setCredentials(str(os.environ['sparql_username']), str(os.environ['sparql_pwd']))

class ItalyUnemploymentRate:

    def __init__(self, default_uri="http://unemp_italy_nuts.staging.derilinx.com", default_format=JSON):
        self.sparql = sparql
        self.sparql.addDefaultGraph(default_uri)
        self.sparql.setReturnFormat(default_format)
        self.sparql.setHTTPAuth(DIGEST)

    def _data_preprocess(self, object, nuts):
        """ e3, e4 .. etc are the qualification code from dataset """
        if object['status'] == 'success':
            new_object = {'years': [], '3': [], '4': [], '11': [], '7': [], 'country': 'Italy', 'nuts_code': nuts,
                          'legend_title': 'Qualification Code'}

            for data in object['results']['bindings']:
                if data['Year']['value'] not in new_object['years']:
                    new_object['years'].append(data['Year']['value'])
                new_object[data['Education']['value']].append(float(data['Value']['value']))
            return new_object
        else:
            return object

    def set_query(self, nuts_region):
        
        query = """ 
                    prefix nuts: <http://ld.linked-open-statistics.org/data/conceptscheme/NutsRegion/>
                    prefix year: <http://ld.linked-open-statistics.org/data/conceptscheme/Year/>
                    prefix gender: <http://ld.linked-open-statistics.org/data/conceptscheme/Gender/>
                    prefix vocab: <http://ld.linked-open-statistics.org/vocab/>
                    prefix education: <http://ld.linked-open-statistics.org/data/conceptscheme/Education/>
                    prefix cor: <http://ld.linked-open-statistics.org/data/conceptscheme/CountryOfResidence/>
                    
                    select replace(str(?year), year:, "") as ?Year, ?obj as ?Value, replace(str(?education), education:, "") as ?Education  where {
                    ?s ?p nuts:""" + nuts_region + """ .
                    ?s vocab:Year ?year .
                    ?s vocab:Gender gender:9 .
                    ?s vocab:Education ?education
                    FILTER (!regex(?year, "Q","i")).
                    ?s vocab:Value ?obj .
                    FILTER (replace(str(?education), education:, "") != '99') .
                    }
                    ORDER BY ASC(?Year)
                """
 

        self.sparql.setQuery(query)

    def execute_query(self, nuts):
        nuts = nuts.strip()
        try:
            self.set_query(nuts)
            results = self.sparql.query().convert()
            if len(results['results']['bindings']) == 0:
                results['status'] = "Bad graph URI/rdf data not according to the standard"
            else:
                results['status'] = "success"
                results['results'] = self._data_preprocess(results, nuts)
        except Exception as e:
            results = {}
            results['status'] = "bad request"

        return results


class BulgariaUnemploymentRate:

    def __init__(self, default_uri="http://unemp_bulgaria_pert.derilinx.com", default_format=JSON):
        self.sparql = sparql
        self.sparql.addDefaultGraph(default_uri)
        self.sparql.setReturnFormat(default_format)
        self.sparql.setHTTPAuth(DIGEST)

    @staticmethod
    def clean_year(year):

        return "".join(list(year[:-2])), "".join(list(year[-2:]))

    def _data_preprocess(self, object, nuts):
        """ Q1, Q2, Q3 .. etc are the quarterly data from dataset """

        if object['status'] == 'success':
            new_object = {'years': [], 'Q1': [], 'Q2': [], 'Q3': [], 'Q4': [], 'country': 'Bulgaria', 'nuts_code': nuts,
                          'legend_title': 'Quarterly Data'}

            for data in object['results']['bindings']:

                _year, _quater = self.clean_year(data['Year']['value'])
                if _year not in new_object['years']:
                    new_object['years'].append(_year)
                new_object[_quater].append(float(data['Value']['value']))
            return new_object
        else:
            return object

    def _set_query(self, nuts_region):

        query = """ 
                    prefix qb: <http://purl.org/linked-data/cube#>
                    prefix losdv: <http://ld.linked-open-statistics.org/vocab/> 
                    prefix losdd: <http://ld.linked-open-statistics.org/data/> 
                    
                    select distinct ?Year ?Value ?nuts_id
                    where{ 
                    ?obs a <http://purl.org/linked-data/cube#Observation>.
                    ?obs <http://purl.org/linked-data/cube#dataSet> <http://ld.linked-open-statistics.org/data/Bulgaria_ILO_perc_ds> .
                    ?obs <http://ld.linked-open-statistics.org/vocab/Gender> <http://ld.linked-open-statistics.org/data/conceptscheme/Gender/0> .
                    ?obs <http://ld.linked-open-statistics.org/vocab/NutsRegion> ?nuts.
                    ?nuts <http://www.w3.org/2000/01/rdf-schema#label> ?nuts_id.
                    ?obs <http://ld.linked-open-statistics.org/vocab/TimePeriod> ?year_1.
                    ?year_1 <http://www.w3.org/2000/01/rdf-schema#label> ?Year.
                    ?obs <http://ld.linked-open-statistics.org/vocab/Value> ?Value .
                    FILTER(?nuts_id = '"""+str(nuts_region)+"""').
                    }
                    ORDER BY ?Year
                """
        self.sparql.setQuery(query)

    def execute_query(self, nuts):
        nuts = nuts.strip()

        try:
            self._set_query(nuts)
            results = self.sparql.query().convert()
            if len(results['results']['bindings']) == 0:
                results['status'] = "Bad graph URI/rdf data not according to the standard"
            else:
                results['status'] = "success"
                results['results'] = self._data_preprocess(results, nuts)
        except Exception as e:
            results = {}
            results['status'] = "bad request"

        return results


class FranceUnemploymentRate:

    def __init__(self, default_uri="http://unemp_france.staging.derilinx.com", default_format=JSON):
        self.sparql = sparql
        self.sparql.addDefaultGraph(default_uri)
        self.sparql.setReturnFormat(default_format)
        self.sparql.setHTTPAuth(DIGEST)

    @staticmethod
    def clean_year(year):

        return "".join(list(year[:-2])), "".join(list(year[-2:]))

    def _data_preprocess(self, object, nuts):
        """ Q1, Q2, Q3 .. etc are the quarterly data from dataset """

        if object['status'] == 'success':
            new_object = {'years': [], 'Q1': [], 'Q2': [], 'Q3': [], 'Q4': [], 'country': 'France', 'nuts_code': nuts,
                          'legend_title': 'Quarterly Data'}

            for data in object['results']['bindings']:

                _year, _quater = self.clean_year(data['Year']['value'])
                if _year not in new_object['years']:
                    new_object['years'].append(_year)
                new_object[_quater].append(float(data['Value']['value']))
            return new_object
        else:
            return object

    def _set_query(self, nuts_region):

        query = """ 
                    prefix qb: <http://purl.org/linked-data/cube#>
                    prefix losdv: <http://ld.linked-open-statistics.org/vocab/> 
                    prefix losdd: <http://ld.linked-open-statistics.org/data/> 
                    
                    select distinct ?Year ?Value
                    where{ 
                    ?obs a <http://purl.org/linked-data/cube#Observation>.
                    ?obs <http://purl.org/linked-data/cube#dataSet> <http://ld.linked-open-statistics.org/data/French_ILO_ds> .
                    ?obs <http://ld.linked-open-statistics.org/vocab/NutsRegion> ?nuts.
                    ?nuts <http://www.w3.org/2000/01/rdf-schema#label> '"""+str(nuts_region)+"""'.
                    ?obs <http://ld.linked-open-statistics.org/vocab/TimePeriod> ?year_1.
                    ?year_1 <http://www.w3.org/2000/01/rdf-schema#label> ?Year.
                    ?obs <http://ld.linked-open-statistics.org/vocab/Value> ?Value .
                    
                    }
                    ORDER BY ?Year
                """
        self.sparql.setQuery(query)

    def execute_query(self, nuts):
        nuts = nuts.strip()

        try:
            self._set_query(nuts)
            results = self.sparql.query().convert()
            if len(results['results']['bindings']) == 0:
                results['status'] = "Bad graph URI/rdf data not according to the standard"
            else:
                results['status'] = "success"
                results['results'] = self._data_preprocess(results, nuts)
        except Exception as e:
            results = {}
            results['status'] = "bad request"

        return results


class IrishUnemploymentRate:

    def __init__(self, default_uri="http://uemp_ireland.staging.derilinx.com", default_format=JSON):
        self.sparql = sparql
        self.sparql.addDefaultGraph(default_uri)
        self.sparql.setReturnFormat(default_format)
        self.sparql.setHTTPAuth(DIGEST)
        self.nuts_rg= {'IE041': 'Border', 'IE042': 'West', 'IE062': 'Mid-East',
                          'IE051': 'Mid-West', 'IE063': 'Midland', 'IE053': 'South-West',
                          'IE052': 'South-East', 'IE061': 'Dublin'}

    @staticmethod
    def clean_year(year):

        return "".join(list(year[:-2])), "".join(list(year[-2:]))

    def _data_preprocess(self, object, nuts):
        """ Q1, Q2, Q3 .. etc are the quarterly data from dataset """

        if object['status'] == 'success':
            new_object = {'years': [], 'Q1': [], 'Q2': [], 'Q3': [], 'Q4': [], 'country': 'Ireland',
                          'nuts_code': nuts.strip(),
                          'legend_title': 'Quarterly Data'}

            for data in object['results']['bindings']:

                _year, _quater = self.clean_year(data['Year']['value'])
                if _year not in new_object['years']:
                    new_object['years'].append(_year)
                new_object[_quater].append(float(data['Value']['value']))
            return new_object
        else:
            return object

    def _set_query(self, nuts_region):

        query = """ 
                    prefix qb: <http://purl.org/linked-data/cube#>
                    prefix losdv: <http://ld.linked-open-statistics.org/vocab/> 
                    prefix losdd: <http://ld.linked-open-statistics.org/data/> 
                    
                    select distinct ?Year ?Value ?nuts_id
                    where{ 
                    ?obs a <http://purl.org/linked-data/cube#Observation>.
                    ?obs <http://purl.org/linked-data/cube#dataSet> <http://ld.linked-open-statistics.org/data/Irish_ILO_ds> .
                    ?obs <http://ld.linked-open-statistics.org/vocab/NutsRegion> ?nuts.
                    ?nuts <http://www.w3.org/2000/01/rdf-schema#label> '"""+str(self.nuts_rg[nuts_region.strip()])+"""'.
                    ?obs <http://ld.linked-open-statistics.org/vocab/TimePeriod> ?year_1.
                    ?year_1 <http://www.w3.org/2000/01/rdf-schema#label> ?Year.
                    ?obs <http://ld.linked-open-statistics.org/vocab/Value> ?Value .
                    
                    }
                    ORDER BY ?Year
                """
        self.sparql.setQuery(query)

    def execute_query(self, nuts):
        nuts = nuts.strip()

        try:
            self._set_query(nuts)
            results = self.sparql.query().convert()
            if len(results['results']['bindings']) == 0:
                results['status'] = "Bad graph URI/rdf data not according to the standard"
            else:
                results['status'] = "success"
                results['results'] = self._data_preprocess(results, nuts)
        except Exception as e:
            results = {}
            results['status'] = "bad request"

        return results


def get_popup(nuts):

    query_instance = {'it': ItalyUnemploymentRate, 'bg': BulgariaUnemploymentRate, 'fr':FranceUnemploymentRate,
                      'ie': IrishUnemploymentRate}
    try:
        query = query_instance["".join(list(nuts)[:2]).lower()]()
        results = query.execute_query(nuts)
    except KeyError:
        results = {}
        results['status'] = "bad request"
        return results

    return results








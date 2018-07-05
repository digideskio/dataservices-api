#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from unittest import TestCase
from nose.tools import assert_raises
from nose.tools import assert_not_equal, assert_equal
from ..helpers.integration_test_helper import IntegrationTestHelper
from ..helpers.integration_test_helper import assert_close_enough

class TestStreetFunctionsSetUp(TestCase):

    def setUp(self):
        self.env_variables = IntegrationTestHelper.get_environment_variables()
        self.sql_api_url = "{0}://{1}.{2}/api/v1/sql".format(
            self.env_variables['schema'],
            self.env_variables['username'],
            self.env_variables['host'],
            self.env_variables['api_key']
        )


class TestStreetFunctions(TestStreetFunctionsSetUp):

    def test_if_select_with_street_point_is_ok(self):
        query = "SELECT cdb_geocode_street_point(street) " \
                "as geometry FROM {0} LIMIT 1&api_key={1}".format(
            self.env_variables['table_name'],
            self.env_variables['api_key'])
        geometry = IntegrationTestHelper.execute_query(self.sql_api_url, query)
        assert_not_equal(geometry['geometry'], None)

    def test_if_select_with_street_without_api_key_raise_error(self):
        query = "SELECT cdb_geocode_street_point(street) " \
                "as geometry FROM {0} LIMIT 1".format(
            self.env_variables['table_name'])
        try:
            IntegrationTestHelper.execute_query(self.sql_api_url, query)
        except Exception as e:
            assert_equal(e.message[0], "The api_key must be provided")


class TestBulkStreetFunctions(TestStreetFunctionsSetUp):
    provider = None
    fixture_points = None

    GOOGLE_POINTS = {
        'Plaza Mayor, Valladolid': [-4.728252, 41.6517025],
        'Paseo Zorrilla, Valladolid': [-4.7404453, 41.6314339],
        '1900 amphitheatre parkway': [-122.0875324, 37.4227968],
        '1901 amphitheatre parkway': [-122.0885504, 37.4238657],
        '1902 amphitheatre parkway': [-122.0876674, 37.4235729],
        'Valladolid': [-4.7245321, 41.652251],
        'Valladolid, Spain': [-4.7245321, 41.652251],
        'Valladolid, Mexico': [-88.2022488, 20.68964],
        'Madrid': [-3.7037902, 40.4167754],
        'Logroño, Spain': [-2.4449852, 42.4627195],
        'Logroño, Argentina': [-61.6961807, -29.5031057]
    }

    HERE_POINTS = {
        'Plaza Mayor, Valladolid': [-4.72979, 41.65258],
        'Paseo Zorrilla, Valladolid': [-4.73869, 41.63817],
        '1900 amphitheatre parkway': [-122.0879468, 37.4234763],
        '1901 amphitheatre parkway': [-122.0879253, 37.4238725],
        '1902 amphitheatre parkway': [-122.0879531, 37.4234775],
        'Valladolid': [-4.73214, 41.6542],
        'Valladolid, Spain': [-4.73214, 41.6542],
        'Valladolid, Mexico': [-88.20117, 20.69021],
        'Madrid': [-3.70578, 40.42028],
        'Logroño, Spain': [-2.45194, 42.46592],
        'Logroño, Argentina': [-61.69604, -29.50425]
    }

    TOMTOM_POINTS = HERE_POINTS.copy()
    TOMTOM_POINTS.update({
        'Plaza Mayor, Valladolid': [-4.72183, 41.5826],
        'Paseo Zorrilla, Valladolid': [-4.74031, 41.63181],
        'Valladolid': [-4.72838, 41.6542],
        'Valladolid, Spain': [-4.72838, 41.6542],
        'Madrid': [-3.70035, 40.42028],
        'Logroño, Spain': [-2.44998, 42.46592],
    })

    FIXTURE_POINTS = {
        'google': GOOGLE_POINTS,
        'heremaps': HERE_POINTS,
        'tomtom': TOMTOM_POINTS
    }

    def setUp(self):
        TestStreetFunctionsSetUp.setUp(self)

        if not self.fixture_points:
            query = "select provider from " \
                    "cdb_dataservices_client.cdb_service_quota_info() " \
                    "where service = 'hires_geocoder'"
            response = self._run_authenticated(query)
            provider = response['rows'][0]['provider']
            self.fixture_points = self.FIXTURE_POINTS[provider]

    def test_full_spec(self):
        query = "select cartodb_id, st_x(the_geom), st_y(the_geom) " \
                "FROM cdb_dataservices_client.cdb_bulk_geocode_street_point(" \
                "'select 1 as cartodb_id, ''Spain'' as country, " \
                "''Castilla y León'' as state, ''Valladolid'' as city, " \
                "''Plaza Mayor'' as street  " \
                "UNION " \
                "select 2 as cartodb_id, ''Spain'' as country, " \
                "''Castilla y León'' as state, ''Valladolid'' as city, " \
                "''Paseo Zorrilla'' as street' " \
                ", 'street', 'city', 'state', 'country')"
        response = self._run_authenticated(query)

        points_by_cartodb_id = {
            1: self.fixture_points['Plaza Mayor, Valladolid'],
            2: self.fixture_points['Paseo Zorrilla, Valladolid']
        }
        self.assert_close_points(self._x_y_by_cartodb_id(response), points_by_cartodb_id)

    def test_empty_columns(self):
        query = "select *, st_x(the_geom), st_y(the_geom) " \
                "FROM cdb_dataservices_client.cdb_bulk_geocode_street_point( " \
                "'select * from jsonb_to_recordset(''[" \
                "{\"cartodb_id\": 1, \"address\": \"1901 amphitheatre parkway, mountain view, ca, us\"}" \
                "]''::jsonb) as (cartodb_id integer, address text)', " \
                "'address', '''''', '''''', '''''')"
        response = self._run_authenticated(query)

        assert_close_enough(self._x_y_by_cartodb_id(response)[1],
                     self.fixture_points['1901 amphitheatre parkway'])

    def test_null_columns(self):
        query = "select *, st_x(the_geom), st_y(the_geom) " \
                "FROM cdb_dataservices_client.cdb_bulk_geocode_street_point( " \
                "'select * from jsonb_to_recordset(''[" \
                "{\"cartodb_id\": 1, \"address\": \"1901 amphitheatre parkway, mountain view, ca, us\"}" \
                "]''::jsonb) as (cartodb_id integer, address text)', " \
                "'address')"
        response = self._run_authenticated(query)

        assert_close_enough(self._x_y_by_cartodb_id(response)[1],
                     self.fixture_points['1901 amphitheatre parkway'])

    def test_batching(self):
        query = "select *, st_x(the_geom), st_y(the_geom) " \
                "FROM cdb_dataservices_client.cdb_bulk_geocode_street_point( " \
                "'select * from jsonb_to_recordset(''[" \
                "{\"cartodb_id\": 1, \"address\": \"1900 amphitheatre parkway, mountain view, ca, us\"}," \
                "{\"cartodb_id\": 2, \"address\": \"1901 amphitheatre parkway, mountain view, ca, us\"}," \
                "{\"cartodb_id\": 3, \"address\": \"1902 amphitheatre parkway, mountain view, ca, us\"}" \
                "]''::jsonb) as (cartodb_id integer, address text)', " \
                "'address', null, null, null, 2)"
        response = self._run_authenticated(query)

        points_by_cartodb_id = {
            1: self.fixture_points['1900 amphitheatre parkway'],
            2: self.fixture_points['1901 amphitheatre parkway'],
            3: self.fixture_points['1902 amphitheatre parkway'],
        }
        self.assert_close_points(self._x_y_by_cartodb_id(response), points_by_cartodb_id)

    def test_city_column_geocoding(self):
        query = "select *, st_x(the_geom), st_y(the_geom) " \
                "FROM cdb_dataservices_client.cdb_bulk_geocode_street_point( " \
                "'select * from jsonb_to_recordset(''[" \
                "{\"cartodb_id\": 1, \"city\": \"Valladolid\"}," \
                "{\"cartodb_id\": 2, \"city\": \"Madrid\"}" \
                "]''::jsonb) as (cartodb_id integer, city text)', " \
                "'city')"
        response = self._run_authenticated(query)

        assert_equal(response['total_rows'], 2)

        points_by_cartodb_id = {
            1: self.fixture_points['Valladolid'],
            2: self.fixture_points['Madrid']
        }
        self.assert_close_points(self._x_y_by_cartodb_id(response), points_by_cartodb_id)

    def test_free_text_geocoding(self):
        query = "select *, st_x(the_geom), st_y(the_geom) " \
                "FROM cdb_dataservices_client.cdb_bulk_geocode_street_point( " \
                "'select * from (" \
                "select 1 as cartodb_id, ''W 26th Street'' as address, " \
                "null as city , null as state , null as country" \
                ")_x', " \
                "'''Logroño, La Rioja, Spain''')"
        response = self._run_authenticated(query)

        assert_close_enough(self._x_y_by_cartodb_id(response)[1],
                     self.fixture_points['Logroño, Spain'])

    def test_templating_geocoding(self):
        query = "SELECT cartodb_id, st_x(the_geom), st_y(the_geom) from " \
                "cdb_dataservices_client.cdb_bulk_geocode_street_point(" \
                "'select 1 as cartodb_id, ''Logroño'' as city', " \
                "'city || '', '' || ''Spain''') " \
                "UNION " \
                "SELECT cartodb_id, st_x(the_geom), st_y(the_geom) from " \
                "cdb_dataservices_client.cdb_bulk_geocode_street_point(" \
                "'select 2 as cartodb_id, ''Logroño'' as city', " \
                "'city || '', '' || ''Argentina''')"
        response = self._run_authenticated(query)

        points_by_cartodb_id = {
            1: self.fixture_points['Logroño, Spain'],
            2: self.fixture_points['Logroño, Argentina']
        }
        self.assert_close_points(self._x_y_by_cartodb_id(response), points_by_cartodb_id)

    def test_template_with_two_columns_geocoding(self):
        query = "SELECT cartodb_id, st_x(the_geom), st_y(the_geom) from " \
                "cdb_dataservices_client.cdb_bulk_geocode_street_point(" \
                "    'select * from (' ||" \
                "    '  select 1 as cartodb_id, ''Valladolid'' as city, ''Mexico'' as country ' ||" \
                "    '  union all '  ||" \
                "    '  select 2, ''Valladolid'', ''Spain''' ||" \
                "    ') _x'," \
                "'city || '', '' || country')"
        response = self._run_authenticated(query)

        points_by_cartodb_id = {
            1: self.fixture_points['Valladolid, Mexico'],
            2: self.fixture_points['Valladolid, Spain']
        }
        self.assert_close_points(self._x_y_by_cartodb_id(response), points_by_cartodb_id)

    def test_large_batches(self):
        """
        Useful just to test a good batch size
        """
        n = 10
        streets = []
        for i in range(0, n):
            streets.append('{{"cartodb_id": {}, "address": "{} Yonge Street, ' \
                           'Toronto, Canada"}}'.format(i, i))

        query = "select *, st_x(the_geom), st_y(the_geom) " \
                "FROM cdb_dataservices_client.cdb_bulk_geocode_street_point( " \
                "'select * from jsonb_to_recordset(''[" \
                "{}" \
                "]''::jsonb) as (cartodb_id integer, address text)', " \
                "'address', null, null, null, {})".format(','.join(streets), n)
        response = self._run_authenticated(query)
        assert_equal(n - 1, len(response['rows']))

    def test_missing_components_on_private_function(self):
        query = "SELECT _cdb_bulk_geocode_street_point(" \
                "   '[{\"id\": \"1\", \"address\": \"Amphitheatre Parkway 22\"}]' " \
                ")"
        response = self._run_authenticated(query)
        assert_equal(1, len(response['rows']))

    def _run_authenticated(self, query):
        authenticated_query = "{}&api_key={}".format(query,
                                                     self.env_variables[
                                                         'api_key'])
        return IntegrationTestHelper.execute_query_raw(self.sql_api_url,
                                                       authenticated_query)

    @staticmethod
    def _x_y_by_cartodb_id(response):
        return {r['cartodb_id']: [r['st_x'], r['st_y']]
                for r in response['rows']}

    @staticmethod
    def assert_close_points(points_a_by_cartodb_id, points_b_by_cartodb_id):
        assert_equal(len(points_a_by_cartodb_id), len(points_b_by_cartodb_id))
        for cartodb_id, point in points_a_by_cartodb_id.iteritems():
            assert_close_enough(point, points_b_by_cartodb_id[cartodb_id])

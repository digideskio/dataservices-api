-- Use regular user role
SET ROLE test_regular_user;

-- Exercise the public function
-- it is public, it shall work
SELECT cdb_geocoder_client.geocode_admin0_polygon('Spain');
SELECT cdb_geocoder_client.geocode_admin1_polygon('California');
SELECT cdb_geocoder_client.geocode_admin1_polygon('California', 'United States');
SELECT cdb_geocoder_client.geocode_namedplace_point('Elx');
SELECT cdb_geocoder_client.geocode_namedplace_point('Elx', 'Valencia');
SELECT cdb_geocoder_client.geocode_namedplace_point('Elx', 'Valencia', 'Spain');
SELECT cdb_geocoder_client.geocode_postalcode_polygon('03204', 'Spain');
SELECT cdb_geocoder_client.geocode_postalcode_point('03204', 'Spain');
SELECT cdb_geocoder_client.geocode_ipaddress_point('8.8.8.8');

-- Check the regular user has no permissions on private functions
SELECT cdb_geocoder_client._geocode_admin0_polygon('evil_user', '{"is_organization": false, "entity_name": "test_user"}', '{"street_geocoder_provider": "nokia","nokia_monthly_quota": 100, "nokia_soft_geocoder_limit": false}', 'Hell');
SELECT cdb_geocoder_client._geocode_admin1_polygon('evil_user', '{"is_organization": false, "entity_name": "test_user"}', '{"street_geocoder_provider": "nokia","nokia_monthly_quota": 100, "nokia_soft_geocoder_limit": false}', 'Hell');
SELECT cdb_geocoder_client._geocode_admin1_polygon('evil_user', '{"is_organization": false, "entity_name": "test_user"}', '{"street_geocoder_provider": "nokia","nokia_monthly_quota": 100, "nokia_soft_geocoder_limit": false}', 'Sheol', 'Hell');
SELECT cdb_geocoder_client._geocode_namedplace_point('evil_user', '{"is_organization": false, "entity_name": "test_user"}', '{"street_geocoder_provider": "nokia","nokia_monthly_quota": 100, "nokia_soft_geocoder_limit": false}', 'Sheol');
SELECT cdb_geocoder_client._geocode_namedplace_point('evil_user', '{"is_organization": false, "entity_name": "test_user"}', '{"street_geocoder_provider": "nokia","nokia_monthly_quota": 100, "nokia_soft_geocoder_limit": false}', 'Sheol', 'Hell');
SELECT cdb_geocoder_client._geocode_namedplace_point('evil_user', '{"is_organization": false, "entity_name": "test_user"}', '{"street_geocoder_provider": "nokia","nokia_monthly_quota": 100, "nokia_soft_geocoder_limit": false}', 'Sheol', 'Hell', 'Ugly world');
SELECT cdb_geocoder_client._geocode_postalcode_polygon('evil_user', '{"is_organization": false, "entity_name": "test_user"}', '{"street_geocoder_provider": "nokia","nokia_monthly_quota": 100, "nokia_soft_geocoder_limit": false}', '66666', 'Hell');
SELECT cdb_geocoder_client._geocode_postalcode_point('evil_user', '{"is_organization": false, "entity_name": "test_user"}', '{"street_geocoder_provider": "nokia","nokia_monthly_quota": 100, "nokia_soft_geocoder_limit": false}', '66666', 'Hell');
SELECT cdb_geocoder_client._geocode_ipaddress_point('evil_user', '{"is_organization": false, "entity_name": "test_user"}', '{"street_geocoder_provider": "nokia","nokia_monthly_quota": 100, "nokia_soft_geocoder_limit": false}', '8.8.8.8');

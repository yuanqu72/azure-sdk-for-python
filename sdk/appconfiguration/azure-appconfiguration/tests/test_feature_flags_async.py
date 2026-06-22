# pylint: disable=too-many-lines
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
from consts import (
    APPCONFIGURATION_ENDPOINT_STRING,
    APPCONFIGURATION_CONNECTION_STRING,
)
from devtools_testutils import EnvironmentVariableLoader, set_custom_default_matcher
from devtools_testutils.aio import recorded_by_proxy_async
from asynctestcase import AsyncAppConfigTestCase
from azure.appconfiguration import (
    FeatureFlag,
)
from azure.appconfiguration.aio import AzureAppConfigurationClient

AppConfigPreparer = functools.partial(
    EnvironmentVariableLoader,
    "appconfiguration",
    appconfiguration_endpoint_string=APPCONFIGURATION_ENDPOINT_STRING,
)


class TestFeatureFlagEndpointAsync(AsyncAppConfigTestCase):
    """Async tests for the new dedicated feature flag endpoint methods"""

    @AppConfigPreparer()
    @recorded_by_proxy_async
    async def test_list_feature_flags(self, appconfiguration_endpoint_string):
        """Test listing feature flags using the dedicated feature flag endpoint."""
        set_custom_default_matcher(compare_bodies=False, excluded_headers="x-ms-content-sha256,x-ms-date")
        client = self.create_client(appconfiguration_endpoint_string)
        
        # Create some feature flags
        feature_flag1 = FeatureFlag(name="feature1", enabled=True)
        feature_flag2 = FeatureFlag(name="feature2", enabled=False)
        
        await client.set_feature_flag(feature_flag1)
        await client.set_feature_flag(feature_flag2)
        
        # List all feature flags
        flags = [f async for f in client.list_feature_flags()]
        assert len(flags) >= 2
        assert any(f.name == "feature1" for f in flags)
        assert any(f.name == "feature2" for f in flags)
        
        # Clean up
        await client.delete_feature_flag("feature1", label=feature_flag1.label)
        await client.delete_feature_flag("feature2", label=feature_flag2.label)
        await client.close()

    @AppConfigPreparer()
    @recorded_by_proxy_async
    async def test_list_feature_flags_with_name_filter(self, appconfiguration_endpoint_string):
        """Test listing feature flags with name filter."""
        set_custom_default_matcher(compare_bodies=False, excluded_headers="x-ms-content-sha256,x-ms-date")
        client = self.create_client(appconfiguration_endpoint_string)
        
        # Create feature flags
        feature_flag1 = FeatureFlag(name="myfeature_alpha", enabled=True)
        feature_flag2 = FeatureFlag(name="myfeature_beta", enabled=False)
        feature_flag3 = FeatureFlag(name="otherfeature", enabled=True)
        
        await client.set_feature_flag(feature_flag1)
        await client.set_feature_flag(feature_flag2)
        await client.set_feature_flag(feature_flag3)
        
        # List with name filter
        flags = [f async for f in client.list_feature_flags(name_filter="myfeature*")]
        assert len(flags) >= 2
        assert all("myfeature" in f.name for f in flags)
        
        # Clean up
        await client.delete_feature_flag("myfeature_alpha", label=feature_flag1.label)
        await client.delete_feature_flag("myfeature_beta", label=feature_flag2.label)
        await client.delete_feature_flag("otherfeature", label=feature_flag3.label)
        await client.close()

    @AppConfigPreparer()
    @recorded_by_proxy_async
    async def test_get_feature_flag(self, appconfiguration_endpoint_string):
        """Test getting a specific feature flag."""
        client = self.create_client(appconfiguration_endpoint_string)
        
        # Create a feature flag
        feature_flag = FeatureFlag(name="test_feature_get", enabled=True)
        created = await client.set_feature_flag(feature_flag)
        
        # Get the feature flag using the new endpoint method
        retrieved = await client.get_feature_flag("test_feature_get", label=created.label)
        assert retrieved is not None
        assert retrieved.name == "test_feature_get"
        assert retrieved.enabled == True
        
        # Clean up
        await client.delete_feature_flag("test_feature_get", label=created.label)
        await client.close()

    @AppConfigPreparer()
    @recorded_by_proxy_async
    async def test_get_feature_flag_not_found(self, appconfiguration_endpoint_string):
        """Test getting a non-existent feature flag."""
        client = self.create_client(appconfiguration_endpoint_string)
        
        # Try to get a non-existent feature flag
        result = await client.get_feature_flag("nonexistent_feature", label=None)
        assert result is None
        await client.close()

    @AppConfigPreparer()
    @recorded_by_proxy_async
    async def test_set_feature_flag(self, appconfiguration_endpoint_string):
        """Test setting a feature flag via the dedicated endpoint."""
        client = self.create_client(appconfiguration_endpoint_string)
        
        # Create a feature flag
        feature_flag = FeatureFlag(name="test_feature_set", enabled=True)
        set_flag = await client.set_feature_flag(feature_flag)
        
        assert set_flag is not None
        assert set_flag.enabled == True
        assert set_flag.name == "test_feature_set"
        
        # Clean up
        await client.delete_feature_flag("test_feature_set", label=set_flag.label)
        await client.close()

    @AppConfigPreparer()
    @recorded_by_proxy_async
    async def test_set_feature_flag_update(self, appconfiguration_endpoint_string):
        """Test updating an existing feature flag."""
        client = self.create_client(appconfiguration_endpoint_string)
        
        # Create and then update a feature flag
        feature_flag = FeatureFlag(name="test_feature_update", enabled=True)
        created = await client.set_feature_flag(feature_flag)
        
        # Update it
        created.enabled = False
        updated = await client.set_feature_flag(created)
        
        assert updated.enabled == False
        assert updated.etag != created.etag
        
        # Clean up
        await client.delete_feature_flag("test_feature_update", label=updated.label)
        await client.close()

    @AppConfigPreparer()
    @recorded_by_proxy_async
    async def test_delete_feature_flag(self, appconfiguration_endpoint_string):
        """Test deleting a feature flag."""
        client = self.create_client(appconfiguration_endpoint_string)
        
        # Create a feature flag
        feature_flag = FeatureFlag(name="test_feature_delete", enabled=True)
        created = await client.set_feature_flag(feature_flag)
        
        # Delete it using the endpoint method
        await client.delete_feature_flag("test_feature_delete", label=created.label)
        
        # Verify it's deleted
        result = await client.get_feature_flag("test_feature_delete", label=created.label)
        assert result is None
        await client.close()

    @AppConfigPreparer()
    @recorded_by_proxy_async
    async def test_list_feature_flag_revisions(self, appconfiguration_endpoint_string):
        """Test listing feature flag revisions."""
        set_custom_default_matcher(compare_bodies=False, excluded_headers="x-ms-content-sha256,x-ms-date")
        client = self.create_client(appconfiguration_endpoint_string)
        
        # Create and update a feature flag to create revisions
        feature_flag = FeatureFlag(name="test_feature_revisions", enabled=True)
        created = await client.set_feature_flag(feature_flag)
        
        # Update to create another revision
        created.enabled = False
        updated = await client.set_feature_flag(created)
        
        # List revisions
        revisions = [r async for r in client.list_feature_flag_revisions(feature_id_filter="test_feature_revisions")]
        assert len(revisions) >= 1  # At least one revision
        assert all("test_feature_revisions" in r.name for r in revisions)
        
        # Clean up
        await client.delete_feature_flag("test_feature_revisions", label=updated.label)
        await client.close()

    @AppConfigPreparer()
    @recorded_by_proxy_async
    async def test_feature_flag_with_label(self, appconfiguration_endpoint_string):
        """Test feature flag operations with labels."""
        client = self.create_client(appconfiguration_endpoint_string)
        
        # Create feature flags with labels
        feature_flag_prod = FeatureFlag(
            name="feature_with_label", 
            enabled=True, 
            label="prod"
        )
        feature_flag_staging = FeatureFlag(
            name="feature_with_label", 
            enabled=False, 
            label="staging"
        )
        
        await client.set_feature_flag(feature_flag_prod)
        await client.set_feature_flag(feature_flag_staging)
        
        # Get specific labeled version
        prod_flag = await client.get_feature_flag("feature_with_label", label="prod")
        assert prod_flag is not None
        assert prod_flag.enabled == True
        
        staging_flag = await client.get_feature_flag("feature_with_label", label="staging")
        assert staging_flag is not None
        assert staging_flag.enabled == False
        
        # Clean up
        await client.delete_feature_flag("feature_with_label", label="prod")
        await client.delete_feature_flag("feature_with_label", label="staging")
        await client.close()

from django_tenants.utils import tenant_context

from api.models import Provider
from api.settings.tags.mapping.utils import resummarize_current_month_by_tag_keys
from masu.test import MasuTestCase
from reporting.provider.all.models import EnabledTagKeys
from reporting_common.models import DelayedCeleryTasks


class TestTagMappingUtils(MasuTestCase):
    """Test the utils for Tag mapping"""

    def setUp(self):
        super().setUp()
        self.test_matrix = {
            Provider.PROVIDER_AWS: self.aws_provider.uuid,
            Provider.PROVIDER_AZURE: self.azure_provider.uuid,
            Provider.PROVIDER_GCP: self.gcp_provider.uuid,
            Provider.PROVIDER_OCI: self.oci_provider.uuid,
            Provider.PROVIDER_OCP: self.ocp_provider.uuid,
        }

    def test_find_tag_key_providers(self):
        with tenant_context(self.tenant):
            for ptype, uuid in self.test_matrix.items():
                with self.subTest(ptype=ptype, uuid=uuid):
                    keys = list(EnabledTagKeys.objects.filter(provider_type=ptype))
                    resummarize_current_month_by_tag_keys(keys, self.schema_name)
                    self.assertTrue(DelayedCeleryTasks.objects.filter(provider_uuid=uuid).exists())

    def test_multiple_returns(self):
        with tenant_context(self.tenant):
            keys = list(EnabledTagKeys.objects.all())
            resummarize_current_month_by_tag_keys(keys, self.schema_name)
            for uuid in self.test_matrix.values():
                self.assertTrue(DelayedCeleryTasks.objects.filter(provider_uuid=uuid).exists())

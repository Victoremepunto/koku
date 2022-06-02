#
# Copyright 2021 Red Hat Inc.
# SPDX-License-Identifier: Apache-2.0
#
"""View for running_celery_task collect_hcs_report_finalization endpoint."""
import datetime
import logging
import uuid

from django.views.decorators.cache import never_cache
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.decorators import renderer_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.settings import api_settings

from hcs.tasks import collect_hcs_report_finalization
from hcs.tasks import HCS_QUEUE


LOG = logging.getLogger(__name__)


@never_cache
@api_view(http_method_names=["GET"])
@permission_classes((AllowAny,))
@renderer_classes(tuple(api_settings.DEFAULT_RENDERER_CLASSES))
def hcs_report_finalization(request):
    """Generate HCS finalized for last month(based on 'datetime.date.today')reports."""
    params = request.query_params
    month = params.get("month")
    year = params.get("year")

    tracing_id = str(uuid.uuid4())

    async_results = []

    today = datetime.date.today()
    finalization_month = today.replace(day=1)

    if month is not None:
        finalization_month = finalization_month.replace(month=int(month))
    else:
        finalization_month = finalization_month - datetime.timedelta(days=1)

    if year is not None:
        finalization_month = finalization_month.replace(year=int(year))

    report_data_msg_key = "HCS Report Finalization"

    if request.method == "GET":
        async_result = collect_hcs_report_finalization.s(month, year, tracing_id).apply_async(queue=HCS_QUEUE)
        async_results.append({"month": finalization_month.strftime("%Y-%m"), "id": str(async_result)})
        return Response({report_data_msg_key: async_results})

﻿# Python <= 3.9
from __future__ import annotations

{{#Special_NexusFeatures}}
import array
import asyncio
import base64
{{/Special_NexusFeatures}}
import json
{{#Special_NexusFeatures}}
from datetime import datetime, time, timedelta
from tempfile import NamedTemporaryFile
from typing import Callable
{{/Special_NexusFeatures}}
from typing import (Any, AsyncIterable, Iterable, Optional, Type, TypeVar,
                    Union, cast)
{{#Special_NexusFeatures}}
from zipfile import ZipFile
{{/Special_NexusFeatures}}

from httpx import AsyncClient, Client, Request, Response
{{{VersioningImports}}}
from .PythonEncoder import JsonEncoder, _json_encoder_options
{{#Special_NexusFeatures}}
from .Shared import DataResponse
{{/Special_NexusFeatures}}
from .Shared import {{{ExceptionType}}}

T = TypeVar("T")

{{{SyncMainClient}}}
{{{AsyncMainClient}}}
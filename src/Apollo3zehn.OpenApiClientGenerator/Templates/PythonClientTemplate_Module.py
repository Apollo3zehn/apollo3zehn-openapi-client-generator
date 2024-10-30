﻿# Python <= 3.9
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import AsyncIterable, Awaitable, Iterable, Optional, TypeVar, Union
from urllib.parse import quote
from uuid import UUID

from httpx import Response

from . import JsonEncoder
from ._client import {{{ClientName}}}AsyncClient, {{{ClientName}}}Client
from ._shared import _json_encoder_options, _to_string

T = TypeVar("T")

{{SyncClient}}
{{SyncSubClients}}
{{AsyncClient}}
{{AsyncSubClients}}
{{Models}}

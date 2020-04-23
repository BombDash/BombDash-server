# Copyright (c) 2020 BombDash

import requests
from requests.auth import HTTPBasicAuth
import json
from typing import Optional, Dict, Any

from bd.server.config import Config as ServerConfig


class BombDashApi:
    """BombDash HTTP API class"""

    def __init__(self, api_url: str, api_auth: str):
        self.api_url = api_url
        self.api_auth = api_auth
    
    def _method(self, method, **kwargs) -> Dict[str, Any]:
        response = requests.request('POST', self.api_url + method, json=kwargs,
                                    auth=HTTPBasicAuth(*ServerConfig.api_auth.split(':')))
        return json.loads(response.text)

    def stats_ping(self) -> Dict[str, Any]:
        pass

    def stats_update(self) -> Dict[str, Any]:
        pass

    def stats_get(self) -> Dict[str, Any]:
        pass

    def stats_types(self) -> Dict[str, Any]:
        pass

    def player_get(self) -> Dict[str, Any]:
        pass

    def player_ban_add(self, player_id: str, reason: str, operator: Optional[str],
                       end: Optional[int]) -> Dict[str, Any]:
        pass

    def player_ban_get(self) -> Dict[str, Any]:
        pass

    def player_server_message(self) -> Dict[str, Any]:
        pass

    def account_create(self) -> Dict[str, Any]:
        pass

    def account_verify(self) -> Dict[str, Any]:
        pass

#!/usr/bin/python

import marathon
import requests
from marathon import MarathonClient
from marathon.models import MarathonApp, MarathonDeployment, MarathonGroup, MarathonInfo, MarathonTask, MarathonEndpoint, MarathonQueueItem
from marathon.exceptions import InternalServerError, NotFoundError, MarathonHttpError, MarathonError
from marathon.models.events import EventFactory

class DcosMarathon(MarathonClient):

    def _is_reachable(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return True
        except requests.exceptions.HTTPError as err:
            return True
        except:
            pass
        return False

    def _token(self, force_new=False):
        if self.dcos == False:
            return None
        if self.auth_token != None and not force_new:
            return self.auth_token
        data = '{"uid": "%s", "password": "%s"}'%(self.user, self.password)
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        response = requests.post(self.url.rstrip("/")+"/acs/api/v1/auth/login", data=data, headers=headers)
        response.raise_for_status()
        return response.json()['token']

    def __init__(self, url, username=None, password=None, timeout=10, dcos=True):
        self.marathon_url = url
        if dcos == True:
            self.marathon_url = "%s/marathon"%(url)
        super(DcosMarathon, self).__init__(self.marathon_url, username=username, password=password, timeout=timeout)
        self.url, self.user, self.password, self.dcos = url, username, password, dcos
        self.auth_token = None
        self.can_connect, self.auth_token = self._is_reachable(self.marathon_url), self._token(force_new=True)

    def __str__(self):
        mode, status = "dcos", "unknown"

        if self.dcos == False:
            mode = "standalone"

        if self.auth_token != None:
            status = "authenticated"
        if self.can_connect == True:
            status = "reachable"

        return "url: %s, mode: %s, status: %s" % (self.marathon_url, mode, status)

    def _do_request(self, method, path, params=None, data=None):
        """Query Marathon server."""
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        if self.dcos == True:
            headers['Authorization'] = "token=%s"%(self._token())
            self.auth = None
        response = None
        servers = list(self.servers)
        while servers and response is None:
            server = servers.pop(0)
            url = ''.join([server.rstrip('/'), path])
            try:
                response = self.session.request(
                    method, url, params=params, data=data, headers=headers,
                    auth=self.auth, timeout=self.timeout)
                marathon.log.info('Got response from %s', server)
            except requests.exceptions.RequestException as e:
                marathon.log.error(
                    'Error while calling %s: %s', url, str(e))

        if response is None:
            raise MarathonError('No remaining Marathon servers to try')

        if response.status_code >= 500:
            marathon.log.error('Got HTTP {code}: {body}'.format(
                code=response.status_code, body=response.text))
            raise InternalServerError(response)
        elif response.status_code >= 400:
            print response.status_code
            marathon.log.error('Got HTTP {code}: {body}'.format(
                code=response.status_code, body=response.text))
            if response.status_code == 404:
                raise NotFoundError(response)
            else:
                raise MarathonHttpError(response)
        elif response.status_code >= 300:
            marathon.log.warn('Got HTTP {code}: {body}'.format(
                code=response.status_code, body=response.text))
        else:
            marathon.log.debug('Got HTTP {code}: {body}'.format(
                code=response.status_code, body=response.text))

        return response

    def _do_sse_request(self, path, params=None, data=None):
        from sseclient import SSEClient

        headers = {'Accept': 'text/event-stream'}
        if self.dcos == True:
            headers['Authorization'] = "token=%s"%(self._token())
            self.auth = None
        messages = None
        servers = list(self.servers)
        while servers and messages is None:
            server = servers.pop(0)
            url = ''.join([server.rstrip('/'), path])
            try:
                messages = SSEClient(url, params=params, data=data, headers=headers,
                                     auth=self.auth)
            except Exception as e:
                marathon.log.error('Error while calling %s: %s', url, e.message)

        if messages is None:
            raise MarathonError('No remaining Marathon servers to try')

        return messages

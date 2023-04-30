import re
import ipaddress
import httpx
from CloudFlare import CloudFlare
from CloudFlare.exceptions import CloudFlareAPIError
from flask import Flask, request

from src.config import config_instance
from src.config.config import is_development
from src.exceptions import UnAuthenticatedError
from src.logger import init_logger
from src.utils import camel_to_snake

DEFAULT_IPV4 = ['173.245.48.0/20', '103.21.244.0/22', '103.22.200.0/22', '103.31.4.0/22', '141.101.64.0/18',
                '108.162.192.0/18', '190.93.240.0/20', '188.114.96.0/20', '197.234.240.0/22',
                '198.41.128.0/17',
                '162.158.0.0/15', '104.16.0.0/13', '104.24.0.0/14', '172.64.0.0/13', '131.0.72.0/22']

# Define dictionary of malicious patterns
malicious_patterns = {
    "buffer_overflow": "^\?unix:A{1000,}",  # pattern for buffer overflow attack
    "SQL_injection": "'?([\w\s]+)'?\s*OR\s*'?([\w\s]+)'?\s*=\s*'?([\w\s]+)'?",  # pattern for SQL injection attack
    "SQL_injection_Commands": "\b(ALTER|CREATE|DELETE|DROP|EXEC(UTE){0,1}|INSERT( +INTO){0,1}|MERGE|REPLACE|SELECT|UPDATE)\b",
    # Match SQL Commands
    "SQL_injection_Comments": "(--|#|\/\*)[\w\d\s]*",  # Match SQL Comments
    "SQL_Injection_syntax": "\b(AND|OR)[\s]*[^\s]*=[^\s]*",  # Match SQL Injection Syntax
    "SQL_Union_select_attack": "(?i)\bselect\b.*\bfrom\b.*\bunion\b.*\bselect\b",  # UNION Select Attack
    "SQL_BLIND_SQL_Injection": "(?i)\b(if|case).*\blike\b.*\bthen\b",  # blind SQL Injection attack
    "SQL_TIMEBASED_Injection": "(?i)\b(select|and)\b.*\bsleep\(\d+\)\b",  # Time based injection attacks
    "XSS": "<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>",  # pattern for cross-site scripting (XSS) attack
    "path_traversal": "\.\.[\\\/]?|\.[\\\/]{2,}",  # pattern for path traversal attack
    # "LDAP_injection": "[()\\\/*\x00-\x1f\x80-\xff]",  # pattern for LDAP injection attack
    "command_injection": ";\s*(?:sh|bash|cmd|powershell)\b",  # pattern for command injection attack
    "file_inclusion": "(?:file|php|zip|glob|data)\s*:",  # pattern for file inclusion attack
    "RCE_attack": "^.*\b(?:eval|assert|exec|system|passthru|popen|proc_open)\b.*$",
    # pattern for remote code execution attack
    "CSRF_attack": "^.*(GET|POST)\s+.*\b(?:referer|origin)\b\s*:\s*(?!https?://(?:localhost|127\.0\.0\.1)).*$",
    # # pattern for cross-site request forgery attack
    "SSRF_attack": "^.*\b(?:curl|wget|file_get_contents|fsockopen|stream_socket_client|socket_create)\b.*$",
    # pattern for server-side request forgery attack
    "CSWSH_attack": "^.*\b(?:Sec-WebSocket-Key|Sec-WebSocket-Accept)\b.*$",
    "BRUTEFORCE_attack": "^.*\b(?:admin|root|test|user|guest)\b.*$",
    "Credential_Stuffing": "(?:\badmin\b|\broot\b|\bpassword\b|\b123456\b|\bqwerty\b|\b123456789\b|\b12345678\b|\b1234567890\b|\b12345\b|\b1234567\b|\b12345678910\b|\b123123\b|\b1234\b|\b111111\b|\babc123\b|\bmonkey\b|\bdragon\b|\bletmein\b|\bsunshine\b|\bprincess\b|\b123456789\b|\bfootball\b|\bcharlie\b|\bshadow\b|\bmichael\b|\bjennifer\b|\bcomputer\b|\bsecurity\b|\btrustno1\b)",
    # "Remote_File_Inclusion": "^.*(include|require)(_once)?\s*\(?\s*[\]\s*(https?:)?//",
    "Clickjacking": '<iframe\s*src="[^"]+"|<iframe\s*src=\'[^\']+\'|\bX-Frame-Options\b\s*:\s*\b(DENY|SAMEORIGIN)\b',
    "XML_External_Entity_Injection": "<!ENTITY[^>]*>",
    "Server_Side_Template_Injection": "\{\{\s*(?:config|app|request|session|env|get|post|server|cookie|_|\|\|)\..+?\}\}",
    "Business_Logic_Attacks": "^\b(?:price|discount|quantity|shipping|coupon|tax|refund|voucher|payment)\b",
    "Javascript_injection": "(?:<\sscript\s>\s*|\blocation\b\s*=|\bwindow\b\s*.\slocation\s=|\bdocument\b\s*.\slocation\s=)",
    "HTML_injection": "<\siframe\s|<\simg\s|<\sobject\s|<\sembed\s",
    # "HTTP_PARAMETER_POLLUTION":  '(?<=^|&)[\w-]+=[^&]*&[\w-]+=',
    "DOM_BASED_XSS": "(?:\blocation\b\s*.\s*(?:hash|search|pathname)|document\s*.\s*(?:location|referrer).hash)"
}


def contains_malicious_patterns(_input: str) -> bool:
    """
    **contains_malicious_patterns**
        will return true if the string matches any of the attack patterns
    :param _input:
    :return:
    """
    attack_pattern = r"(select|update|delete|drop|create|alter|insert|into|from|where|union|having|or|and|exec|script|javascript|xss|sql|cmd|../|..\|buffer|format|code|include|shell|rfi|lfi|phish)"

    return re.search(attack_pattern, _input, re.IGNORECASE) is not None


EMAIL: str = config_instance().CLOUDFLARE_SETTINGS.EMAIL
TOKEN: str = config_instance().CLOUDFLARE_SETTINGS.TOKEN

async_client = httpx.AsyncClient(http2=True, limits=httpx.Limits(max_connections=100, max_keepalive_connections=20))


async def send_request(api_url: str, headers: dict[str, str | int], method: str = 'get',
                       data: str | None = None):
    try:
        if method.lower() == "get":
            response = await async_client.get(url=api_url, headers=headers, timeout=360000)
        elif method.lower() == "post":
            if data:
                response = await async_client.post(url=api_url, json=data, headers=headers, timeout=360000)
            else:
                response = await async_client.post(url=api_url, headers=headers, timeout=360000)
        else:
            return None
    except httpx.HTTPError as http_err:
        raise http_err
    except Exception as err:
        raise err
    return response.json()


class Firewall:
    """
        used in conjunction with cloudflare to secure requests to this web application
        by using several methods including IP White listing

    """
    # TODO setup security for outgoing Responses , including setting Security headers
    def __init__(self):
        self.allowed_hosts = config_instance().HOST_ADDRESSES.split(",")
        self._max_payload_size: int = 8 * 64
        try:
            self.cloud_flare = CloudFlare(email=EMAIL, token=TOKEN)
        except CloudFlareAPIError:
            pass
        self.ip_ranges = []
        self.bad_addresses = set()
        self.compiled_bad_patterns = [re.compile(pattern) for pattern in malicious_patterns.values()]
        self._logger = init_logger(camel_to_snake(self.__class__.__name__))

    def init_app(self, app: Flask):
        # Setting Up Incoming Request Security Checks
        if is_development():
            # if this is not a development server secure the server with our firewall
            app.before_request(self.is_host_valid)
            app.before_request(self.is_edge_ip_allowed)
            app.before_request(self.check_if_request_malicious)
        # obtain the latest cloudflare edge servers
        ipv4, ipv6 = self.get_ip_ranges()
        # updating the ip ranges
        self.ip_ranges.extend(ipv4)
        self.ip_ranges.extend(ipv6)

    def is_host_valid(self) -> bool:
        """will return true if host is one of the allowed hosts addresses"""
        header_host = request.headers.get('Host')
        if header_host.casefold() != request.host.casefold():
            raise UnAuthenticatedError('Bad Host Header')
        if request.host not in self.allowed_hosts:
            raise UnAuthenticatedError('Host not allowed')

    def is_edge_ip_allowed(self):
        """checks if edge ip falls within allowable ranges"""
        edge_ip = self.get_edge_server_ip(headers=request.headers)
        if not any(ipaddress.ip_address(edge_ip) in ipaddress.ip_network(ip_range) for ip_range in self.ip_ranges):
            raise UnAuthenticatedError('IP Address not allowed')

    def check_if_request_malicious(self):
        """
        **check_if_request_malicious**
            Analyses request headers , body and path if there
            are any malicious patterns an error will be thrown
        """
        # Check request for malicious patterns
        headers: dict[str, str] = request.headers
        body = request.data

        if 'Content-Length' in headers and int(headers['Content-Length']) > self._max_payload_size:
            # Request payload is too large,
            raise UnAuthenticatedError('Payload is suspicious')

        if body:
            # Set default regex pattern for string-like request bodies
            #  StackOverflow attacks
            payload_regex = "^[A-Za-z0-9+/]{1024,}={0,2}$"
            if re.match(payload_regex, body) or contains_malicious_patterns(_input=body):
                raise UnAuthenticatedError('Payload is suspicious')

        path = str(request.path)
        if any((pattern.match(path) for pattern in self.compiled_bad_patterns)):
            raise UnAuthenticatedError('Payload is suspicious')

    @staticmethod
    def get_client_ip() -> str:
        """
        **get_client_ip**
            will return the actual client ip address of the client making the request
        """
        ip = request.headers.get('cf-connecting-ip')
        return ip.split(',')[0]

    @staticmethod
    def get_edge_server_ip(headers) -> str:
        """obtains cloudflare edge server the request is being routed through"""
        return headers.get("x-real-ip")

    @staticmethod
    def get_ip_ranges() -> tuple[list[str], list[str]]:
        """
            obtains a list of ip addresses from cloudflare edge servers
        :return:
        """
        _uri = 'https://api.cloudflare.com/client/v4/ips'
        _headers = {'Accept': 'application/json', 'X-Auth-Email': EMAIL}
        try:
            response = await send_request(api_url=_uri, headers=_headers)
            ipv4_cidrs = response.get('result', {}).get('ipv4_cidrs', DEFAULT_IPV4)
            ipv6_cidrs = response.get('result', {}).get('ipv6_cidrs', [])
            return ipv4_cidrs, ipv6_cidrs

        except CloudFlareAPIError:
            return [], []

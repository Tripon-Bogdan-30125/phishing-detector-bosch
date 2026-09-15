import whois
import dns.resolver
import tldextract
import ssl
import socket
from datetime import datetime

class OSINTAnalyzer:
    def __init__(self):
        self.free_cas = ["Let's Encrypt", "ZeroSSL", "cPanel", "Cloudflare"]

    def get_whois_data(self, domain):
        age_days, expiration_days = -1, -1
        try:
            domain_info = whois.whois(domain)
            creation_date = domain_info.creation_date
            if isinstance(creation_date, list): creation_date = creation_date[0]
            if isinstance(creation_date, datetime):
                age_days = (datetime.now() - creation_date.replace(tzinfo=None)).days
            exp_date = domain_info.expiration_date
            if isinstance(exp_date, list): exp_date = exp_date[0]
            if isinstance(exp_date, datetime):
                expiration_days = (exp_date.replace(tzinfo=None) - datetime.now()).days
        except: pass
        return age_days, expiration_days

    def get_asn_info(self, hostname):
        """Află ASN-ul (identificatorul rețelei) unde este găzduit site-ul."""
        try:
            ip = socket.gethostbyname(hostname)
            reversed_ip = ".".join(reversed(ip.split(".")))
            query = f"{reversed_ip}.origin.asn.cymru.com"
            answers = dns.resolver.resolve(query, 'TXT')
            asn = str(answers[0]).split("|")[0].strip().replace('"', '')
            return int(asn)
        except: return 0

    def get_ssl_info(self, hostname):
        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, 443), timeout=3) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    not_before = datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
                    issuer = dict(x[0] for x in cert['issuer'])
                    issuer_name = issuer.get('organizationName', '')
                    return 1, (datetime.now() - not_before).days, (1 if any(ca in issuer_name for ca in self.free_cas) else 0)
        except: return 0, -1, 1

    def extract_features(self, url):
        features = {}
        ext = tldextract.extract(url)
        domain = f"{ext.domain}.{ext.suffix}"
        hostname = ext.fqdn if ext.fqdn else domain
        age, exp = self.get_whois_data(domain)
        features['domain_age_days'] = age
        features['domain_expiration_days'] = exp
        try: features['has_mx_record'] = 1 if dns.resolver.resolve(domain, 'MX') else 0
        except: features['has_mx_record'] = 0
        ssl_v, cert_a, free_ca = self.get_ssl_info(hostname)
        features['ssl_valid'] = ssl_v
        features['cert_age_days'] = cert_a
        features['is_free_ca'] = free_ca
        features['asn_number'] = self.get_asn_info(hostname)
        return features
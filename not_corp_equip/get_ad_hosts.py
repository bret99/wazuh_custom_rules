from ldap3 import Server, Connection, ALL, NTLM, SUBTREE
import sys
 
domain_controller = '' # insert DOMAIN_CONTROLLER_NAME here; example: 10-dc-001.ad.example.com
domain_controller_ip = '' # insert DOMAIN_CONTROLLER_IP here; example: 10.78.34.13
admin_username = '' # insert DOMAIN_ADMINISTRATOR_USERNAME here
admin_password = '' # insert DOMAIN_ADMINISTRATOR_PASSWORD here
domain_dc = '' # insert DOMAIN_CONTROLLER_DC here; example: example.com

admin_dn = f'{admin_username}@{domain_dc}'
base_dn = '' # insert DOMAIN_CONTROLLER_DN here; example: 'DC=ad,DC=example,DC=com'

server = Server(domain_controller_ip, get_info=ALL)
conn = Connection(server, user=admin_dn, password=admin_password)
conn.bind()

search_filter = '(objectClass=computer)'
page_size = 1000
cookie = None
all_hosts = []
 
while True:
    conn.search(
        base_dn,
        search_filter,
        search_scope=SUBTREE,
        paged_size=page_size,
        paged_cookie=cookie,
        attributes=['cn']
    )
    
    all_hosts.extend(conn.entries)
    
    cookie = conn.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
    if not cookie:
        break
 
print(f"Total hosts found: {len(all_hosts)}")
for host in all_hosts:
    print(host.cn)

conn.unbind()

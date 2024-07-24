from ldap3 import Server, Connection, ALL, NTLM, SUBTREE
import sys
 
domain_controller = 'DOMAIN_CONTROLLER_NAME'
domain_controller_ip = 'DOMAIN_CONTROLLER_IP'
admin_username = 'DOMAIN_ADMINISTRATOR_USERNAME'
admin_password = 'DOMAIN_ADMINISTRATOR_PASSWORD'

admin_dn = f'{admin_username}@rtmis.ru'
base_dn = 'DOMAIN_CONTROLLER_DN' # may contain few values; example: 'DC=ad,DC=example,DC=us'

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

from ldap3 import Server, Connection, ALL, NTLM, SUBTREE

try:
    from Crypto.Hash import MD4  # Ensure pycryptodome is available
except ImportError:
    print("pycryptodome library is not installed. Please install it using 'pip install pycryptodome'.")
    exit(1)


# Configuration
server_address = '' # insert DOMAIN_CONTROLLER_NAME here; example: 10-dc-001.ad.example.com
username = '' # insert DOMAIN_ADMINISTRATOR_USERNAME here; example: example\\john.doe
password = '' # insert DOMAIN_ADMINISTRATOR_PASSWORD here
search_base = '' # insert DOMAIN_CONTROLLER_DN here; example: 'DC=ad,DC=example,DC=com'

# Create the server and connection
server = Server(server_address, get_info=ALL)
conn = Connection(server, user=username, password=password, authentication=NTLM)

# Bind to the server
if not conn.bind():
    print('Error in binding:', conn.result)
    exit()

# Search for disabled accounts
search_filter = '(&(objectCategory=person)(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=2))'
attributes = ['sAMAccountName', 'userAccountControl']

conn.search(search_base, search_filter, search_scope=SUBTREE, attributes=attributes)

# Write results to a text file
with open('/var/ossec/etc/lists/ad_disabled_accounts_prev', 'w') as f:
    for entry in conn.entries:
        f.write(f"{entry.sAMAccountName}\n")

# Close the connection
conn.unbind()

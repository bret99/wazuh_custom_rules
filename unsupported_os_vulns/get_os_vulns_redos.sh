trivy filesystem --using-bdu --scanners vuln --skip-dirs /var/log --format json -o /var/log/pre_vulns.json /
rm -f /var/log/vulns.json
cat /var/log/pre_vulns.json | jq -c '.Results[] | select(.Vulnerabilities != null) | .Vulnerabilities[]' > /var/log/pre_vulns2.json
cat /var/log/pre_vulns2.json > /var/log/vulns.json
rm -f /var/log/pre_vulns.json
rm -f /var/log/pre_vulns2.json

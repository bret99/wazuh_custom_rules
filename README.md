# Wazuh Guard Extensions (WGE)

[![Wazuh Version](https://img.shields.io/badge/Wazuh-4.0+-00A4EF.svg?style=flat-square&logo=wazuh)](https://wazuh.com)
[![Language: Python](https://img.shields.io/badge/Language-Python_3.x-3776AB.svg?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![Language: Bash](https://img.shields.io/badge/Language-Bash-4EAA25.svg?style=flat-square&logo=gnu-bash&logoColor=white)](https://www.gnu.org/software/bash/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![CI Validation](https://img.shields.io/github/actions/workflow/status/bret99/wazuh_custom_rules/wazuh-validator.yml?branch=main&style=flat-square&label=wazuh-logtest)](https://github.com/bret99/wazuh_custom_rules/actions)

A production-ready collection of enterprise-grade custom decoders, rules, and active response scripts for Wazuh SIEM. This repository enhances threat detection capabilities across web servers, authentication systems, and infrastructure components by filling gaps in the default Wazuh ruleset.

## 🚀 Key Features

* **Granular Web Attack Detection:** Enhanced identification of SQL Injections, XSS, and Path Traversal patterns with reduced false-positive rates.
* **Advanced Bruteforce Correlators:** Multi-stage rules tracking distributed and high-frequency authentication failures.
* **Optimized Regex Decoders:** High-performance, non-backtracking regular expressions tailored for Wazuh's analysis engine.
* **Automated Active Response:** Production-hardened shell scripts for instant threat mitigation (IP banning, session termination).

---

## 📂 Repository Structure

* `local_decoder.xml` - Custom extraction logic for non-standard log formats.
* `local_rules.xml` - Categorized XML rulesets structured by threat vectors.

---

## 🛠️ Installation & Deployment

### 1. Deploy Decoders & Rules
Copy the required XML files to your Wazuh Manager manager instance:

```bash
# Copy decoders
cp local_decoder.xml /var/ossec/etc/decoders/

# Copy rules
cp local_rules.xml /var/ossec/etc/rules/
```

### 2. Verify and Restart
Always validate the configuration before restarting the manager service:

```bash
/var/ossec/bin/wazuh-logtest -t
systemctl restart wazuh-manager
```

---

## 🧪 Testing Simulation

You can verify the rules locally using `wazuh-logtest`. Paste your raw log format to see the triggered alert ID and severity mapping:

```bash
/var/ossec/bin/wazuh-logtest
```

### Example Input:
```text
2026-05-15 12:00:00 [ERROR] Failed password for root from 192.168.1.100 port 49152 ssh2
```

### Expected Output:
```text
**Phase 1: Dependencies successfully matched.
**Phase 2: Decoder matched: 'sshd'
**Phase 3: Alert triggered: ID '100201' -> Level '10' (SSH Bruteforce Attempt)
```

---

## 💎 Support the Project

If this tool helps protect your infrastructure, consider supporting the developer! 

### Crypto Wallets
| Asset | Network | Address |
| :--- | :--- | :--- |
| **BTC** | Bitcoin | `bc1qjwl80sv06xj2yhumn6k6xemchryem923wwts5x` |
| **USDT / ETH** | Ethereum (ERC20) | `0xc01b996c7b08ccfad463f27e54f1e74e6ac6f9ff` |
| **USDT / SOL** | Solana | `D7a5CdLaDwkKehnH82y6VJEF3hADWuupuhWCXecHvEnt` |
| **TON** | TON Network | `UQBhPLwdFiJdh6sZ96sZfxrxD9Lu6NFtaUecWeoHSM-EPc0P` |
| **LTC** | Litecoin | `ltc1qkm58ks5kuc64rjwd74sfalc5xsn7h6sr4vt45w` |
| **SOL** | Solana | `D7a5CdLaDwkKehnH82y6VJEF3hADWuupuhWCXecHvEnt` |

---

📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

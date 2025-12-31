# Passive Network Reconnaissance & Security Assessment

This project conducts a **passive reconnaissance audit** of a large academic network to identify publicly visible infrastructure characteristics and potential security risks. Using open-source intelligence (OSINT) and passive scanning tools, the assessment analyzes DNS records, IP address allocations, autonomous system ownership, exposed services, and protocol usage without interacting directly with target systems.

The goal of the project is to demonstrate how much information about an organization’s network can be inferred using only publicly available data, and how that information can inform defensive security decisions.

---

## Project Goals

The primary goals of this project were to:

- Perform ethical, non-intrusive reconnaissance on a real-world network
- Identify publicly exposed infrastructure characteristics
- Detect potential security risks and misconfigurations
- Identify indicators of externally hosted services and Shadow IT
- Evaluate the limitations of passive reconnaissance in IPv6 environments

---

## Methodology

### Reconnaissance Type
- Passive reconnaissance only (no active scanning or exploitation)

### Tools Used
- **Censys** – IP address intelligence, services, and OS fingerprinting
- **DNSDumpster** – DNS and subdomain enumeration
- WHOIS and ASN lookups for ownership verification

### Scope of Analysis
- Public IPv4 address blocks associated with the organization
- DNS records and subdomain resolution
- Autonomous system numbers (ASN) and hosting providers
- Web servers, operating systems, and network protocols
- Comparison of HTTP vs HTTPS exposure
- Visibility challenges introduced by IPv6

---

## Key Findings

- Multiple publicly accessible hosts were serving content over **unencrypted HTTP**, increasing exposure to man-in-the-middle and data interception risks.
- A diverse mix of operating systems and web servers was observed, reflecting typical campus network complexity.
- Several subdomains using the organization’s domain resolved to **external cloud infrastructure**, indicating potential Shadow IT.
- Identified external services were hosted under a different ASN, separate from the organization’s official network.
- IPv6 significantly reduced visibility using traditional passive reconnaissance tools, highlighting a growing blind spot in asset discovery.

---

## Security Observations

### HTTP vs HTTPS
A notable portion of publicly accessible services did not enforce HTTPS. This increases risk to users and systems by allowing plaintext transmission of credentials and session data. Enforcing HTTPS with modern TLS configurations would significantly reduce this exposure.

### Web Server Exposure
Common web servers (Apache, IIS, NGINX) were observed across hosts. While widely used and reliable, misconfiguration, outdated versions, or exposed administrative interfaces can expand the attack surface if not consistently managed and patched.

### Shadow IT Indicators
Subdomains resolving to cloud infrastructure outside the organization’s ASN suggest externally hosted services operating under the institutional domain. These resources may fall outside centralized security monitoring and policy enforcement.

---

## Impact of IPv6

The project highlights how IPv6 complicates traditional reconnaissance and asset discovery. The vast IPv6 address space makes exhaustive scanning impractical, meaning exposed services may remain undiscovered by both attackers and defenders. Organizations must adopt DNS, certificate transparency, and traffic monitoring strategies to maintain visibility in IPv6 environments.

---

## Tools & Technologies

- Passive reconnaissance and OSINT techniques
- DNS and ASN analysis
- Web server and protocol identification
- IPv4 vs IPv6 discovery limitations
- Network security risk assessment

---

## Takeaways

This project demonstrates that significant insight into an organization’s network can be gained without sending a single packet to target systems. Passive reconnaissance remains a powerful technique for both attackers and defenders, particularly for identifying exposed services, Shadow IT, and encryption gaps.

At the same time, the assessment shows that modern networks—especially those using IPv6 and cloud infrastructure—require updated visibility and monitoring strategies to avoid blind spots.

---

## Disclaimer

This project was conducted for educational purposes only and relied exclusively on publicly available data. No systems were accessed, scanned, or modified.

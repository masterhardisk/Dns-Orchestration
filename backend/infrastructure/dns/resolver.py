import dns.resolver

public_resolver = dns.resolver.Resolver()
public_resolver.nameservers = ["8.8.8.8", "8.8.4.4"]
public_resolver.timeout = 3
public_resolver.lifetime = 5


def resolve_domain_ip(domain: str) -> str | None:
    try:
        answers = public_resolver.resolve(domain, "A")
        return answers[0].to_text()
    except Exception:
        return None
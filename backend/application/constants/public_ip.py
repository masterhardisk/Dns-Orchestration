IP_PROVIDERS = {
    "ipify": [
        ("https://api.ipify.org?format=json", "json:ip"),
    ],
    "ipleak": [
        ("https://ipv4.ipleak.net/json", "json:query"),
    ],
    "ifconfig": [
        ("https://ifconfig.me/ip", "text"),
    ],
    "identme": [
        ("https://ident.me", "text"),
    ]
}
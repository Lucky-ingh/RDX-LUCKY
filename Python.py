import nmap

scanner = nmap.PortScanner()
target = "scanme.nmap.org"
scanner.scan(target, '22-80')

for host in scanner.all_hosts():
    print(f"Host: {host} ({scanner[host].hostname()})")
    print("State:", scanner[host].state())
    for proto in scanner[host].all_protocols():
        print("Protocol:", proto)
        ports = scanner[host][proto].keys()
        for port in ports:
            print(f"Port: {port}\tState: {scanner[host][proto][port]['state']}")

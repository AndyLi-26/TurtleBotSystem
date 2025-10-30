with open("path-1k.json", "w") as f:
    f.write('{')
    for i in range(500):
        f.write(f'"s{i}": [[0,{i}]],\n')
    f.write('}')

with open("config-1k.json", "w") as f:
    f.write('{"AGENTS": {')
    for i in range(500):
        f.write(f'"s{i}": "192.168.11.3:8888",\n')
    f.write('},"LOCALISATION_IP": "192.168.11.3:8079","PRECISION": 0.5}')
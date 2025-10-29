with open("path-1k.json", "w") as f:
    for i in range(1024):
        f.write(f'"s{i}": [[0,{i}]],\n')

with open("config-1k.json", "w") as f:
    for i in range(1024):
        f.write(f'"s{i}": "192.168.11.3:8888",\n')

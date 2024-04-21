with open("missing.txt", "r") as f:
    missing = f.readlines()



missing_set = {line[2:-1] for line in missing} 
print(missing_set) 

def remove_chars(chars: list, s:str):
    out = s
    for c in chars:
        out = out.replace(c,"")
    return out

with open("env.yml", "r") as f:
    lines = f.readlines()
removals = []

for i,line in enumerate(lines):
    updated_line = remove_chars(["-", " "], line)[:-1]
    # print(updated_line)
    if updated_line in missing_set:
        removals.append(i)
for rem in removals[::-1]:
    del lines[rem]
with open("env.yml", 'w') as file:
    file.writelines(lines)    
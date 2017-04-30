with open("new_users_handles.txt", "r") as f:
  handles = f.readlines()
  exist = []
  new_handles = []
  for h in handles:
    if h not in exist:
      new_handles.append(h)
      exist.append(h)
  handles = new_handles
  with open("deduped.txt", "w") as g:
    for handle in handles:
      g.write(handle)
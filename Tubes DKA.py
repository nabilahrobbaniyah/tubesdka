import random
import heapq
import math

jumlah_rumah = 100
jumlah_tps = 3
total_gerobak = random.randint(5, 7)
total_truk = random.randint(2, 4)
kapasitas_gerobak = 15
kapasitas_truk = 200
gerobak_mulai = 6 * 60
gerobak_selesai = 15 * 60
truk_mulai = 8 * 60
truk_selesai = 17 * 60

class House:
    def __init__(self, id):
        self.id = f"H{id}"
        self.x = random.randint(0,100)
        self.y = random.randint(0,100)
        self.waste = random.randint(0,7) 
class TPS:
    def __init__(self, id):
        self.id = id
        self.x = random.randint(0,100)
        self.y = random.randint(0,100)
        self.capacity = random.randint(400,500)
        self.current = 0

# untuk assignment rumah ke truk/gerobak
class Vehicle:
    def __init__(self, name, vtype, home_tps):
        self.name = name
        self.vtype = vtype
        self.home_tps = home_tps # zona utamanya
        self.position = home_tps
        self.load = 0 # isi muatan saat ini
        self.cargo_detail = {}
        self.distance = 0
        self.time_used = 0
        self.log = []
        self.start_time = gerobak_mulai if vtype == "gerobak" else truk_mulai
    def free_capacity(self): # sisa kapasitas yang bisa diisi
        if self.vtype == "gerobak":
            return kapasitas_gerobak - self.load
        return kapasitas_truk - self.load

# buat graph
graph = {}
all_nodes = []
houses = [House(i) for i in range(jumlah_rumah)]
tps_nodes = [TPS(f"TPS{i}") for i in range(jumlah_tps)]
all_nodes.extend(houses)
all_nodes.extend(tps_nodes)
for node in all_nodes: # inisialisasi graph
    graph[node.id] = []
for node in all_nodes: # untuk setiap node, buat 2-5 tetangga acak dengan jarak 1-5
    neighbors = random.sample(
        [n for n in all_nodes if n.id != node.id],
        random.randint(1, 5)
    )
    for nb in neighbors: # untuk setiap tetangga, tambahkan ke graph dengan jarak acak
        d = random.randint(1, 5)
        graph[node.id].append((nb.id, d))
        graph[nb.id].append((node.id, d))

# shortest path ucs
def shortest_path(start, goal):
    pq = [(0, start)]
    dist_map = {start: 0}

    while pq:
        cost, node = heapq.heappop(pq)

        if node == goal:
            return cost

        if cost > dist_map.get(node, float('inf')):
            continue

        for nxt, w in graph[node]:
            new_cost = cost + w
            if new_cost < dist_map.get(nxt, float('inf')):
                dist_map[nxt] = new_cost
                heapq.heappush(pq, (new_cost, nxt))

    return 999999

house_zone = {} # untuk menyimpan zona rumah, yaitu TPS terdekatnya
house_tps_distance = {}
for h in houses:
    nearest = None
    best_dist = 999999
    for tps in tps_nodes:
        d = shortest_path(h.id, tps.id)
        if d < best_dist: # jika jarak ke TPS ini lebih dekat, update zona rumah
            best_dist = d
            nearest = tps.id
    house_zone[h.id] = nearest
    house_tps_distance[h.id] = best_dist

def nearest_available_tps(vehicle):
    best = None
    best_cost = 999999
    for tps in tps_nodes:
        if tps.current >= tps.capacity:
            continue
        c = shortest_path(vehicle.position, tps.id)
        if c < best_cost:
            best_cost = c
            best = tps # simpan objek TPS terbaik
    return best, best_cost

def nearest_truck(vehicle):
    best = None
    best_dist = 999999
    for v in vehicles:
        if v.vtype != "truk":
            continue
        free = kapasitas_truk - v.load
        if free <= 0:
            continue
        d = shortest_path(vehicle.position, v.position)
        if d < best_dist:
            best_dist = d
            best = v

    return best, best_dist

def transfer_to_truck(gerobak):
    if gerobak.load <= 0:
        return False

    truck, dist = nearest_truck(gerobak)

    if truck is None:
        return False

    if dist != 0:
        return False

    if not move(gerobak, dist):
        return False

    free = kapasitas_truk - truck.load

    amount = min(gerobak.load, free)

    if amount <= 0:
        return False

    truck.load += amount
    gerobak.load -= amount
    gerobak.time_used += amount * 2

    for hid, kg in list(gerobak.cargo_detail.items()):
        take = min(kg, amount)

        truck.cargo_detail[hid] = (
            truck.cargo_detail.get(hid, 0)
            + take
        )

        gerobak.cargo_detail[hid] -= take

        if gerobak.cargo_detail[hid] <= 0:
            del gerobak.cargo_detail[hid]

        amount -= take

        if amount <= 0:
            break

    t = format_time(
        gerobak.start_time,
        gerobak.time_used
    )

    gerobak.log.append(
        f"{t} - titip sampah ke {truck.name}"
    )

    return True

def best_house(vehicle):

    best = None
    best_score = -999999
    best_dist = 0

    zone = vehicle.home_tps

    for h in houses:

        if h.waste <= 0:
            continue

        if house_zone[h.id] != zone:
            continue

        d = shortest_path(
            vehicle.position,
            h.id
        )

        score = h.waste * 2 - d

        if score > best_score:
            best_score = score
            best = h
            best_dist = d

    return best, best_dist

def max_operating_time(vehicle):
    if vehicle.vtype == "gerobak":
        return gerobak_selesai - gerobak_mulai
    return truk_selesai - truk_mulai
def can_move(vehicle, dist):
    if vehicle.vtype == "gerobak":
        t = dist * 3
    else:
        t = dist * (3 / 5)
    return (
        vehicle.time_used + t
        <= max_operating_time(vehicle)
    )
def can_load(vehicle, kg):
    if vehicle.vtype == "gerobak":
        t = kg * 2
    else:
        t = (kg / 10) * 2
    return (
        vehicle.time_used + t
        <= max_operating_time(vehicle)
    )
# TIME
def move(vehicle, dist):
    if not can_move(vehicle, dist):
        return False
    vehicle.distance += dist
    if vehicle.vtype == "gerobak":
        t = dist * 3
    else:
        t = dist * (3 / 5)
    vehicle.time_used += t
    return True

def load_house(vehicle, house, dist):
    cap = vehicle.free_capacity() # sisa kapasitas yang bisa diisi
    take = min(cap, house.waste) # min untuk memastikan tidak mengambil lebih dari yang bisa diangkut atau yang tersedia di rumah
    if take <= 0:
        return False
    if not can_load(vehicle, take):
        return False
    house.waste -= take
    vehicle.load += take
    vehicle.cargo_detail[house.id] = (vehicle.cargo_detail.get(house.id, 0) + take) # angka 0 untuk default jika rumah ini belum pernah diambil sebelumnya
   
    t = format_time(vehicle.start_time, vehicle.time_used)
    vehicle.log.append(f"{t} - {vehicle.name} ambil {take}kg dari {house.id} | jarak: {dist}")
    return True

def dump_to_tps(vehicle):
    if vehicle.load <= 0:
        return
    tps, dist = nearest_available_tps(vehicle)
    if tps is None:
        return
    if not move(vehicle, dist):
        return
    vehicle.position = tps.id
    can_dump = min(vehicle.load, tps.capacity - tps.current)
    remaining = can_dump
    dumped_from = [] # untuk mencatat dari rumah mana saja sampah yang dibuang ke TPS ini, dalam format "Hid:kg"
    for hid in list(vehicle.cargo_detail.keys()): # hid = id rumah yang diangkut
        if remaining <= 0:
            break
        amt = vehicle.cargo_detail[hid] # amt= jumlah yang diangkut dari rumah hid
        taken = min(amt, remaining) # jumlah yang diambil dari rumah ini untuk dibuang ke TPS
        dumped_from.append(f"{hid}:{taken}kg")
        vehicle.cargo_detail[hid] -= taken # update sisa yang diangkut dari rumah ini setelah dibuang ke TPS
        if vehicle.cargo_detail[hid] <= 0: # jika sudah habis, hapus dari cargo_detail
            del vehicle.cargo_detail[hid]
        remaining -= taken
    tps.current += can_dump
    vehicle.load -= can_dump
    if vehicle.vtype == "gerobak": # waktu yang dibutuhkan untuk membuang sampah ke TPS
        vehicle.time_used += can_dump * 2
    else:
        vehicle.time_used += (can_dump / 10) * 2
    detail = ", ".join(dumped_from)
    t = format_time(vehicle.start_time, vehicle.time_used)
    vehicle.log.append(f"{t} - {vehicle.name} buang {can_dump}kg ke {tps.id}")

def format_time(start_minutes, elapsed):
    total = start_minutes + int(elapsed)
    h = total // 60
    m = total % 60
    return f"{h:02d}.{m:02d}"

vehicles = []

used_gerobak = 0
used_truk = 0

# 1. JAMIN MINIMAL 1 GEROBAK PER TPS
for tps in tps_nodes:
    if used_gerobak < total_gerobak:
        vehicles.append(Vehicle(f"G{used_gerobak}", "gerobak", tps.id))
        used_gerobak += 1

# 2. JAMIN MINIMAL 1 TRUK PER TPS
for tps in tps_nodes:
    if used_truk < total_truk:
        vehicles.append(Vehicle(f"T{used_truk}", "truk", tps.id))
        used_truk += 1

# 3. SISA GEROBAK RANDOM
for i in range(used_gerobak, total_gerobak):
    tps = random.choice(tps_nodes)
    vehicles.append(Vehicle(f"G{i}", "gerobak", tps.id))

# 4. SISA TRUK RANDOM
for i in range(used_truk, total_truk):
    tps = random.choice(tps_nodes)
    vehicles.append(Vehicle(f"T{i}", "truk", tps.id))

def operate_one_step(vehicle):

    max_time = (
        gerobak_selesai - gerobak_mulai
        if vehicle.vtype == "gerobak"
        else truk_selesai - truk_mulai
    )

    if vehicle.time_used >= max_time:
        return

    house, dist = best_house(vehicle)

    if house is None:

        if vehicle.load > 0:
            dump_to_tps(vehicle)

        return

    if not move(vehicle, dist):
        return

    vehicle.position = house.id

    if not load_house(vehicle, house, dist):
        return

    # kalau sudah penuh atau rumah habis
    if vehicle.load >= vehicle.free_capacity() + vehicle.load:
        dump_to_tps(vehicle)

    elif vehicle.load > 0:
        dump_to_tps(vehicle)

active = True
iteration = 0
max_iter = 10000
while active and iteration < max_iter:
    iteration += 1
    active = False
    for v in vehicles:
        before = v.time_used
        operate_one_step(v)
        if v.time_used > before:
            active = True

# REPORT
print("\nTPS ")
for t in tps_nodes:
    print(t.id, "isi:", t.current, "/", t.capacity)

print("\nkendaraan ")
total_distance = 0
for v in vehicles:
    total_distance += v.distance
    print( v.name, "| waktu:", round(v.time_used, 2), "| jarak:", v.distance, "| sisa muatan:", v.load, "kg", "| zona:", v.home_tps)
print("\ntotal jarak semua kendaraan:", total_distance)

print("\nSisa sampah rumah")
remain = sum(h.waste for h in houses) # total sampah yang masih tersisa di rumah-rumah
print(remain)
# print rumah yang masih punya sampah di semua zona
for zone in set(house_zone.values()):
    print(f"\nZona {zone}:")
    for h in houses:
        if house_zone[h.id] == zone and h.waste > 0:
            print(f"{h.id}: {h.waste}kg | jarak ke TPS: {house_tps_distance[h.id]}")

print("\nlog aktivitas kendaraan")
for v in vehicles:
    print("\n", v.name)
    for item in v.log[:20]:
        print(item)

import matplotlib.pyplot as plt

plt.figure(figsize=(10,8))

for h in houses:
    plt.scatter(h.x, h.y, s=20)

for t in tps_nodes:
    plt.scatter(
        t.x,
        t.y,
        marker="*",
        s=300
    )

plt.title("Peta Penduduk Desa")
plt.grid(True)
plt.show()
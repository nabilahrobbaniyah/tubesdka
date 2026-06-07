import random
import heapq

# langkah langkah:
# 1. buat graph jalanan antar rumah dan TPS
# 2. buat fungsi untuk cari shortest path antar node (ucs)
# 3. buat fungsi untuk cari rumah terbaik untuk dikunjungi (prioritaskan yang dekat TPS untuk gerobak, jauh dari TPS untuk truk)
# 4. buat fungsi untuk cek apakah kendaraan bisa bergerak ke suatu node (cek waktu operasional)
# 5. buat fungsi untuk cek apakah kendaraan bisa mengambil sampah dari rumah (cek kapasitas dan waktu)
# 6. buat fungsi untuk cek apakah kendaraan bisa membuang sampah ke TPS (cek kapasitas TPS dan waktu)
# 7. buat loop operasi kendaraan sampai semua kendaraan tidak bisa bergerak lagi

total_rumah = 100
jumlah_tps = 3
# RANDOMISASI JUMLAH KENDARAAN
total_gerobak = random.randint(5, 7)
total_truk = random.randint(1, 4)
kapasitas_gerobak = 15
kapasitas_truk = 200
gerobak_mulai = 6 * 60
gerobak_selesai = 15 * 60
truk_mulai = 8 * 60
truk_selesai = 17 * 60

# 70 rumah untuk truk, 30 rumah untuk gerobak
class House:
    def __init__(self, id_): # id_ dari 0 sampai 99
        self.id = f"H{id_}"
        self.waste = random.randint(0, 7) # jumlah sampah di satu rumah, dalam kg
class TPS:
    def __init__(self, id_):
        self.id = id_
        self.capacity = random.randint(400, 500) # kapasitas TPS dalam kg
        self.current = 0 # jumlah sampah yang sudah ada di TPS

# untuk assignment rumah ke truk/gerobak
class Vehicle:
    def __init__(self, name, vtype, home_tps):
        self.name = name
        self.vtype = vtype
        self.home_tps = home_tps
        self.position = home_tps
        self.load = 0
        self.cargo_detail = {}
        self.distance = 0
        self.time_used = 0
        self.log = []
    def free_capacity(self): # sisa kapasitas yang bisa diisi
        if self.vtype == "gerobak":
            return kapasitas_gerobak - self.load
        return kapasitas_truk - self.load

# buat graph
graph = {}
all_nodes = []
houses = [House(i) for i in range(total_rumah)]
tps_nodes = [TPS(f"TPS{i}") for i in range(jumlah_tps)]
all_nodes.extend(houses)
all_nodes.extend(tps_nodes)
for node in all_nodes: # inisialisasi graph
    graph[node.id] = []
for node in all_nodes: # graph random
    neighbors = random.sample(
        [n for n in all_nodes if n.id != node.id],
        random.randint(2, 5)
    )
    for nb in neighbors:
        d = random.randint(1, 5)
        graph[node.id].append((nb.id, d))
        graph[nb.id].append((node.id, d))

# shortest path ucs
def shortest_path(start, goal):
    pq = []
    heapq.heappush(pq, (0, start))
    visited = set()
    while pq:
        cost, node = heapq.heappop(pq)
        if node == goal:
            return cost
        if node in visited:
            continue
        visited.add(node)
        for nxt, dist in graph[node]:
            if nxt not in visited:
                heapq.heappush(
                    pq,
                    (
                        cost + dist,
                        str(nxt)
                    )
                )
    return 999999

house_zone = {}
for h in houses:
    nearest = None
    best_dist = 999999
    for tps in tps_nodes:
        d = shortest_path(
            h.id,
            tps.id
        )
        if d < best_dist:
            best_dist = d
            nearest = tps.id
    house_zone[h.id] = nearest
# HELPERS
def nearest_available_tps(vehicle):
    best = None
    best_cost = 999999
    for tps in tps_nodes:
        if tps.current >= tps.capacity:
            continue
        c = shortest_path(
            vehicle.position,
            tps.id
        )
        if c < best_cost:
            best_cost = c
            best = tps
    return best, best_cost

def best_house(vehicle):
    best = None
    best_score = -999
    best_dist = 0
    zone = vehicle.home_tps
    for h in houses:
        if h.waste <= 0:
            continue
        if house_zone[h.id] != zone:
            continue
        d = shortest_path(vehicle.position,h.id)
        tps_dist = shortest_path(h.id, zone)
        if vehicle.vtype == "gerobak":
            # prioritaskan dekat TPS
            if tps_dist > 5:
                continue
            score = (h.waste * 2- d- tps_dist
            )
        else:
            # prioritaskan jauh TPS
            if tps_dist <= 5:
                continue
            score = (
                h.waste * 2
                + tps_dist
                - d
            )
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

def load_house(vehicle, house):
    cap = vehicle.free_capacity()
    take = min(
        cap,
        house.waste
    )
    if take <= 0:
        return False
    if not can_load(vehicle, take):
        return False
    house.waste -= take
    vehicle.load += take
    vehicle.cargo_detail[h.id] = (
        vehicle.cargo_detail.get(h.id, 0) + take
    )
    if vehicle.vtype == "gerobak":
        vehicle.time_used += take * 2
    else:
        vehicle.time_used += (take / 10) * 2
    return vehicle.log.append(
        f"{vehicle.name} ambil {take}kg dari {house.id}"
    )

def dump_to_tps(vehicle):

    if vehicle.load <= 0:
        return

    tps, dist = nearest_available_tps(vehicle)

    if tps is None:
        return

    if not move(vehicle, dist):
        return

    vehicle.position = tps.id

    can_dump = min(
        vehicle.load,
        tps.capacity - tps.current
    )

    remaining = can_dump

    dumped_from = []

    for hid in list(vehicle.cargo_detail.keys()):

        if remaining <= 0:
            break

        amt = vehicle.cargo_detail[hid]

        taken = min(
            amt,
            remaining
        )

        dumped_from.append(
            f"{hid}:{taken}kg"
        )

        vehicle.cargo_detail[hid] -= taken

        if vehicle.cargo_detail[hid] <= 0:
            del vehicle.cargo_detail[hid]

        remaining -= taken

    tps.current += can_dump
    vehicle.load -= can_dump

    detail = ", ".join(dumped_from)

    vehicle.log.append(
        f"{vehicle.name} buang "
        f"{can_dump}kg "
        f"ke {tps.id}"
    )

# OPERATE
vehicles = []

# buat gerobak secara random
for i in range(total_gerobak):
    tps = random.choice(tps_nodes)
    vehicles.append(
        Vehicle(
            f"gerobak_{i}",
            "gerobak",
            tps.id
        )
    )

# buat truk secara random
for i in range(total_truk):
    tps = random.choice(tps_nodes)
    vehicles.append(
        Vehicle(
            f"truk_{i}",
            "truck",
            tps.id
        )
    )

def operate(vehicle):
    max_time = gerobak_selesai - gerobak_mulai \
        if vehicle.vtype == "gerobak" \
        else truk_selesai - truk_mulai
    while vehicle.time_used < max_time:
        if vehicle.load >= (
            kapasitas_gerobak
            if vehicle.vtype == "gerobak"
            else kapasitas_truk
        ):
            dump_to_tps(vehicle)
            continue
        house, dist = best_house(vehicle)
        if house is None:
            break
        move(vehicle, dist)
        vehicle.position = house.id
        load_house(vehicle, house)
        if vehicle.load > 0:
            dump_to_tps(vehicle)
        if not move(vehicle, dist):
            return
        vehicle.position = house.id
        if not load_house(vehicle, house):
            return
# RUN
def operate_one_step(vehicle):
    max_time = (
        gerobak_selesai - gerobak_mulai
        if vehicle.vtype == "gerobak"
        else truk_selesai - truk_mulai
    )
    if vehicle.time_used >= max_time:
        return
    if vehicle.load >= (
        kapasitas_gerobak
        if vehicle.vtype == "gerobak"
        else kapasitas_truk
    ):
        dump_to_tps(vehicle)
        return
    house, dist = best_house(vehicle)
    if house is None:
        return
    move(vehicle, dist)
    vehicle.position = house.id
    load_house(vehicle, house)
    if vehicle.load > 0:
        dump_to_tps(vehicle)
active = True
while active:
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
    print( v.name, "| waktu:", round(v.time_used, 2), "| jarak:", v.distance, "| sisa muatan:", v.load, "kg")
print("\ntotal jarak semua kendaraan:", total_distance)
print("\nSisa sampah rumah")
remain = sum(h.waste for h in houses)
print(remain)
print("\nlog aktivitas kendaraan")
for v in vehicles:
    print("\n", v.name)
    for item in v.log[:20]:
        print(item)

"""확정 LOG 01~10의 논리와 선택지 유일성을 검산한다."""

from itertools import permutations


def check():
    assert 5 * (5 + 1) == 30  # LOG 01
    assert 10 - 2 == 8  # LOG 02: 첫날 사용 + 마지막 단독 상자

    edges = [("A", "C"), ("B", "A"), ("C", "B"), ("C", "D"),
             ("D", "F"), ("E", "D"), ("F", "A")]
    assert [p for p in "ABCD" if sum(a == p for a, _ in edges) == 2] == ["C"]

    # LOG 04: 6석 원탁에서 A의 위치를 0으로 고정한다.
    valid_seats = []
    for order in permutations("BCDEF"):
        seats = ("A",) + order
        pos = {person: i for i, person in enumerate(seats)}
        if pos["E"] != (pos["A"] + 1) % 6:
            continue
        if pos["D"] != (pos["A"] - 1) % 6:
            continue
        if pos["C"] != (pos["D"] + 3) % 6:
            continue
        if any((pos["B"] - pos[p]) % 6 in (1, 5) for p in ("A", "D")):
            continue
        valid_seats.append(seats)
    assert len(valid_seats) == 1
    seats = valid_seats[0]
    assert seats[(seats.index("E") + 3) % 6] == "F"

    choices5 = ["A,B,C,F", "A,C,E,F", "B,C,D,F", "A,D,E,F"]
    def allowed5(choice):
        crew = set(choice.split(","))
        return (len(crew) == 4 and
                ("A" not in crew or "B" in crew) and
                not {"C", "D"} <= crew and
                ("E" not in crew or "A" not in crew))
    assert [x for x in choices5 if allowed5(x)] == ["A,B,C,F"]

    choices6 = ["C-B-E-A-D", "B-C-E-D-A", "C-D-E-B-A", "B-A-E-C-D"]
    def allowed6(choice):
        seq = choice.split("-")
        return (seq[2] == "E" and seq.index("C") < seq.index("A") and
                seq.index("B") < seq.index("D") < seq.index("A"))
    assert [x for x in choices6 if allowed6(x)] == ["B-C-E-D-A"]

    assert (12 - 1) * (10 // (6 - 1)) == 22  # LOG 07
    assert 17 % 4 == 1  # LOG 08: 1개를 먼저 가져가 16개를 남긴다.

    plates = list(range(1, 9))
    removed = [plates.pop(0)]
    idx = 0
    while len(plates) > 1:
        idx = (idx + 1) % len(plates)  # 다음 남은 접시=첫 번째, 그 다음=두 번째
        removed.append(plates.pop(idx))
        idx %= len(plates)
    assert removed == [1, 3, 5, 7, 2, 6, 4]
    assert plates == [8]

    def true_claims(door):
        return sum([door == "B", door != "C", door != "B"])
    assert [d for d in "ABC" if true_claims(d) == 1] == ["C"]


if __name__ == "__main__":
    check()
    print("LOG 01~10 logic verified")

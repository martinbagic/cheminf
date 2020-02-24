from . import hack

from collections import defaultdict


class Poset:
    def __init__(self, genfunc, roots, canonicalizer):
        self.genfunc = genfunc
        self.roots = roots
        self.canonicalizer = canonicalizer

    def __call__(self):
        stack = set(self.roots)

        P = defaultdict(set)
        C = defaultdict(set)
        S = defaultdict(set)

        seen = set()

        while stack:
            print('STACK LEN = ', len(stack))
            a = stack.pop()
            seen.add(a)

            resolve = seen - {a}

            while resolve:
                b = resolve.pop()

                if b in S[a] or b in P[a] or b in C[a]:  # already explored
                    continue

                x = self.genfunc(a, b)

                if self.canonicalizer:
                    x = self.canonicalizer(x)

                if a == x:  # a = x < b; b is a parent of a
                    C[b].add(a)
                    P[a].add(b)

                    for p in P[b]:  # all parents of b are parents of a
                        P[a].add(p)
                        C[p].add(a)
                        resolve -= {p}

                    for c in C[a]:  # all children of a are children of b
                        P[c].add(b)
                        C[b].add(c)
                        resolve -= {c}

                elif b == x:  # a > x = b; a is a parent of b
                    C[a].add(b)
                    P[b].add(a)

                    for p in P[a]:  # all parents of a are parents of b
                        P[b].add(p)
                        C[p].add(b)
                        resolve -= {p}

                    for c in C[b]:  # all children of b are children of a
                        P[c].add(a)
                        C[a].add(c)
                        resolve -= {c}

                else:  # a > x < b; a and b are siblings and x their child
                    S[a].add(b)
                    S[b].add(a)

                    C[a].add(x)
                    C[b].add(x)
                    P[x].add(a)
                    P[x].add(b)

                    stack.add(x)  # new node, need to investigate

        print(seen)

        return C

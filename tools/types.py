numbers = {}

for i in range(30):
    numbers[i] = "(\\f.\\x.{0}x{1})".format(" ".join(["(f ", ] * i), "".join([")", ] * i))

type_true = "(\\x.\\y.x)"

type_false = "(\\x.\\y.y)"

type_not = ("(\\a.a {0} {1})".format(type_false, type_true))

type_is_zero = "(\\n.n (\\x.{0}) {1})".format(type_false, type_true)

type_is_even = "(\\n.n {0} {1})".format(type_not, type_true)

type_add = "(\\a.\\b.\\f.\\x.a f (b f x))"

type_mul = "(\\a.\\b.a ({0} b) {1})".format(type_add, numbers[0])

type_pow = "(\\a.\\b.b ({0} a) {1})".format(type_mul, numbers[1])

type_pow2 = "(\\a.\\b.b a)"

type_minus = "(\\a.\\b.b (\\n.n (\\p.\\f.f (p (\\a.\\b.b)) \\f.\\x.f (p (\\a.\\b.b) f x)) " \
             "(\\f.f (\\f.\\x.x) \\f.\\x.x) \\a.\\b.a) a)"
type_S = "(\\x.\\y.\\z.x z (y z))"

type_K = "(\\x.\\y.x)"

type_I = "(\\x.x)"

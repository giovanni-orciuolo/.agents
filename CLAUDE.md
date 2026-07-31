# Software Engineering Standards

Applies when writing, refactoring, reviewing, designing, or debugging code in any language.

## Objective

Code exists to serve users, and to be cost-effectively maintained by developers. Optimize for how
easily the next person can **discover, understand, change, test, debug, and deploy** it. Developers
read code far more often than they write it.

Two failure modes, equally bad:
- **Under-designed** — god objects, primitive obsession, no tests, tangled dependencies.
- **Over-designed** — abstractions for hypothetical futures, ceremony, indirection with no payoff.

When these pull in opposite directions, prefer the simpler thing that is still testable.

---

## Test-Driven Development

**Red → Green → Refactor.** Design happens during REFACTOR, not while writing the implementation.

The three laws:
1. No production code except to make a failing test pass.
2. No more test code than is sufficient to fail (compile errors count as failing).
3. No more production code than is sufficient to pass the one failing test.

**RED** — write a failing test describing behavior in domain language. Concrete example, not abstract
statement. Assert on observable behavior, never on implementation detail.

**GREEN** — simplest code that passes. *Fake It* (return a constant) is legitimate and often preferable
to jumping straight to the general solution; let further tests force generality.

**REFACTOR** — remove duplication (see Rule of Three), extract long methods, fix names that drifted,
simplify conditionals.

**Transformation Priority Premise** — when moving RED→GREEN, prefer earlier transformations:
`{} → nil → constant → variable → unconditional → conditional → scalar → collection → recursion → mutation`.
Jumping to a late transformation early means the tests aren't driving the design.

**Test naming** — behavior and domain language, one example per test:
```
BAD:  it('can add numbers')          it('should set the data property to 1')
GOOD: it('when adding 2 + 3, returns 5')   it('recognizes "mom" as a palindrome')
```

Structure every test **Arrange-Act-Assert**. When stuck, write it backwards: assert first, then the
act that produces it, then the arrange it requires.

Start with real collaborators (classic TDD). Introduce test doubles only at genuine infrastructure
boundaries — databases, network, clock, filesystem. Heavy mocking of your own domain objects means the
tests assert your design back at you and prove nothing.

---

## SOLID

| Principle | Question to ask | Red flag |
|---|---|---|
| **S**RP | Does this have ONE reason to change? | Describing it requires "and" |
| **O**CP | Can I extend without modifying? | `if/else` chain on a type field |
| **L**SP | Can subtypes replace base types safely? | Type-checking in calling code |
| **I**SP | Are clients forced to depend on unused methods? | `throw new Error('not implemented')` |
| **D**IP | Do high-level modules depend on abstractions? | `new ConcreteThing()` inside business logic |

These scale past classes: SRP → one responsibility per bounded context; OCP → new features arrive as
new modules; DIP → business logic knows nothing about databases or frameworks.

**The Dependency Rule.** Source dependencies point inward, toward policy:
`Infrastructure → Application → Domain`. The domain defines the interfaces it needs; infrastructure
implements them. Inner layers know nothing of outer layers. Never the reverse.

---

## Naming

In priority order:
1. **Consistency** — one name per concept, the same name everywhere. Not `getUser` / `fetchCustomer` /
   `retrieveClient` for the same idea.
2. **Understandability** — domain language over technical jargon.
3. **Specificity** — ban vague nouns: `data`, `info`, `manager`, `handler`, `processor`, `utils`.
4. **Brevity** — short, but never at the cost of clarity. Not `usrLst`, not
   `listOfAllActiveUsersInTheSystem`.
5. **Searchability** — unique enough to grep.
6. **Pronounceability** — you must be able to say it out loud.
7. **Austerity** — drop filler: `UserData` → `User`, `UserClass` → `User`.

Don't abbreviate. If a name is too long to type comfortably, the thing it names is doing too much.

---

## Structure & Size

Treat these as **thresholds that trigger a question**, not laws that trigger an immediate rewrite. When
one trips, ask "is this doing too much?" — usually yes, occasionally no.

- One level of indentation per method. Extract, don't nest.
- **No `else`.** Guard clauses, early returns, or polymorphism.
- Methods under ~10 lines; classes under ~50; files under ~100.
- More than 2–3 instance variables suggests a missing intermediate object.
- More than 3 parameters suggests a missing parameter object.
- **One dot per line** (Law of Demeter). `order.customer.address.city` → `order.shippingCity()`.
  Only call methods on `this`, on parameters, on objects you created, and on your direct components.
- Wrap collections in a class that owns their behavior rather than exposing a bare array whose
  invariants every caller must remember.
- Code reads top-to-bottom like a story: public API first, supporting detail below, in call order.

---

## Value Objects, Entities, and Behavior

**Wrap domain primitives in types.** IDs, emails, money, quantities, dates-with-meaning. The wrapper
validates on construction, so invalid values cannot exist, and the type system stops argument
transposition:

```ts
// BAD  — nothing prevents createOrder(email, userId)
function createOrder(userId: string, email: string)

// GOOD — validated at the boundary, unswappable
class Email  { constructor(private readonly value: string) { /* validate or throw */ } }
class UserId { constructor(private readonly value: string) {} }
function createOrder(userId: UserId, email: Email)
```

Apply this to concepts with rules or meaning. A local loop counter or an opaque pass-through string
does not need a wrapper — that is ceremony, not design.

- **Value objects** — identity is their attributes. Immutable. Compared by value. `Money`, `Email`,
  `DateRange`.
- **Entities** — identity survives attribute change. Mutated only through intention-revealing methods.
  Compared by identity. `User`, `Order`.
- **Aggregates** — one root is the only entry point; the root enforces invariants for the cluster.
  External code never reaches inside to mutate a child.

**Tell, don't ask.** Behavior belongs with the data it operates on. Don't interrogate an object and
then make its decisions for it:

```ts
// BAD  — caller owns the rule, and every caller must reimplement it
if (account.getBalance() >= amount) account.setBalance(account.getBalance() - amount);

// GOOD — the object owns its invariant
const result = account.withdraw(amount);
```

Accessors that merely expose fields turn objects into data bags and scatter their rules across callers.
Expose behavior; expose state only when a caller genuinely needs to render or serialize it.

**Design by contract** — for each method be clear on preconditions, postconditions, and the invariants
the object always maintains. Enforce preconditions at construction where possible.

**Composition over inheritance.** Inheritance couples you to a base class you don't control and forces
an "is-a" that usually isn't. Inject collaborators instead. Reserve inheritance for true is-a
relationships, framework requirements, and deliberate Template Method.

**Polymorphism over type switching.** A `switch` on a type field that appears in more than one place is
a missing set of types.

---

## Complexity

**Essential** complexity is inherent to the domain — express it clearly. **Accidental** complexity comes
from your own solutions — eliminate it.

Symptoms worth naming out loud:
- **Change amplification** — "to add this field I must edit 15 files." Boundaries are wrong.
- **Cognitive load** — "I must understand 10 classes to understand this one." Coupling is too tight.
- **Unknown unknowns** — "I changed this and something unrelated broke." Hidden state or implicit
  contracts.

**YAGNI** — build for the requirement in front of you. "We might need it later", "just in case", "for
future extensibility" are the tells. Guessing future needs produces the wrong abstraction, and the
wrong abstraction costs more than the duplication it replaced.

**KISS** — start with the obvious solution. Prefer boring and well-understood. Question every layer of
indirection: what would break if it were gone?

**DRY, gated by the Rule of Three:**
```
Duplication #1 → leave it
Duplication #2 → notice it, leave it
Duplication #3 → NOW extract
```
> A little duplication is far better than the wrong abstraction.

Two pieces of code that look alike but change for different reasons are not duplication. Only extract
when they share a *reason to change*.

**Separation of concerns** — split business logic from infrastructure, policy from mechanism, input from
processing from output.

**Boy Scout Rule** — leave code better than you found it. One name, one extraction, one missing test per
visit. Don't refactor code that works and won't change, code about to be deleted, or code with no test
coverage to protect you.

---

## Architecture

**Feature-first, not layer-first.** Group by what changes together:
```
GOOD  src/users/{User,UserService,UserRepository}   BAD  src/controllers/, src/services/,
      src/orders/{Order,OrderService,...}                src/repositories/
```
Within a feature, separate domain / application / infrastructure / presentation. The domain layer has
zero dependencies on the others.

- Interfaces are the contracts at boundaries; the consumer defines them, not the provider.
- Handle cross-cutting concerns (logging, auth, error handling) at the edge — middleware, decorators —
  not scattered through business logic.
- **Walking skeleton** — get the thinnest end-to-end slice deployable early to prove the architecture,
  then flesh out features.

Architectural red flags: circular module dependencies; domain importing infrastructure; framework types
in business logic; shared mutable state across modules; a `utils`/`common` package that only grows; the
database schema dictating the domain model.

---

## Code Smells → Refactoring

Stop and fix when you see:

| Smell | Move |
|---|---|
| Long method | Extract method / compose method |
| Large class | Extract class along responsibility lines |
| Long parameter list | Introduce parameter object |
| Data clumps (same args travel together) | Extract class |
| Primitive obsession | Wrap in value object |
| Switch/if-else on type | Replace with polymorphism |
| Divergent change (one class, many reasons) | Split by responsibility |
| Shotgun surgery (one change, many classes) | Move related code together |
| Feature envy (uses another's data more than own) | Move method to that class |
| Inappropriate intimacy | Move method / extract class |
| Message chains `a.getB().getC()` | Hide delegate |
| Middle man (pure delegation) | Inline it |
| Refused bequest (unused inherited members) | Replace inheritance with delegation |
| Speculative generality | Delete it (YAGNI) |
| Dead code, comments explaining bad code | Delete / rename / extract |

Before refactoring: confirm it's actually a problem, ensure test coverage exists, move in small steps
with tests green, commit often.

---

## Design Patterns

Know them; don't reach for them. **Let patterns emerge from refactoring** — they solve problems you
have, not problems you might have. A pattern applied speculatively is just accidental complexity with
a respectable name.

Anti-patterns: God Object, Golden Hammer (one pattern for everything), premature optimization
(profile first), copy-paste programming, `SomethingFactoryProvider` for a job a function would do.

---

## Comments

Comments explain **why** — business reasons, non-obvious constraints, warnings. Code explains what and
how. If a comment is needed to explain what code does, rename or extract until it isn't.

```ts
// BAD:  Add 1 to counter
// GOOD: Compensate for the legacy API's 0-based page index
```

Match the comment density and idiom of the surrounding file. Don't annotate the obvious.

---

## Language Notes

**JS/TS** — when checking an untrusted string against an object or map, use `Object.hasOwn(obj, key)`
(or `Object.prototype.hasOwnProperty.call`). Never the `in` operator: it matches prototype keys like
`toString` and `constructor`.

---

## Working Checklist

**Before coding**
- [ ] Do I understand the requirement well enough to state acceptance criteria?
- [ ] What is the first failing test?
- [ ] What is the simplest thing that could work?
- [ ] Am I solving a real problem or a hypothetical one?

**While coding**
- [ ] Is this still the simplest thing that works?
- [ ] Does this class have one responsibility?
- [ ] Am I depending on an abstraction or a concretion?
- [ ] Can I name this more precisely?
- [ ] Is there duplication to extract yet? (Rule of Three)

**After it works**
- [ ] Do all tests pass? (Run them. Don't assume.)
- [ ] Any dead code to delete?
- [ ] Any complex condition to simplify or name?
- [ ] Are the names still accurate after the changes?
- [ ] Would someone unfamiliar understand this in six months?

---

## Stop and Rethink

- Writing production code with no failing test driving it
- A class that knows about everything
- A method that needs scrolling, or nests more than one level deep
- `else` where an early return would do
- Passing raw primitives for domain concepts with rules
- Depending on a concrete implementation in business logic
- Hardcoding what belongs in configuration
- Creating an abstraction before the third duplication
- Adding capability "just in case"
- Claiming something is done, fixed, or passing without having run it

> Focus on WHAT needs to happen, not HOW it needs to happen.

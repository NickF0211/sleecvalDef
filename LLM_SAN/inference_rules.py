CONFLICTS = "conflicts"
ME = "ME"
WITNESS = "witness"
HB = "HB"
IMPLIES = "implies"
EQ = "equals"
JUSTIFICATION = "justification"

all_relations = [WITNESS, CONFLICTS, HB, IMPLIES, EQ, ME]
commute = [CONFLICTS, EQ, ME]
EVENT_REL = [WITNESS, CONFLICTS, HB]
MEASURE_REL = [IMPLIES, EQ, ME]


def get_delta(new_result, old_result):

    delta = []
    for r in old_result:
        if r in new_result:
            delta.append(r)
    return delta
def get_compare_result(raw_result, new_result):
    num_deleted = 0
    num_added = 0
    raw_relations = raw_result["relations"]
    new_relations = new_result["relations"]
    for r in raw_relations:
        if r not in new_relations:
            num_deleted += 1

    for r in new_relations:
        if r not in raw_relations:
            num_added += 1

    print("number of added {} and number of deleted {}".format(num_added, num_deleted))


def get_summary(result):
    relations = result["relations"]
    print("numer of rels {}".format(len(relations)))


def pair_sort(a, b):
    return min(a, b), max(a, b)


def FALSE(content):
    if isinstance(content, bool):
        return content is False
    elif isinstance(content, str):
        return content.lower() == "false" or content.lower().startswith('f')


def TRUE(content):
    if isinstance(content, bool):
        return content is True
    elif isinstance(content, str):
        return content.lower() == "true" or content.lower().startswith('t')


class TestCase:
    TestCase_connection = {}

    def __init__(self, rel_name, a, b, outcome="{fill in here, true of false}",
                 justification="{fill in your justification}"):
        self.rel_name = rel_name
        self.a = a
        self.b = b
        self.outcome = outcome
        self.justification = justification

    def to_json(self):
        if self.rel_name in EVENT_REL:
            return {"Relationship": {"event1": self.a, "event2": self.b, JUSTIFICATION: self.justification,
                                     self.rel_name: self.outcome}}
        elif self.rel_name in MEASURE_REL:
            return {"Relationship": {"measure1": self.a, "measure2": self.b, JUSTIFICATION: self.justification,
                                     self.rel_name: self.outcome}}
        else:
            print("Unsupported relation type")
            assert False

    def prompt_questions(self):
        assert isinstance(self.outcome, str)
        return self.to_json()

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "{} {} {}".format(self.a, self.rel_name, self.b)

    def __hash__(self):
        hash_value = hash(self.__repr__())
        return hash_value

    def __eq__(self, other):
        return self.__repr__() == other.__repr__()

    def process_relation(self, relations):
        if TRUE(self.outcome):
            target = get_rel_by_name(relations, self.rel_name, add_rels=True)
            if self.rel_name in commute:
                pairs = (pair_sort(self.a, self.b))
            else:
                pairs = (self.a, self.b)
            target.add(pairs)
            # to register
            local_target = get_rel_by_name(TestCase.TestCase_connection, self.rel_name, add_rels=True, is_dict=True)
            local_target[pairs] = self
        elif FALSE(self.outcome):
            if self.rel_name in commute:
                pairs = (pair_sort(self.a, self.b))
            else:
                pairs = (self.a, self.b)
            target = get_rel_by_name(relations, get_neg_name(self.rel_name), add_rels=True)
            target.add(pairs)
        else:
            assert False


def get_all_relations(relations, old_relations = None):
    if old_relations is not None:
        return get_delta(get_all_relations(relations, None), get_all_relations(old_relations, None))
    else:
        delta = relations

    results = []
    for k in delta:
        if k in all_relations:
            pairs = delta[k]
            if pairs:
                test_pairs = TestCase.TestCase_connection[k]
                for pair in pairs:
                    results.append(test_pairs[pair].to_json())
    return results


def get_all_relations_str(relations):
    result = get_all_relations(relations)
    return ',\n'.join([str(r) for r in result])


def is_witness(relations, rc):
    if WITNESS in rc:
        result = TestCase(WITNESS, rc["event1"], rc["event2"], outcome=rc[WITNESS], justification=rc[JUSTIFICATION])
        result.process_relation(relations)
        return True
    else:
        return False


def is_conflict(relations, rc):
    if CONFLICTS in rc:
        result = TestCase(CONFLICTS, rc["event1"], rc["event2"], outcome=rc[CONFLICTS],
                          justification=rc[JUSTIFICATION])
        result.process_relation(relations)
        return True
    else:
        return False


def is_HB(relations, rc):
    if HB in rc:
        result = TestCase(HB, rc["event1"], rc["event2"], outcome=rc[HB], justification=rc[JUSTIFICATION])
        result.process_relation(relations)
        return True
    else:
        return False


def is_implies(relations, rc):
    if IMPLIES in rc:
        result = TestCase(IMPLIES, rc["measure1"], rc["measure2"], outcome=rc[IMPLIES], justification=rc[JUSTIFICATION])
        result.process_relation(relations)
        return True
    else:
        return False


def is_equals(relations, rc):
    if EQ in rc:
        result = TestCase(EQ, rc["measure1"], rc["measure2"], outcome=rc[EQ], justification=rc[JUSTIFICATION])
        result.process_relation(relations)
        return True
    else:
        return False


def is_ME(relations, rc):
    if ME in rc:
        result = TestCase(ME, rc["measure1"], rc["measure2"], outcome=rc[ME], justification=rc[JUSTIFICATION])
        result.process_relation(relations)
        return True
    else:
        return False


def build_relations(relations):
    new_relations = {}
    for r in relations:
        rc = r["Relationship"]
        if is_witness(new_relations, rc) or is_conflict(new_relations, rc) or is_HB(new_relations, rc) or is_implies(
                new_relations, rc) or is_equals(new_relations, rc) or is_ME(new_relations, rc):
            continue
        else:
            print("invalid relation {}".format(rc))

    return new_relations


def make_cononical(partial_rel, new_partial_rel, commute=False):
    for (a, b) in partial_rel:
        if commute:
            lhs = min(a, b)
            rhs = max(a, b)
            new_partial_rel.add((lhs, rhs))
        else:
            new_partial_rel.add((a, b))


def canonical(relations):
    for rel in all_relations:
        true_relations = get_rel_by_name(relations, rel)
        new_true_relations = set()
        make_cononical(true_relations, new_true_relations, commute=rel in commute)

        false_relations = get_rel_by_name(relations, get_neg_name(rel))
        new_false_relations = set()
        make_cononical(false_relations, new_false_relations, commute=rel in commute)


def is_true(rel):
    return rel == 1


def is_false(rel):
    return rel == -1


def is_unknown(rel):
    return rel == 0


def get_neg_name(name):
    return "not {}".format(name)


def get_rel_by_name(relations, rel_name, add_rels=False, is_dict=False):
    if rel_name in relations:
        return relations[rel_name]
    else:
        if is_dict:
            target_rel = {}
        else:
            target_rel = set()
        if add_rels:
            relations[rel_name] = target_rel
        return target_rel


def check_trivial_case(a, b, rel):
    if rel == WITNESS:
        if a == b:
            return 1
    if rel == CONFLICTS:
        if a == b:
            return -1

    if rel == HB:
        if a == b:
            return -1

    if rel == IMPLIES:
        if a == b:
            return 1

    if rel == ME:
        if a == b:
            return -1

    if rel == EQ:
        if a == b:
            return 1

    return 0


def check_rel(a, b, rel, relations, commute=False):
    trivial_result = check_trivial_case(a, b, rel)
    if is_true(trivial_result) or is_false(trivial_result):
        return trivial_result
    true_target_rel = get_rel_by_name(relations, rel)
    false_target_rel = get_rel_by_name(relations, get_neg_name(rel))
    if commute:
        if (a, b) in true_target_rel or (b, a) in true_target_rel:
            return 1
        elif (a, b) in false_target_rel or (b, a) in false_target_rel:
            return -1
        else:
            return 0
    else:
        if (a, b) in true_target_rel:
            return 1
        elif (a, b) in false_target_rel:
            return -1
        else:
            return 0


### A relationship cannot hold both true and false at the same time"
def check_consistent(relations):
    new_true_rel = set()
    for rel in all_relations:
        changed = False
        does_commute = rel in commute
        true_target_rel = get_rel_by_name(relations, rel)
        false_target_rel = get_rel_by_name(relations, get_neg_name(rel))
        for (a, b) in true_target_rel:
            if (a, b) in false_target_rel:
                print("inconsistent {} {} {}".format(a, rel, b))
                changed = True
            else:
                new_true_rel.add((a, b))

            if does_commute:
                if (b, a) in false_target_rel:
                    print("inconsistent {} {} {}".format(b, rel, a))
                    changed = True
                else:
                    new_true_rel.add((a, b))

        relations[rel] = new_true_rel
        return changed


### Relation between witnes and conflicts

### If A witness B, then A not conflict with B" ####
def check_rule1(relations, test_cases):
    changed = False
    witness = get_rel_by_name(relations, WITNESS)
    neg_witness = get_rel_by_name(relations, get_neg_name(WITNESS), add_rels=True)
    new_witness = set()
    for (a, b) in witness:
        result = check_rel(a, b, CONFLICTS, relations, True)
        if is_true(result):
            changed = True
            # TODO we favor conflict over witness
            print("inconsistent {} {} {}".format(a, WITNESS, b))
            neg_witness.add((a, b))
        elif is_unknown(result):
            test_cases.add(TestCase(CONFLICTS, a, b))
            new_witness.add((a, b))
        else:
            new_witness.add((a, b))

    relations[WITNESS] = new_witness
    return changed


### if A witness B, and B conflict with C, then A conflicts with C
def check_rule2(relations, test_cases):
    new_witness = set()
    changed = False
    witness = get_rel_by_name(relations, WITNESS)
    conflicts = get_rel_by_name(relations, CONFLICTS)
    neg_witness = get_rel_by_name(relations, get_neg_name(WITNESS), add_rels=True)
    for (a, b) in witness:
        matched = False
        for (c, d) in conflicts:
            if b == c:
                other = d
            elif b == d:
                other = c
            else:
                continue
            matched = True
            result = check_rel(a, other, CONFLICTS, relations, True)
            if is_true(result):
                # TODO we favor conflict over witness
                new_witness.add((a, b))
            elif is_unknown(result):
                test_cases.add(TestCase(CONFLICTS, a, other))
                new_witness.add((a, b))
            else:
                neg_witness.add((a, b))
                print("inconsistent {} {} {}".format(a, WITNESS, b))
                changed = True
                break
        if not matched:
            new_witness.add((a, b))

    relations[WITNESS] = new_witness
    return changed


### if A witness B, and B witness with C, then A witness with C
def check_rule3(relations, test_cases):
    changed = False
    new_witness = set()
    witness = get_rel_by_name(relations, WITNESS)
    neg_witness = get_rel_by_name(relations, get_neg_name(WITNESS), add_rels=True)
    for (a, b) in witness:
        matched = False
        for (c, d) in witness:
            if b == c:
                matched = True
                result = check_rel(a, d, WITNESS, relations, False)
                if is_true(result):
                    new_witness.add((a, b))
                elif is_unknown(result):
                    new_witness.add((a, b))
                    test_cases.add(TestCase(WITNESS, a, d))
                else:
                    changed = True
                    neg_witness.add((a, b))
                    print("inconsistent {} {} {}".format(a, WITNESS, b))
                    break
        if not matched:
            new_witness.add((a, b))

    relations[WITNESS] = new_witness
    return changed


### if A HB B, then B not B HB A
def check_rule5(relations, test_cases):
    changed = False
    new_HB = set()
    HBs = get_rel_by_name(relations, HB)
    neg_HBs = get_rel_by_name(relations, get_neg_name(HB), add_rels=True)
    for (a, b) in HBs:
        if (b, a) in HBs:
            changed = True
            print("inconsistent {} {} {}".format(a, HB, b))
            neg_HBs.add((a, b))
        else:
            new_HB.add((a, b))

    relations[HB] = new_HB
    return changed


### if A HB B, and A witness C, then C HB B ###
def check_rule6(relations, test_cases):
    changed = False
    new_HB = set()
    HBs = get_rel_by_name(relations, HB)
    neg_HBs = get_rel_by_name(relations, get_neg_name(HB), add_rels=True)
    witness = get_rel_by_name(relations, WITNESS)
    for (a, b) in HBs:
        matched = False
        for (c, d) in witness:
            if a == c:
                matched = True
                result = check_rel(a, d, HB, relations)
                if is_true(result):
                    new_HB.add((a, b))
                elif is_false(result):
                    changed = True
                    neg_HBs.add((a, b))
                    print("inconsistent {} {} {}".format(a, HB, b))
                    break
                else:
                    new_HB.add((a, b))
                    test_cases.add(TestCase(HB, a, d))
        if not matched:
            new_HB.add((a, b))

    relations[HB] = new_HB
    return changed


### if A HB B and B HB C, then A HB C ###
def check_rule7(relations, test_cases):
    changed = False
    new_HB = set()
    HBs = get_rel_by_name(relations, HB)
    neg_HBs = get_rel_by_name(relations, get_neg_name(HB), add_rels=True)
    for (a, b) in HBs:
        matched = False
        for (c, d) in HBs:
            if b == c:
                matched = True
                result = check_rel(a, d, HB, relations)
                if is_true(result):
                    new_HB.add((a, b))
                elif is_false(result):
                    changed = True
                    neg_HBs.add((a, b))
                    print("inconsistent {} {} {}".format(a, HB, b))
                    break
                else:
                    new_HB.add((a, b))
                    test_cases.add(TestCase(HB, a, d))

        if not matched:
            new_HB.add((a, b))

    relations[HB] = new_HB
    return changed


### If A implies B, then A not ME with B" ####
def check_rule8(relations, test_cases):
    changed = False
    implies = get_rel_by_name(relations, IMPLIES)
    neg_implies = get_rel_by_name(relations, get_neg_name(IMPLIES), add_rels=True)
    new_implies = set()
    for (a, b) in implies:
        result = check_rel(a, b, ME, relations, True)
        if is_true(result):
            changed = True
            # TODO we favor ME over implies
            print("inconsistent {} {} {}".format(a, IMPLIES, b))
            neg_implies.add((a, b))
        else:
            new_implies.add((a, b))

    relations[IMPLIES] = new_implies
    return changed


### if A implies B, and B ME with C, then A ME with C
def check_rule9(relations, test_cases):
    new_implies = set()
    changed = False
    implies = get_rel_by_name(relations, IMPLIES)
    me = get_rel_by_name(relations, ME)
    neg_implies = get_rel_by_name(relations, get_neg_name(IMPLIES), add_rels=True)

    for (a, b) in implies:
        matched = False
        for (c, d) in me:
            if b == c:
                other = d
            elif b == d:
                other = c
            else:
                continue
            matched = True
            result = check_rel(a, other, ME, relations, True)
            if is_true(result):
                # TODO we favor ME over implies
                new_implies.add((a, b))
            elif is_unknown(result):
                test_cases.add(TestCase(ME, a, other))
                new_implies.add((a, b))
            else:
                neg_implies.add((a, b))
                print("inconsistent {} {} {}".format(a, IMPLIES, b))
                changed = True
                break
        if not matched:
            new_implies.add((a, b))
    relations[IMPLIES] = new_implies
    return changed


### if A implies B, and B implies with C, then A implies with C
def check_rule10(relations, test_cases):
    changed = False
    new_implies = set()
    implies = get_rel_by_name(relations, IMPLIES)
    neg_implies = get_rel_by_name(relations, get_neg_name(IMPLIES), add_rels=True)
    for (a, b) in implies:
        matched = False
        for (c, d) in implies:
            if b == c:
                matched = True
                result = check_rel(a, d, IMPLIES, relations, False)
                if is_true(result):
                    new_implies.add((a, b))
                elif is_unknown(result):
                    new_implies.add((a, b))
                    test_cases.add(TestCase(IMPLIES, a, d))
                else:
                    changed = True
                    neg_implies.add((a, b))
                    print("inconsistent {} {} {}".format(a, IMPLIES, b))
                    break

        if not matched:
            new_implies.add((a, b))

    relations[IMPLIES] = new_implies
    return changed


### if A EQ B, then A implies B and B implies A ###
def check_rule11(relations, test_cases):
    changed = False
    new_EQs = set()
    EQs = get_rel_by_name(relations, EQ)
    neg_EQs = get_rel_by_name(relations, get_neg_name(EQ), add_rels=True)
    for (a, b) in EQs:
        result1 = check_rel(a, b, IMPLIES, relations, False)
        result2 = check_rel(b, a, IMPLIES, relations, False)

        if is_true(result1) and is_true(result2):
            new_EQs.add((a, b))
        elif is_false(result1) or is_false(result2):
            changed = True
            neg_EQs.add((a, b))
            print("inconsistent {} {} {}".format(a, EQ, b))
            break
        else:
            new_EQs.add((a, b))
            if is_unknown(result1):
                test_cases.add(TestCase(IMPLIES, a, b))
            if is_unknown(result2):
                test_cases.add(TestCase(IMPLIES, b, a))

    relations[EQ] = new_EQs
    return changed


def _check_rules(relations, test_cases):
    changed = check_consistent(relations)
    changed = changed or check_rule1(relations, test_cases)
    changed = changed or check_rule2(relations, test_cases)
    changed = changed or check_rule3(relations, test_cases)
    changed = changed or check_rule5(relations, test_cases)
    changed = changed or check_rule6(relations, test_cases)
    changed = changed or check_rule7(relations, test_cases)
    changed = changed or check_rule8(relations, test_cases)
    changed = changed or check_rule9(relations, test_cases)
    changed = changed or check_rule10(relations, test_cases)
    changed = changed or check_rule11(relations, test_cases)
    check_consistent(relations)
    return changed


def check_rules(relations):
    test_cases = set()
    canonical(relations)

    old_test_case = len(test_cases)
    changed = _check_rules(relations, test_cases)

    while len(test_cases) > old_test_case or changed:
        old_test_case = len(test_cases)
        changed = _check_rules(relations, test_cases)

    return test_cases


def parse_and_process(relations):
    new_relations = build_relations(relations)
    test_cases = check_rules(new_relations)
    return new_relations, test_cases


def merge(a, b):
    assert type(a) == type(b)
    if isinstance(b, dict):
        for k in b:
            if k in a:
                a[k] = merge(a[k], b[k])
            else:
                a[k] = b[k]
        return a
    elif isinstance(b, set):
        return a.union(b)


def parse_and_refine(relations, new_relations_json):
    new_relations = build_relations(new_relations_json)
    merged_relations = merge(relations, new_relations)
    test_cases = check_rules(merged_relations)
    return merged_relations, test_cases

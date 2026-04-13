"""Quick smoke test for sanitize_question — run inside backend container."""
import json
from data_pipeline.json_utils import sanitize_question

q1 = json.loads(r'''{"question_text":"test","options":{"A":"$h = \\\\frac{1}{2}H$","B":"$h = \\\\frac{1}{3}H$"},"correct_answer":"B"}''')
print("Q12 before:", repr(q1["options"]["A"]))
r1 = sanitize_question(q1)
print("Q12 after :", repr(r1["options"]["A"]))
assert r1["options"]["A"] == "$h = \\frac{1}{2}H$", "Q12 overescape not fixed"

q2 = {"question_text":"test","options":{"A":"0,5","B":"1","C":"0,25","E":"0,75","0,125":"D"},"correct_answer":"C"}
r2 = sanitize_question(q2)
print("Q3 keys  :", sorted(r2["options"].keys()))
print("Q3 D val :", r2["options"].get("D"))
assert sorted(r2["options"].keys()) == ["A", "B", "C", "D", "E"], "Q3 swap not repaired"
assert r2["options"]["D"] == "0,125", "Q3 D value wrong"

q3 = {"question_text":"test","options":{"A":"\\text{ m}^2","B":"1","C":"2","D":"3","E":"4"},"correct_answer":"A"}
r3 = sanitize_question(q3)
print("Bare lx  :", repr(r3["options"]["A"]))
assert r3["options"]["A"].startswith("$") and r3["options"]["A"].endswith("$"), "Bare latex not wrapped"

print("ALL PASS")
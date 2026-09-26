# Mock Exam 1 sample solution

This is one valid implementation, not the only correct answer. To build a
review workspace without changing the original starter:

```bash
cp -a practice/mock-exam-1/starter /tmp/mock-exam-1-solution
cp -a practice/_solutions/mock-exam-1/solution/. /tmp/mock-exam-1-solution/
cd /tmp/mock-exam-1-solution
ansible-playbook data_transform.yml
ansible-playbook delegation.yml
python3 /path/to/practice/mock-exam-1/grade.py .
```

From the Git-compatible lab kit, use the equivalent paths:

```bash
cp -a labs/mock-exam-1/starter /tmp/mock-exam-1-solution
cp -a solutions/mock-exam-1/solution/. /tmp/mock-exam-1-solution/
cd /tmp/mock-exam-1-solution
```

The delegation play creates its reports under `/tmp/mock-exam-reports` on the
control node. Those generated files are intentionally not stored here.

# Mock Exam 2 sample solution

This overlay demonstrates one safe structure for the rolling deployment. Build
a separate review workspace with:

```bash
cp -a practice/mock-exam-2/starter /tmp/mock-exam-2-solution
cp -a practice/_solutions/mock-exam-2/solution/. /tmp/mock-exam-2-solution/
chmod 0755 /tmp/mock-exam-2-solution/inventory/platform_inventory.py
cd /tmp/mock-exam-2-solution
./inventory/platform_inventory.py --list
./inventory/platform_inventory.py --host smoke_runner
ansible-inventory --graph
ansible-inventory --list
cd -
python3 practice/mock-exam-2/grade.py /tmp/mock-exam-2-solution
```

From the Git-compatible lab kit, replace `practice/mock-exam-2` with
`labs/mock-exam-2` and `practice/_solutions` with `solutions`.

The grader executes only the supplied inventory script locally; it makes no
managed-host or network calls. Review the block/rescue/always sequence before
running the deployment against disposable managed hosts.

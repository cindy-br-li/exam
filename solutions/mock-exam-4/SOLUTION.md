# Mock Exam 4 sample solution

Copy the solution overlay onto a fresh starter, then create the Git history:

```bash
cp -a practice/mock-exam-4/starter /tmp/mock-exam-4-solution
cp -a practice/_solutions/mock-exam-4/solution/. /tmp/mock-exam-4-solution/
cd /tmp/mock-exam-4-solution
git init
git config user.name 'Student User'
git config user.email student@lab.example.com
git add . && git commit -m 'Configure project and inventory'
git switch -c feature/branch-access
git commit --allow-empty -m 'Complete account management playbook'
```

Run `python grade.py` from the parent mock-exam directory after placing the
merged workspace at `starter/`.

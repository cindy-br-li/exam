# Mock Exam 3 sample solution

This overlay migrates the supplied role into `northstar.content_supply`, completes collection metadata and dependencies, builds and installs the collection locally, consumes the role by FQCN, and defines a schema-v3 custom execution environment.

```bash
cp -a practice/mock-exam-3/starter /tmp/mock-exam-3-solution
cp -a practice/_solutions/mock-exam-3/solution/. /tmp/mock-exam-3-solution/
chmod 0755 /tmp/mock-exam-3-solution/build_install.sh
python3 practice/mock-exam-3/grade.py /tmp/mock-exam-3-solution
```

The solution intentionally contains no custom module or filter. Its EE notes cover `ansible-builder create`, tagged build, generated-context inspection, image facts, and runtime role validation. Commands unavailable offline are explicitly marked as not run.

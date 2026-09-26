# EX374 Mock Exam Lab

This repository contains four solution-free mock exams for a Red Hat training
workstation. It does not alter Red Hat's native `lab` command or course state.
See [COVERAGE.md](COVERAGE.md) for the AU374 practical-skills mapping.

## Install

```bash
git clone <your-repository-url> ex374-lab-kit
cd ex374-lab-kit
chmod +x install.sh
./install.sh
```

## Run and mark the exam

```bash
exlab start mock-exam-1
cd ~/ex374-work/mock-exam-1
cat TASK.md

exlab grade
exlab status
exlab finish
```

Choose `mock-exam-1` through `mock-exam-4`. Each automatic grader awards
partial credit out of 100. The pass mark is 70.

For the next two exams specifically:

```bash
exlab finish mock-exam-1       # finish the active exam first, if applicable
exlab start mock-exam-2
cd ~/ex374-work/mock-exam-2

# Later, after finishing Mock Exam 2:
exlab finish mock-exam-2
exlab start mock-exam-3
cd ~/ex374-work/mock-exam-3
```

The installer restores executable permissions for supplied shell and Python
scripts, so dynamic inventory and collection build scripts work after cloning
the repository on the RHEL workstation.

## Sample solutions

Reference solution overlays for all four mock exams are stored separately
under `solutions/`. They are not copied into `~/ex374-work` by `exlab start`.
After completing an exam, review its explanation and files with:

```bash
exlab solution mock-exam-1

# Or directly from the cloned repository:
less solutions/mock-exam-1/SOLUTION.md
find solutions/mock-exam-1/solution -type f -print
```

Each `SOLUTION.md` explains how to combine the untouched starter with the
solution overlay in a temporary directory for comparison and grading.

## Reset

```bash
exlab reset mock-exam-1
```

Reset asks for confirmation, deletes all work in
`~/ex374-work/mock-exam-1`, and regenerates the original starter files.

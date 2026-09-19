# EX374 Mock Exam Lab

This repository contains one solution-free mock exam for a Red Hat training
workstation. It does not alter Red Hat's native `lab` command or course state.

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

The automatic grader awards partial credit out of 100. The pass mark is 70.

## Reset

```bash
exlab reset mock-exam-1
```

Reset asks for confirmation, deletes all work in
`~/ex374-work/mock-exam-1`, and regenerates the original starter files.

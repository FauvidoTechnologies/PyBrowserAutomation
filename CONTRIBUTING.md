# Contributing Guidelines

Thank for taking the time to contribute to the project! This is how you can easily get started:

1. **Understand the code**

This part is easiest if you simply use it. `pyba` is a browser automation tool for OSINT. Run it for data extraction scenarios (for help on running it, check out `.\automation_eval` or the `usage` section from the [docs](https://pyba.readthedocs.io)) and see if it works as you expected it to.

2. **Raise issues**

This allows everyone else to know that certain issues have already been found and are being worked upon.

3. **Fork the repo**

Create your own copy of the repo. It is recommended you keep it public (though not enforced by a license)

4. **Make changes to a new branch**

Ensure that any changes you make are to a new branch you created.

5. **Pre-commit**

Before you make a PR, ensure that you tun pre-commit on your code to format it with the latest pep8 guidelines. To do this you will need to have pre-commit installed:

```sh
pip install pre-commit
# After installation, go to the root directory of your fork
git add .
make pre-commit
```

Ensure that you run it enough times such that it doesn't make any more changes. Then add and commit again.

6. **Make a Pull Request**

We're following the standard way of contributions. Once you have your changes make a pull request.

> [!NOTE]
> We unfortunately don't have any tests yet. This is an area we need work on. So, your PRs will be manually tested by the maintainers

# Good Luck!